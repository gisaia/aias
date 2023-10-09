import hashlib
import json
import os
import time

import requests
from celery import Task, shared_task
from pydantic import BaseModel, Field

from airs.core.models import mapper
from airs.core.models.model import Item
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.job import StatusInfo
from aproc.core.processes.process import Process as Process
from aproc.core.settings import Configuration as AprocConfiguration
from aproc.core.utils import base_model2description
from extensions.aproc.proc.download.drivers.driver import Driver
from extensions.aproc.proc.download.drivers.drivers import Drivers
from extensions.aproc.proc.download.drivers.exceptions import (
    DriverException, RegisterException)
from extensions.aproc.proc.download.notifications import Notifications
from extensions.aproc.proc.download.settings import Configuration

DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


def __update_status__(task: Task, state: str, meta: dict = None):
    LOGGER.info(task.name+" "+state+" "+str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)

# TODO TO BE REMOVED
class ItemDownloadProcess(BaseModel):
    collection: str | None = Field(default=None, title="Collection name", description="Name of the collection where the item is registered", minOccurs=1, maxOccurs=1)
    item_id: str | None = Field(default=None, title="Item's id to be downloaded")


class InputDownloadProcess(BaseModel):
    requests: list[dict[str, str]] = Field(default=[], title="The list of item (collection, item_id) to download")
    crop_wkt: str = Field(default=None, title="WKT geometry for cropping the data")
    target_projection: str = Field(default=None, title="epsg target projection")
    target_format: str = Field(default=None, title="target format")


class OutputDownloadProcess(BaseModel):
    download_location: str = Field(title="Downloaded file location", description="Location of the downloaded file")


