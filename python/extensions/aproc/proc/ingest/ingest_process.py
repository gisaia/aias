import json
import os

import requests
from celery import shared_task
from pydantic import BaseModel, Field

from airs.core.models.mapper import item_from_json, to_json
from airs.core.models.model import Asset, Item, Properties
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.execute import Execute
from aproc.core.processes.process import Process as Process, Subscriber as OGCSubscriber
from aproc.core.settings import Configuration
from aproc.core.utils import add_msg_to_text, base_model2description
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.drivers.exceptions import (ConnectionException,
                                                      DriverException,
                                                      RegisterException)
from extensions.aproc.proc.enrich.enrich_process import InputEnrichProcess
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.ingest.settings import \
    Configuration as IngestConfiguration
from extensions.aproc.proc.processes.arlas_services_helper import (
    JSON_HEADER, ARLASServicesHelper)
from extensions.aproc.proc.processes.process_model import InputProcess, OutputProcess

AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")
DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.get_logger()


class InputIngestProcess(InputProcess):
    collection: str = Field(title="Collection name", description="Name of the collection where the item will be registered")
    catalog: str = Field(title="Catalog name", description="Name of the catalog, within the collection, where the item will be registered")
    url: str = Field(title="Archive URL", description="URL pointing at the archive")
    annotations: str = Field(title="Item annotations", description="Item annotations")
    enrichments: list[str] = Field(default=[], title="Enrichments", description="List of enrichments to apply on the item")


class OutputIngestProcess(OutputProcess):
    item_location: str = Field(title="Item location", description="Location of the Item on the ARLAS Item Registration Service")
    archive_url: str = Field(title="Archive location", description="Initial location of the ingested archive")
    collection: str = Field(title="Target collection", description="Collection that contains the item")
    catalog: str = Field(title="Target catalog", description="Catalog that contains the item")


