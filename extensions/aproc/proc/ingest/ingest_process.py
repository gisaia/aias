import hashlib
import os

import requests
from celery import shared_task, Task
from pydantic import BaseModel, Field

from airs.core.models.mapper import item_from_json, to_json
from airs.core.models.model import Asset
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.job import StatusInfo
from aproc.core.processes.process import Process as Process
from aproc.core.settings import Configuration
from aproc.core.utils import base_model2description
from extensions.aproc.proc.ingest.drivers.drivers import Drivers
from extensions.aproc.proc.ingest.drivers.exceptions import (
    ConnectionException, DriverException, RegisterException)

DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


def __update_status__(task: Task, state: str, meta: dict = None):
    LOGGER.info(task.name+" "+state+" "+str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)


class InputIngestProcess(BaseModel):
    collection: str = Field(title="Collection name", description="Name of the collection where the item will be registered", minOccurs=1, maxOccurs=1)
    catalog: str = Field(title="Catalog name", description="Name of the catalog, within the collection, where the item will be registered", minOccurs=1, maxOccurs=1)
    url: str = Field(title="Archive URL", description="URL pointing at the archive", minOccurs=1, maxOccurs=1)


class OutputIngestProcess(BaseModel):
    item_location: str = Field(title="Item location", description="Location of the Item on the ARLAS Item Registration Service")


