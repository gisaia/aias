import os
from celery import Task, shared_task
from pydantic import BaseModel, Field
import hashlib
import time
from airs.core.models.model import Item
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.job import StatusInfo
from aproc.core.processes.process import Process as Process
from aproc.core.utils import base_model2description
from extensions.aproc.proc.download.drivers.driver import Driver
from extensions.aproc.proc.download.drivers.drivers import Drivers
from extensions.aproc.proc.download.drivers.exceptions import DriverException
from extensions.aproc.proc.download.notifications import Notifications
from extensions.aproc.proc.download.settings import Configuration

DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


def __update_status__(task: Task, state: str, meta: dict = None):
    LOGGER.info(task.name+" "+state+" "+str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)


class InputDownloadProcess(BaseModel):
    item: Item = Field(title="Full item description containing the asset to be downloaded")
    asset_name: str = Field(title="Asset's name, within the item, to be downloaded")
    email: str = Field(title="email of the person to notify once downloaded")
    crop_wkt: str = Field(title="WKT geometry for cropping the data")
    target_projection: str = Field(title="epsg target projection")
    target_format: str = Field(title="target format")


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
    outputs=base_model2description(StatusInfo)
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
        target_directory = os.path.join(Configuration.settings.outbox_directory, send_to.replace("@","_").replace(".","_"))
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        file_name = os.path.basename(item.assets.get(asset_name).href)
        if not os.path.exists(file_name):  # TODO REMOVE THE NOT ONCED TESTED
            file_name = hashlib.md5(str(time.time_ns()).encode("utf-8")).hexdigest()+file_name
        return (target_directory, file_name)

    @shared_task(bind=True)
    def execute(self, item: dict, header: dict[str, str], asset_name: str, crop_wkt: str, target_projection: str, target_format: str, send_to: str) -> dict:
        item: Item = Item(**item)
        # self is a celery task because bind=True
        driver: Driver = Drivers.solve(item, asset_name)
        if driver is not None:
            __update_status__(self, state='PROGRESS', meta={"ACTION": "DOWNLOAD", "TARGET": item.id+"/"+asset_name})
            (target_directory, file_name) = AprocProcess.__get_download_location__(item, asset_name, send_to)
            context = {
                "target_directory": target_directory,
                "target_projection": target_projection,
                "target_format": target_format,
                "file_name": file_name,
                "send_to": send_to,
                "item_id": item.id,
                "asset_name": asset_name
            }
            try:
                driver.fetch_and_transform(
                    item=item,
                    asset_name=asset_name,
                    target_directory=target_directory,
                    file_name=file_name,
                    crop_wkt=crop_wkt,
                    target_projection=target_projection,
                    target_format=target_format)
                Notifications.try_send_to(Configuration.settings.email_content_user, send_to, context=context)
            except Exception as e:
                LOGGER.error("Failed to download the asset {}/{}".format(item.id, asset_name))
                LOGGER.exception(e)
                context["error"] = str(e.__cause__)
                Notifications.try_send_to(Configuration.settings.email_content_error_download, to=send_to, context=context)
        else:
            LOGGER.error("No driver found for {} in {}".format(asset_name, Item(**item).model_dump_json))
            raise DriverException("No driver found for {} in {}".format(asset_name, Item(**item).model_dump_json))