summary: ProcessSummary = ProcessSummary(
    title="Ingest an archive in AIRS.",
    description="Extract the item and assets information from an archive and register the item and assets in ARLAS Item Registration Services.",
    keywords=["AIRS", "ARLAS Item Registration Services"],
    id="ingest",
    version=AIAS_VERSION,
    jobControlOptions=[JobControlOptions.async_execute],
    outputTransmission=[TransmissionMode.reference],
    # TODO: provide the links if any => link could be the execute endpoint
    links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(exclude_none=True, exclude_unset=True),
    inputs=base_model2description(InputIngestProcess),
    outputs=base_model2description(OutputIngestProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            IngestConfiguration.init(configuration_file=configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME))
            IngestConfiguration.raise_if_not_valid()
            DriverManager.init(summary.id, IngestConfiguration.settings.drivers)
        else:
            raise DriverException("Invalid configuration for ingest drivers ({})".format(configuration))
        AprocProcess.input_model = InputIngestProcess
        description.inputs.get("include_drivers").schema_.items.enum = DriverManager.driver_names(summary.id)
        description.inputs.get("exclude_drivers").schema_.items.enum = DriverManager.driver_names(summary.id)

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    @staticmethod
    def get_resource_id(inputs: BaseModel) -> str:
        url = InputIngestProcess(**inputs.model_dump(exclude_none=True, exclude_unset=True)).url
        driver: IngestDriver = DriverManager.solve(summary.id, url)
        if driver is not None:
            return driver.get_item_id(url)
        raise DriverException("No driver found for  {}".format(url))

    @shared_task(bind=True, track_started=True)
    def execute(self, headers: dict[str, str], subscriber: dict[str, str], url: str, collection: str, catalog: str, annotations: str, include_drivers: list[str] = [], exclude_drivers: list[str] = [], enrichments: list[str] = [], cascade_subscriber: bool = False) -> dict:
        # self is a celery task because bind=True
        """ ingest the archive url in 6 step:
        - identify the driver for ingestion
        - identify the assets to fetch
        - fetch the assets (e.g. copy/download)
        - transform the assets if necessary (e.g. create cog)
        - upload the assets
        - register the item

        Args:
            url (str): archive url
            collection (str): target collection
            catalog (str): target catalog

        Returns:
            object: an dict pointing towards the registered item (OutputIngestProcess)
        """
        if not url.startswith(IngestConfiguration.settings.inputs_directory):
            msg = "Can not ingest directory {} : it is not prefixed with {}".format(url, IngestConfiguration.settings.inputs_directory)
            LOGGER.error(msg)
            raise Exception(msg)

        if not AccessManager.exists(url):
            msg = "File or directory {} not found in configured storages".format(url)
            LOGGER.error(msg)
            raise DriverException(msg)

        driver: IngestDriver = DriverManager.solve(summary.id, url, include_drivers=include_drivers, exclude_drivers=exclude_drivers)
        if driver is not None:
            try:
                message = ""
                error = ""
                LOGGER.info("Driver {} will be used".format(driver.name))
                LOGGER.debug("ingestion: 1 - identify_assets")
                Process.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'identify_assets', "ACTION": "INGEST", "TARGET": url})
                assets: list[Asset] = driver.identify_assets(url)
                AprocProcess.__check_assets__(url, assets)

                LOGGER.debug("ingestion: 2 - fetch_assets")
                Process.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'fetch_assets', "ACTION": "INGEST", "TARGET": url})
                try:
                    assets = driver.fetch_assets(url, assets)
                except Exception as e:
                    msg = "Fetching assets failed for connection reasons ({})".format(e.response)
                    LOGGER.error(msg)
                    raise ConnectionException(msg)
                AprocProcess.__check_assets__(url, assets, file_exists=True)

                LOGGER.debug("ingestion: 3 - transform_assets")
                Process.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'transform_assets', "ACTION": "INGEST", "TARGET": url})
                assets = driver.transform_assets(url, assets)
                AprocProcess.__check_assets__(url, assets, file_exists=True)

                LOGGER.debug("ingestion: 4 - create_item")
                Process.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'create_item', "ACTION": "INGEST", "TARGET": url})
                item = driver.to_item(url, assets)
                item.collection = collection
                item.catalog = catalog
                if not item.properties:
                    item.properties = Properties()
                item.properties.annotations = annotations
                LOGGER.debug("ingestion: 5 - upload")
                i: int = 0
                for asset_name, asset in item.assets.items():
                    Process.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'upload_asset', 'current': i, 'asset': asset_name, 'total': len(item.assets), "ACTION": "INGEST", "TARGET": url})
                    i += 1
                    asset: Asset = asset
                    ARLASServicesHelper.upload_asset_if_managed(item, asset, Configuration.settings.airs_endpoint)
                LOGGER.debug("ingestion: 6 - register")
                Process.update_task_status(LOGGER, self, state='PROGRESS', meta={'step': 'register_item', "ACTION": "INGEST", "TARGET": url})
                item: Item = ARLASServicesHelper.insert_or_update_item(item, Configuration.settings.airs_endpoint)
                sub_jobs: list[str] = []
                if enrichments:
                    try:
                        inputs: InputEnrichProcess = InputEnrichProcess(requests=[{"collection": item.collection, "item_id": item.id}], enrichments=enrichments, cascade_subscriber=cascade_subscriber)
                        execute = Execute(inputs=inputs.model_dump(exclude_none=True, exclude_unset=True), subscriber=OGCSubscriber(**subscriber) if cascade_subscriber else None)
                        r: requests.Response = requests.post("/".join([IngestConfiguration.settings.aproc_endpoint, "processes", "enrich", "execution"]), data=json.dumps(execute.model_dump()), headers=headers)
                        if not r.ok:
                            msg = "Failed to submit the enrich request for {} ({}): {}".format(url, item.id, str(r.status_code) + ":" + str(r.content))
                            LOGGER.error(msg)
                            error = add_msg_to_text(msg, error)
                        else:
                            sub_jobs.append(json.loads(r.content).get("jobID"))
                            msg = "Send enrichment request for {} ({}) ok".format(url, item.id)
                            LOGGER.debug("Send ingestion request for {} ({}) ok".format(url, item.id))
                            message = add_msg_to_text(msg, message)
                    except Exception as err:
                        msg = "Exception while requesting enrichment {} with {}: {}".format(url, enrichments, str(err))
                        error = add_msg_to_text(msg, error)
                        LOGGER.error(msg)
                        LOGGER.exception(err)
                return OutputIngestProcess(process="ingest", collection=collection, catalog=catalog, archive_url=url, item_location=os.path.join(Configuration.settings.airs_endpoint, "collections", item.collection, "items", item.id), sub_jobs=sub_jobs, message=message, error=error).model_dump(exclude_none=True, exclude_unset=True)
            except Exception as err:
                msg = "Exception while ingesting {}: {}".format(url, str(err))
                LOGGER.error(msg)
                LOGGER.exception(err)
                raise DriverException(msg)
        else:
            LOGGER.error("No driver found for {}".format(url))
            raise DriverException("No driver found for  {}".format(url))

    @staticmethod
    def __check_assets__(url: str, assets: list[Asset], file_exists: bool = False):
        for asset in assets:
            if asset.name is None:
                raise DriverException("Invalid asset for {} : no name provided".format(url))
            if asset.href is None:
                raise DriverException("Invalid asset {} for {} : no href provided".format(asset.name, url))
            if asset.roles is None:
                raise DriverException("Invalid asset {} for {} : no roles provided".format(asset.name, url))
            if file_exists:
                if asset.airs__managed is True and not AccessManager.exists(asset.href):
                    raise DriverException("Invalid asset {} for {} : file {} not found".format(asset.name, url, asset.href))

    @staticmethod
    def insert_or_update_item(item: Item, airs_endpoint) -> Item:
        item_already_exists = False
        try:
            r = requests.get(url="/".join([airs_endpoint, "collections", item.collection, "items", item.id]), headers=JSON_HEADER)
            if r.ok:
                LOGGER.debug("Item {}/{} already exists: triggers update".format(item.collection, item.id))
                item_already_exists = True
            else:
                LOGGER.debug("Item {}/{} does not yes exist: triggers insert".format(item.collection, item.id))
        except requests.exceptions.ConnectionError:
            msg = "AIRS Service can not be reached ({})".format(airs_endpoint)
            LOGGER.error(msg)
            raise ConnectionException(msg)
        try:
            if item_already_exists:
                LOGGER.debug("update item {}/{} ...".format(item.collection, item.id))
                r = requests.put(url="/".join([airs_endpoint, "collections", item.collection, "items", item.id]), data=to_json(item), headers=JSON_HEADER)
            else:
                LOGGER.debug("Insert item {}/{} ...".format(item.collection, item.id))
                r = requests.post(url="/".join([airs_endpoint, "collections", item.collection, "items"]), data=to_json(item), headers=JSON_HEADER)
            if r.ok:
                LOGGER.debug("upsert done for item {}/{} ...".format(item.collection, item.id))
                return item_from_json(r.content)
            else:
                LOGGER.error("Item has not been registered: {} - {}".format(r.status_code, r.content))
                LOGGER.error(to_json(item))
                raise RegisterException("Item has not been registered: {} - {}".format(r.status_code, r.content))
        except requests.exceptions.ConnectionError:
            msg = "AIRS Service can not be reached ({})".format(airs_endpoint)
            LOGGER.error(msg)
            raise ConnectionException(msg)