summary: ProcessSummary = ProcessSummary(
            title="Download an item.",
            description="Download an item from the catalog.",
            keywords=["Download", "Export"],
            id="download",
            version="0.1",
            jobControlOptions=[JobControlOptions.async_execute],
            outputTransmission=[TransmissionMode.reference],
            # TODO: provide the links if any => link could be the execute endpoint
            links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(),
    inputs=base_model2description(InputDownloadProcess),
    outputs=base_model2description(OutputDownloadProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            Drivers.init(configuration_file=configuration[DRIVERS_CONFIGURATION_FILE_PARAM_NAME])
        else:
            raise DriverException("Invalid configuration for download drivers ({})".format(configuration))
        AprocProcess.input_model = InputDownloadProcess
        Notifications.init()

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    def __get_download_location__(item: Item, send_to: str, format:str) -> (str, str):
        if send_to is None: send_to = "anonymous"
        target_directory = os.path.join(Configuration.settings.outbox_directory, send_to.split("@")[0].replace(".","_").replace("-","_"), item.id)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        file_name = os.path.basename(item.id.replace("-", "_").replace(" ", "_").replace("/", "_").replace("\\", "_").replace("@", "_"))+"."+format
        if os.path.exists(file_name):
            file_name = hashlib.md5(str(time.time_ns()).encode("utf-8")).hexdigest()+file_name
        return (target_directory, file_name)

    def get_resource_id(inputs: BaseModel):
        inputs: InputDownloadProcess = InputDownloadProcess(**inputs.model_dump())        
        hash_object = hashlib.sha1("/".join(list(map(lambda r: r["collection"]+r["item_id"], inputs.requests))).encode())
        return hash_object.hexdigest()

    @shared_task(bind=True)
    def execute(self, context: dict[str, str], requests: list[dict[str, str]], crop_wkt: str, target_projection: str, target_format: str = "Geotiff") -> dict:
        # self is a celery task because bind=True
        for request in requests:
            collection: str = request.get("collection")
            item_id: str = request.get("item_id")
            mail_context = {
                "target_projection": target_projection,
                "target_format": target_format,
                "item_id": item_id,
                "collection": collection,
                "arlas-user-email": context.get("arlas-user-email", "anonymous"),
                "target_directory": None,
                "file_name": None,
                "error": None
            }
            send_to: str = context.get("arlas-user-email")
            if send_to is None:
                LOGGER.warning("download request for {}/{} is anonymous".format(collection, item_id))
            else:
                LOGGER.info("download request for {}/{}".format(collection, item_id))

            Notifications.try_send_to(Configuration.settings.email_request_subject_admin, Configuration.settings.email_request_content_admin, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
            if send_to is not None: Notifications.try_send_to(Configuration.settings.email_request_subject_user, Configuration.settings.email_request_content_user, to=[send_to], context=mail_context)

            item: Item = AprocProcess.__get_item__(collection=collection, item_id=item_id, headers=context)
            if item is None:
                error_msg = "{}/{} not found".format(collection, item_id)
                LOGGER.error(error_msg)
                mail_context["error"] = error_msg
                Notifications.try_send_to(Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
                raise RegisterException(error_msg)

            driver: Driver = Drivers.solve(item)
            if driver is not None:
                try:
                    __update_status__(self, state='PROGRESS', meta={"ACTION": "DOWNLOAD", "TARGET": item_id})
                    (target_directory, file_name) = AprocProcess.__get_download_location__(item, send_to, target_format)
                    LOGGER.info("Download will be placed in {}/{}".format(target_directory, file_name))
                    mail_context["target_directory"] = target_directory
                    mail_context["file_name"] = file_name
                    mail_context = AprocProcess.__update_paths__(mail_context)
                    driver.fetch_and_transform(
                        item=item,
                        target_directory=target_directory,
                        file_name=file_name,
                        crop_wkt=crop_wkt,
                        target_projection=target_projection,
                        target_format=target_format)
                    if send_to is not None: Notifications.try_send_to(Configuration.settings.email_subject_user, Configuration.settings.email_content_user, to=[send_to], context=mail_context)
                    Notifications.try_send_to(Configuration.settings.email_subject_admin, Configuration.settings.email_content_admin, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
                    return OutputDownloadProcess(download_location=os.path.join(target_directory, file_name)).model_dump()
                except Exception as e:
                    error_msg = "Failed to download the item {}/{} ({})".format(collection, item_id, e.__cause__)
                    LOGGER.error(error_msg)
                    LOGGER.exception(e)
                    mail_context["error"] = error_msg
                    raise Exception(error_msg)
            else:
                error_msg = "No driver found for {}/{}".format(collection, item_id)
                LOGGER.error(error_msg)
                mail_context["error"] = error_msg
                Notifications.try_send_to(Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
                raise DriverException(error_msg)

    def __get_item__(collection: str, item_id: str, headers: dict[str, str] = {}):
        try:
            r = requests.get(url=Configuration.settings.arlas_url_search.format(collection=Configuration.settings.collection_prefix+"_"+collection, item=item_id), headers=headers)
            if r.ok:
                result = r.json()
                if result.get("hits") and len(result.get("hits")) > 0:
                    return mapper.item_from_dict(result.get("hits")[0]["data"])
                else:
                    LOGGER.warn("No result found for {}/{}".format(collection, item_id))
                    return None
            else:
                LOGGER.error("Error while retrieving {}/{} ({})".format(collection, item_id, r.content))
                return None
        except Exception as e:
            LOGGER.error("Exception while retrieving {}/{}".format(collection, item_id))
            LOGGER.exception(e)
            return None

    def __update_paths__(mail_context: dict[str, str]):
        try:
            if mail_context.get("target_directory"):
                if not not Configuration.settings.email_path_prefix_add:
                    mail_context["target_directory"] = os.path.join(Configuration.settings.email_path_prefix_add, mail_context["target_directory"].removeprefix(Configuration.settings.outbox_directory).removeprefix("/"))
                if Configuration.settings.email_path_to_windows:
                    mail_context["target_directory"] = mail_context["target_directory"].replace("/","\\")
        except Exception as e:
            LOGGER.exception(e)
        return mail_context
