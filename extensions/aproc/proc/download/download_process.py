import hashlib
import os
import shutil
from datetime import datetime

from celery import shared_task
from pydantic import BaseModel, Field

from airs.core.models.model import Item
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.processes.process import Process
from aproc.core.settings import Configuration as AprocConfiguration
from aproc.core.utils import base_model2description
from extensions.aproc.proc.download.drivers.download_driver import \
    DownloadDriver
from extensions.aproc.proc.download.notifications import Notifications
from extensions.aproc.proc.download.settings import \
    Configuration as DownloadConfiguration
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.drivers.exceptions import (DriverException,
                                                      RegisterException)
from extensions.aproc.proc.processes.arlas_services_helper import ARLASServicesHelper
from extensions.aproc.proc.processes.process_model import InputProcess
from extensions.aproc.proc.variables import (ARLAS_COLLECTION_KEY,
                                             ARLAS_ITEM_ID_KEY,
                                             DOWNLOAD_FAILED_MSG, EVENT_ACTION,
                                             EVENT_CATEGORY_KEY,
                                             EVENT_KIND_KEY, EVENT_MODULE_KEY,
                                             EVENT_OUTCOME_KEY, EVENT_REASON,
                                             EVENT_TYPE_KEY, USER_ACTION_KEY,
                                             USER_EMAIL_KEY, USER_ID_KEY)

AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")
DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


class InputDownloadProcess(InputProcess):
    requests: list[dict[str, str]] = Field(default=[], title="The list of item (collection, item_id) to download")
    crop_wkt: str = Field(default=None, title="WKT geometry for cropping the data")
    target_projection: str = Field(default=None, title="epsg target projection")
    target_format: str = Field(default=None, title="target format")
    raw_archive: bool = Field(default=True, title="raw archive")


class OutputDownloadProcess(BaseModel):
    download_locations: list[str] = Field(title="Downloaded file location", description="Location of the downloaded file")


