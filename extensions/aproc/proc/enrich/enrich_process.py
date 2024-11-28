import hashlib
import os
from time import time

import requests
from celery import Task, shared_task
from pydantic import BaseModel, Field

from airs.core.models import mapper
from airs.core.models.model import Asset, Item
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.processes.process import Process as Process
from aproc.core.settings import Configuration as AprocConfiguration
from aproc.core.utils import base_model2description
from extensions.aproc.proc.enrich.drivers.driver import Driver
from extensions.aproc.proc.enrich.drivers.drivers import Drivers
from extensions.aproc.proc.enrich.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.ingest_process import AprocProcess as IngestAprocProcess

DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


def __update_status__(task: Task, state: str, meta: dict = None):
    LOGGER.info(task.name + " " + state + " "  + str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)


class InputEnrichProcess(BaseModel):
    requests: list[dict[str, str]] = Field(default=[], title="The list of items (collection, item_id) to enrich")
    asset_type: str = Field(default=None, title="Name of the asset type to add (e.g. cog)")


class OutputEnrichProcess(BaseModel):
    item_locations: list[str] = Field(title="Items locations", description="Locations of the Item on the ARLAS Item Registration Service")


summary: ProcessSummary = ProcessSummary(
    title="Enrich one or more items with assets.",
    description="Enrich one or more items with assets.",
    keywords=["Enrich"],
    id="enrich",
    version="0.1",
    jobControlOptions=[JobControlOptions.async_execute],
    outputTransmission=[TransmissionMode.reference],
    # TODO: provide the links if any => link could be the execute endpoint
    links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(),
    inputs=base_model2description(InputEnrichProcess),
    outputs=base_model2description(OutputEnrichProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            Drivers.init(configuration_file=configuration[DRIVERS_CONFIGURATION_FILE_PARAM_NAME])
        else:
            raise DriverException("Invalid configuration for enrich drivers ({})".format(configuration))
        AprocProcess.input_model = InputEnrichProcess

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    @staticmethod
    def before_execute(headers: dict[str, str], requests: list[dict[str, str]], asset_type: str) -> dict[str, str]:
        return {}

    def get_resource_id(inputs: BaseModel):
        inputs: InputEnrichProcess = InputEnrichProcess(**inputs.model_dump())        
        hash_object = hashlib.sha1("/".join(list(map(lambda r: r["collection"] + r["item_id"], inputs.requests))).encode())
        return hash_object.hexdigest()

    @shared_task(bind=True, track_started=True)
    def execute(self, headers: dict[str, str], requests: list[dict[str, str]], asset_type: str) -> dict:
        item_locations = []
        for request in requests:
            collection: str = request.get("collection")
            item_id: str = request.get("item_id")
            item: Item = AprocProcess.__get_item_from_airs__(collection=collection, item_id=item_id)
            if item is None:
                error_msg = "{}/{} not found".format(collection, item_id)
                LOGGER.error(error_msg)
                LOGGER.info("Enrichment failed", extra={"event.kind": "event", "event.category": "file", "event.type": "user-action", "event.action": "enrich", "event.outcome": "failure", "event.reason": error_msg, "event.module": "aproc-enrich", "arlas.collection": collection, "arlas.item.id": item_id})
                raise DriverException(error_msg)
            driver: Driver = Drivers.solve(item)
            if driver is not None:
                try:
                    LOGGER.info("ingestion: 1 - enrichment will be done by {}".format(driver.name))
                    __update_status__(self, state='PROGRESS', meta={"ACTION": "ENRICH", "TARGET": item_id})
                    LOGGER.info("Build asset {}".format(asset_type))
                    start = time()
                    asset, asset_location = driver.create_asset(
                        item=item,
                        asset_type=asset_type)
                    end = time()
                    LOGGER.info("took {} ms".format(end - start))
                    asset: Asset = asset
                    asset.href = asset_location
                    item.assets[asset.name] = asset
                    if item.properties.keywords is None:
                        item.properties.keywords = []
                    item.properties.keywords.append("has_{}".format(asset_type))
                    LOGGER.info("Enrichment success", extra={"event.kind": "event", "event.category": "file", "event.type": "user-action", "event.action": "enrich", "event.outcome": "success", "event.module": "aproc-enrich", "arlas.collection": collection, "arlas.item.id": item_id})

                    LOGGER.debug("ingestion: 2 - upload asset if needed")
                    __update_status__(self, state='PROGRESS', meta={'step': 'upload', 'current': 1, 'asset': asset.name, 'total': len(item.assets), "ACTION": "ENRICH", "TARGET": item_id})
                    start = time()
                    IngestAprocProcess.upload_asset_if_managed(item, asset, AprocConfiguration.settings.airs_endpoint)
                    end = time()
                    LOGGER.info("took {} ms".format(end - start))

                    LOGGER.debug("ingestion: 3 - update")
                    __update_status__(self, state='PROGRESS', meta={'step': 'update_item', "ACTION": "ENRICH", "TARGET": item_id})
                    item: Item = IngestAprocProcess.insert_or_update_item(item, AprocConfiguration.settings.airs_endpoint)
                    item_locations.append(os.path.join(AprocConfiguration.settings.airs_endpoint, "collections", item.collection, "items", item.id))
                except Exception as e:
                    error_msg = "Failed to enrich the item {}/{} ({})".format(collection, item_id, str(e))
                    LOGGER.info("Enrichment failed", extra={"event.kind": "event", "event.category": "file", "event.type": "user-action", "event.action": "enrich", "event.outcome": "failure", "event.reason": error_msg, "event.module": "aproc-enrich", "arlas.collection": collection, "arlas.item.id": item_id})
                    LOGGER.error(error_msg)
                    LOGGER.exception(e)
                    raise Exception(error_msg)
            else:
                error_msg = "No driver found for {}/{}".format(collection, item_id)
                LOGGER.info("Enrichment failed", extra={"event.kind": "event", "event.category": "file", "event.type": "user-action", "event.action": "enrich", "event.outcome": "failure", "event.reason": error_msg, "event.module": "aproc-enrich", "arlas.collection": collection, "arlas.item.id": item_id})
                LOGGER.error(error_msg)
                raise DriverException(error_msg)
        return OutputEnrichProcess(item_locations=item_locations).model_dump()

    def __get_item_from_airs__(collection: str, item_id: str):
        try:
            r = requests.get(url=os.path.join(AprocConfiguration.settings.airs_endpoint, "collections", collection, "items", item_id))
            if r.ok:
                return mapper.item_from_json(r.content)
            else:
                return None
        except Exception:
            return None