summary: ProcessSummary = ProcessSummary(
            title="Ingest an archive in AIRS.",
            description="Extract the item and assets information from an archive and register the item and assets in ARLAS Item Registration Services.",
            keywords=["AIRS", "ARLAS Item Registration Services"],
            id="ingest",
            version="0.1",
            jobControlOptions=[JobControlOptions.async_execute],
            outputTransmission=[TransmissionMode.reference],
            # TODO: provide the links if any => link could be the execute endpoint
            links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(),
    inputs=base_model2description(InputIngestProcess),
    outputs=base_model2description(OutputIngestProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            Drivers.init(configuration_file=configuration[DRIVERS_CONFIGURATION_FILE_PARAM_NAME])
        else:
            raise DriverException("Invalid configuration for ingest drivers ({})".format(configuration))
        AprocProcess.input_model = InputIngestProcess

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    def get_resource_id(inputs: BaseModel):
        hash_object = hashlib.sha1(InputIngestProcess(**inputs.model_dump()).url.encode())
        return hash_object.hexdigest()

    @shared_task(bind=True)
    def execute(self, headers: dict[str, str], url: str, collection: str, catalog: str) -> dict:
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
            driver_name (str): driver name
            collection (str): target collection
            catalog (str): target catalog

        Returns:
            object: an dict pointing towards the registered item (OutputIngestProcess)
        """

        driver = Drivers.solve(url)
        if driver is not None:
            LOGGER.debug("ingestion: 1 - identify_assets")
            __update_status__(self, state='PROGRESS', meta={'step':'identify_assets', "ACTION": "INGEST", "TARGET": url})
            assets: list[Asset] = driver.identify_assets(url)
            AprocProcess.__check_assets__(url, assets)

            LOGGER.debug("ingestion: 2 - fetch_assets")
            __update_status__(self, state='PROGRESS', meta={'step':'fetch_assets', "ACTION": "INGEST", "TARGET": url})
            try:
                assets = driver.fetch_assets(url, assets)
            except requests.exceptions.ConnectionError as e:
                msg = "Fetching assets failed for connection reasons ({})".format(e.response)
                LOGGER.error(msg)
                raise ConnectionException(msg)
            AprocProcess.__check_assets__(url, assets, file_exists=True)

            LOGGER.debug("ingestion: 3 - transform_assets")
            __update_status__(self, state='PROGRESS', meta={'step':'transform_assets', "ACTION": "INGEST", "TARGET": url})
            assets = driver.transform_assets(url, assets)
            AprocProcess.__check_assets__(url, assets, file_exists=True)

            LOGGER.debug("ingestion: 4 - create_item")
            __update_status__(self, state='PROGRESS', meta={'step':'create_item', "ACTION": "INGEST", "TARGET": url})
            item = driver.to_item(url, assets)
            item.collection = collection
            item.catalog = catalog
            LOGGER.debug("ingestion: 5 - upload")
            i: int = 0
            for asset_name, asset in item.assets.items():
                __update_status__(self, state='PROGRESS', meta={'step': 'upload', 'current': i, 'asset': asset_name, 'total': len(item.assets), "ACTION": "INGEST", "TARGET": url})
                i += 1
                asset: Asset = asset
                if asset.airs__managed is True:
                    with open(asset.href, 'rb') as filedesc:
                        file = {'file': (asset.name, filedesc, asset.type)}
                        try:
                            r = requests.post(url=os.path.join(Configuration.settings.airs_endpoint, "collections",item.collection, "items", item.id, "assets", asset.name), files=file)
                            if r.ok:
                                LOGGER.debug("asset uploaded successfully")                    
                            else:
                                msg = "Failed to upload asset: {} - {} on {}".format(r.status_code, r.content, Configuration.settings.airs_endpoint)
                                LOGGER.error(msg)
                                raise RegisterException(msg)
                        except requests.exceptions.ConnectionError:
                            msg = "AIRS Service can not be reached ({})".format(Configuration.settings.airs_endpoint)
                            LOGGER.error(msg)
                            raise ConnectionException(msg)
                else:
                    LOGGER.info("{} not managed".format(asset.name))
            LOGGER.debug("ingestion: 6 - register")
            __update_status__(self, state='PROGRESS', meta={'step':'register_item', "ACTION": "INGEST", "TARGET": url})
            item_already_exists = False
            try:
                r = requests.get(url=os.path.join(Configuration.settings.airs_endpoint, "collections", item.collection, "items", item.id), headers={"Content-Type": "application/json"})
                if r.ok:
                    item_already_exists = True
            except requests.exceptions.ConnectionError:
                msg = "AIRS Service can not be reached ({})".format(Configuration.settings.airs_endpoint)
                LOGGER.error(msg)
                raise ConnectionException(msg)
            try:
                if item_already_exists:
                    r = requests.put(url=os.path.join(Configuration.settings.airs_endpoint, "collections", item.collection, "items", item.id), data=to_json(item), headers={"Content-Type": "application/json"})
                else:
                    r = requests.post(url=os.path.join(Configuration.settings.airs_endpoint, "collections", item.collection, "items"), data=to_json(item), headers={"Content-Type": "application/json"})
                if r.ok:
                    item_from_json(r.content).model_dump()
                    return OutputIngestProcess(item_location=os.path.join(Configuration.settings.airs_endpoint, "collections", item.collection, "items", item.id)).model_dump()
                else:
                    LOGGER.error("Item has not been registered: {} - {}".format(r.status_code, r.content))
                    LOGGER.error(to_json(item))
                    raise RegisterException("Item has not been registered: {} - {}".format(r.status_code, r.content))
            except requests.exceptions.ConnectionError:
                msg = "AIRS Service can not be reached ({})".format(Configuration.settings.airs_endpoint)
                LOGGER.error(msg)
                raise ConnectionException(msg)
        else:
            LOGGER.error("No driver found for {}".format(url))
            raise DriverException("No driver found for  {}".format(url))
        
    def __check_assets__(url: str, assets: list[Asset], file_exists: bool = False):
        for asset in assets:
            if asset.name is None:
                raise DriverException("Invalid asset for {} : no name provided".format(url))
            if asset.href is None:
                raise DriverException("Invalid asset {} for {} : no href provided".format(asset.name, url))
            if asset.roles is None:
                raise DriverException("Invalid asset {} for {} : no roles provided".format(asset.name, url))
            if file_exists:
                if asset.airs__managed is True and not os.path.exists(asset.href):
                    raise DriverException("Invalid asset {} for {} : file {} not found".format(asset.name, url, asset.href))