summary: ProcessSummary = ProcessSummary(
    title="Download an item.",
    description="Download an item from the catalog.",
    keywords=["Download", "Export"],
    id="download",
    version=AIAS_VERSION,
    jobControlOptions=[JobControlOptions.async_execute],
    outputTransmission=[TransmissionMode.reference],
    # TODO: provide the links if any => link could be the execute endpoint
    links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(exclude_none=True, exclude_unset=True),
    inputs=base_model2description(InputDownloadProcess),
    outputs=base_model2description(OutputDownloadProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            DownloadConfiguration.init(configuration_file=configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME))
            DownloadConfiguration.raise_if_not_valid()
            DriverManager.init(summary.id, DownloadConfiguration.settings.drivers)
        else:
            raise DriverException("Invalid configuration for download drivers ({})".format(configuration))
        AprocProcess.input_model = InputDownloadProcess
        Notifications.init()
        description.inputs.get("include_drivers").schema_.items.enum = DriverManager.driver_names(summary.id)
        description.inputs.get("exclude_drivers").schema_.items.enum = DriverManager.driver_names(summary.id)

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    @staticmethod
    def before_execute(headers: dict[str, str], requests: list[dict[str, str]], crop_wkt: str, target_projection: str = "native", target_format: str = "native", raw_archive: bool = True, include_drivers: list[str] = [], exclude_drivers: list[str] = []) -> dict[str, str]:
        (send_to, user_id) = ARLASServicesHelper.get_user_email(headers.get("authorization"))
        for request in requests:
            collection: str = request.get("collection")
            item_id: str = request.get("item_id")
            mail_context = {
                "raw_archive": raw_archive,
                "target_projection": target_projection,
                "target_format": target_format,
                "item_id": item_id,
                "collection": collection,
                "target_directory": None,
                "file_name": None,
                "error": None,
                "arlas-user-email": send_to
            }
            Notifications.report(None, DownloadConfiguration.settings.email_request_subject_admin, DownloadConfiguration.settings.email_request_content_admin, DownloadConfiguration.settings.notification_admin_emails.split(","), context=mail_context)
            Notifications.report(None, DownloadConfiguration.settings.email_request_subject_user, DownloadConfiguration.settings.email_request_content_user, to=[send_to], context=mail_context)
            # RGPD : log level is info
            LOGGER.debug("checking for item access {}/{} for {}".format(collection, item_id, send_to))
            item: Item = ARLASServicesHelper.get_item_from_arlas(arlas_url_search=DownloadConfiguration.settings.arlas_url_search, collection=collection, item_id=item_id, headers=headers)
            if item is None:
                error_msg = "{}/{} not found".format(collection, item_id)
                LOGGER.error(error_msg)
                LOGGER.info(DOWNLOAD_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                mail_context["error"] = error_msg
                Notifications.report(None, DownloadConfiguration.settings.email_subject_error_download, DownloadConfiguration.settings.email_content_error_download, DownloadConfiguration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                raise RegisterException(error_msg)
            else:
                LOGGER.debug("{} can access {}/{}".format(send_to, collection, item_id))
        return {}

    @staticmethod
    def __get_download_location__(item: Item, send_to: str) -> tuple[str, str]:
        if send_to is None:
            send_to = "anonymous"
        relative_target_directory = os.path.join(send_to.split("@")[0].replace(".", "_").replace("-", "_"), item.id + "_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        target_directory = os.path.join(DownloadConfiguration.settings.outbox_directory, relative_target_directory)
        if not os.path.exists(target_directory):
            LOGGER.info("create {}".format(target_directory))
            os.makedirs(target_directory)
        return (target_directory, relative_target_directory)

    @staticmethod
    def get_resource_id(inputs: BaseModel):
        inputs: InputDownloadProcess = InputDownloadProcess(**inputs.model_dump(exclude_none=True, exclude_unset=True))
        hash_object = hashlib.sha1("/".join(list(map(lambda r: r["collection"] + r["item_id"], inputs.requests))).encode())
        return hash_object.hexdigest()

    @shared_task(bind=True, track_started=True)
    def execute(self, headers: dict[str, str], requests: list[dict[str, str]], crop_wkt: str, target_projection: str = "native", target_format: str = "native", raw_archive: bool = True, include_drivers: list[str] = [], exclude_drivers: list[str] = []) -> dict:
        (send_to, user_id) = ARLASServicesHelper.get_user_email(headers.get("authorization"))
        LOGGER.debug("processing download requests from {}".format(send_to))
        download_locations = []
        for request in requests:
            collection: str = request.get("collection")
            item_id: str = request.get("item_id")
            mail_context = {
                "target_projection": target_projection,
                "target_format": target_format,
                "item_id": item_id,
                "collection": collection,
                "target_directory": None,
                "file_name": None,
                "error": None,
                "arlas-user-email": send_to
            }
            item: Item = ARLASServicesHelper.get_item_from_airs(airs_endpoint=AprocConfiguration.settings.airs_endpoint, collection=collection, item_id=item_id)
            if item is None:
                error_msg = "{}/{} not found".format(collection, item_id)
                LOGGER.error(error_msg)
                LOGGER.info(DOWNLOAD_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                mail_context["error"] = error_msg
                Notifications.report(None, DownloadConfiguration.settings.email_subject_error_download, DownloadConfiguration.settings.email_content_error_download, DownloadConfiguration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                raise RegisterException(error_msg)

            driver: DownloadDriver = DriverManager.solve(summary.id, item, include_drivers=include_drivers, exclude_drivers=exclude_drivers)
            if driver is not None:
                try:
                    LOGGER.info("Download will be done by {}".format(driver.name))
                    Process.update_task_status(LOGGER, self, state='PROGRESS', meta={"ACTION": "DOWNLOAD", "TARGET": item_id})
                    target_directory, relative_target_directory = AprocProcess.__get_download_location__(item, send_to)
                    LOGGER.info("Download will be placed in {}".format(target_directory))
                    mail_context["target_directory"] = target_directory
                    mail_context = AprocProcess.__update_paths__(mail_context)
                    driver.fetch_and_transform(
                        item=item,
                        target_directory=target_directory,
                        crop_wkt=crop_wkt,
                        target_projection=target_projection,
                        target_format=target_format,
                        raw_archive=raw_archive)
                    if DownloadConfiguration.settings.outbox_s3 and DownloadConfiguration.settings.outbox_s3.bucket:
                        ARLASServicesHelper.dir2s3(target_directory, relative_target_directory, DownloadConfiguration.settings.outbox_s3)
                        if DownloadConfiguration.settings.clean_outbox_directory:
                            LOGGER.debug("clean {}".format(target_directory))
                            shutil.rmtree(target_directory)
                        mail_context["target_directory"] = DownloadConfiguration.settings.outbox_s3.asset_http_endpoint_url.format(DownloadConfiguration.settings.outbox_s3.bucket, relative_target_directory)
                    Notifications.report(item, DownloadConfiguration.settings.email_subject_user, DownloadConfiguration.settings.email_content_user, to=[send_to], context=mail_context, outcome="success")
                    Notifications.report(item, DownloadConfiguration.settings.email_subject_admin, DownloadConfiguration.settings.email_content_admin, DownloadConfiguration.settings.notification_admin_emails.split(","), context=mail_context)
                    LOGGER.info("Download success", extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "success", USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                    download_locations.append(mail_context["target_directory"])
                except Exception as e:
                    error_msg = "Failed to download the item {}/{} ({})".format(collection, item_id, str(e))
                    LOGGER.info(DOWNLOAD_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                    LOGGER.error(error_msg)
                    LOGGER.exception(e)
                    mail_context["error"] = error_msg
                    Notifications.report(item, DownloadConfiguration.settings.email_subject_error_download, DownloadConfiguration.settings.email_content_error_download, DownloadConfiguration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                    raise Exception(error_msg)
            else:
                error_msg = "No driver found for {}/{}".format(collection, item_id)
                LOGGER.info(DOWNLOAD_FAILED_MSG, extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", EVENT_REASON: error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                LOGGER.error(error_msg)
                mail_context["error"] = error_msg
                Notifications.report(item, DownloadConfiguration.settings.email_subject_error_download, DownloadConfiguration.settings.email_content_error_download, DownloadConfiguration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                raise DriverException(error_msg)
        return OutputDownloadProcess(download_locations=download_locations).model_dump(exclude_none=True, exclude_unset=True)

    @staticmethod
    def __update_paths__(mail_context: dict[str, str]):
        try:
            if mail_context.get("target_directory"):
                if DownloadConfiguration.settings.email_path_prefix_add:
                    mail_context["target_directory"] = os.path.join(DownloadConfiguration.settings.email_path_prefix_add, mail_context["target_directory"].removeprefix(DownloadConfiguration.settings.outbox_directory).removeprefix("/"))
                if DownloadConfiguration.settings.email_path_to_windows:
                    mail_context["target_directory"] = mail_context["target_directory"].replace("/", "\\")
        except Exception as e:
            LOGGER.exception(e)
        return mail_context
