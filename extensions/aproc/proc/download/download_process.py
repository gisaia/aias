import os
import json
import requests
from celery import Task, shared_task
from pydantic import BaseModel, Field
import hashlib
import time
from airs.core.models import mapper
from airs.core.models.model import Item
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.job import StatusInfo
from aproc.core.processes.process import Process as Process
from aproc.core.utils import base_model2description
from extensions.aproc.proc.download.drivers.driver import Driver
from extensions.aproc.proc.download.drivers.drivers import Drivers
from extensions.aproc.proc.download.drivers.exceptions import DriverException, RegisterException
from extensions.aproc.proc.download.notifications import Notifications
from extensions.aproc.proc.download.settings import Configuration
from aproc.core.settings import Configuration as AprocConfiguration

DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


def __update_status__(task: Task, state: str, meta: dict = None):
    LOGGER.info(task.name+" "+state+" "+str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)


class InputDownloadProcess(BaseModel):
    collection: str = Field(title="Collection name", description="Name of the collection where the item is registered", minOccurs=1, maxOccurs=1)
    item_id: str = Field(title="Asset's item id to be downloaded")
    asset_name: str = Field(title="Asset's name, within the item, to be downloaded")
    crop_wkt: str  = Field(default=None, title="WKT geometry for cropping the data")
    target_projection: str  = Field(default=None, title="epsg target projection")
    target_format: str  = Field(default=None, title="target format")


class OutputDownloadProcess(BaseModel):
    download_location: str = Field(title="Downloaded file location", description="Location of the downloaded file")


summary: ProcessSummary = ProcessSummary(
            title="Download assets.",
            description="Download assets from the catalog.",
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

    def __get_download_location__(item: Item, asset_name: str, send_to: str) -> (str, str):
        if send_to is None: send_to = "anonymous"
        target_directory = os.path.join(Configuration.settings.outbox_directory, send_to.split("@")[0].replace(".","_").replace("-","_"), item.id)
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        file_name = os.path.basename(item.assets.get(asset_name).href)
        if os.path.exists(file_name):
            file_name = hashlib.md5(str(time.time_ns()).encode("utf-8")).hexdigest()+file_name
        return (target_directory, file_name)

    def get_resource_id(inputs: BaseModel):
        inputs: InputDownloadProcess = InputDownloadProcess(**inputs.model_dump())
        hash_object = hashlib.sha1((inputs.collection+inputs.item_id+inputs.asset_name).encode())
        return hash_object.hexdigest()


    @shared_task(bind=True)
    def execute(self, context: dict[str, str], collection: str, item_id: str, asset_name: str, crop_wkt: str, target_projection: str, target_format: str) -> dict:
        # self is a celery task because bind=True
        mail_context = {
            "target_projection": target_projection,
            "target_format": target_format,
            "item_id": item_id,
            "collection": collection,
            "asset_name": asset_name,
            "arlas-user-email": context.get("arlas-user-email", "anonymous"),
            "target_directory": None,
            "file_name": None,
            "error": None
        }
        send_to: str = context.get("arlas-user-email")
        if send_to is None:
            LOGGER.warning("download request for {}/{}/{} is anonymous".format(collection, item_id, asset_name))
        else:
            LOGGER.info("download request for {}/{}/{} is for {}".format(collection, item_id, asset_name, send_to))

        Notifications.try_send_to(Configuration.settings.email_request_subject_admin, Configuration.settings.email_request_content_admin, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
        if send_to is not None: Notifications.try_send_to(Configuration.settings.email_request_subject_user, Configuration.settings.email_request_content_user, to=[send_to], context=mail_context)


        item: Item = AprocProcess.__get_item__(collection=collection, item_id=item_id)
        if item is None:
            LOGGER.error("{}/{}/{} not found".format(collection, item_id, asset_name))
            mail_context["error"] = "{}/{}/{} not found".format(collection, item_id, asset_name)
            Notifications.try_send_to(Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
            raise RegisterException("{}/{}/{} not found".format(collection, item_id, asset_name))

        driver: Driver = Drivers.solve(item, asset_name)
        if driver is not None:
            try:
                __update_status__(self, state='PROGRESS', meta={"ACTION": "DOWNLOAD", "TARGET": item_id+"/"+asset_name})
                (target_directory, file_name) = AprocProcess.__get_download_location__(item, asset_name, send_to)
                LOGGER.info("Download will be placed in {}/{}".format(target_directory, file_name))
                mail_context["target_directory"] = target_directory
                mail_context["file_name"] = file_name
                mail_context = AprocProcess.__update_paths__(mail_context)
                driver.fetch_and_transform(
                    item=item,
                    asset_name=asset_name,
                    target_directory=target_directory,
                    file_name=file_name,
                    crop_wkt=crop_wkt,
                    target_projection=target_projection,
                    target_format=target_format)
                if send_to is not None: Notifications.try_send_to(Configuration.settings.email_subject_user, Configuration.settings.email_content_user, to=[send_to], context=mail_context)
                Notifications.try_send_to(Configuration.settings.email_subject_admin, Configuration.settings.email_content_admin, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
                return OutputDownloadProcess(download_location=os.path.join(target_directory, file_name)).model_dump()
            except Exception as e:
                LOGGER.error("Failed to download the asset {}/{}/{}".format(collection, item_id, asset_name))
                LOGGER.exception(e)
                mail_context["error"] = str(e.__cause__)
                raise Exception("Failed to download the asset {}/{}/{}: {}".format(collection, item_id, asset_name, e.__cause__))
        else:
            LOGGER.error("No driver found for {} in {}".format(asset_name, item.model_dump_json()))
            mail_context["error"] = str("No driver found for {}/{}/{}".format(collection, item_id, asset_name))
            Notifications.try_send_to(Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
            raise DriverException("No driver found for {}/{}/{}".format(collection, item_id, asset_name))

    def __get_item__(collection: str, item_id: str):
        try:
            r = requests.get(url=os.path.join(AprocConfiguration.settings.airs_endpoint, "collections", collection, "items", item_id))
            if r.ok:
                return mapper.item_from_json(r.content)
            else:
                return None
        except Exception:
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
