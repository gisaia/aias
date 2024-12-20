import hashlib
import mimetypes
import os
import shutil
from datetime import datetime

import requests
from celery import Task, shared_task
from pydantic import BaseModel, Field

import airs.core.s3 as s3
from airs.core.models import mapper
from airs.core.models.model import Item
from airs.core.settings import S3 as S3Configuration
from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
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

EVENT_KIND_KEY = "event.kind"
ARLAS_ITEM_ID_KEY = "arlas.item.id"
ARLAS_COLLECTION_KEY = "arlas.collection"
EVENT_CATEGORY_KEY = "event.category"
EVENT_TYPE_KEY = "event.type"
USER_ACTION_KEY = "user-action"
EVENT_ACTION = "event.action"
EVENT_OUTCOME_KEY = "event.outcome"
USER_ID_KEY = "user.id"
USER_EMAIL_KEY = "user.email"
EVENT_MODULE_KEY = "event.module"


def __update_status__(task: Task, state: str, meta: dict = None):
    LOGGER.info(task.name + " " + state + " " + str(meta))
    if task.request.id is not None:
        task.update_state(state=state, meta=meta)


class InputDownloadProcess(BaseModel):
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

    @staticmethod
    def before_execute(headers: dict[str, str], requests: list[dict[str, str]], crop_wkt: str, target_projection: str = "native", target_format: str = "native", raw_archive: bool = True) -> dict[str, str]:
        (send_to, user_id) = AprocProcess.__get_user_email__(headers.get("authorization"))
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
            Notifications.report(None, Configuration.settings.email_request_subject_admin, Configuration.settings.email_request_content_admin, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
            Notifications.report(None, Configuration.settings.email_request_subject_user, Configuration.settings.email_request_content_user, to=[send_to], context=mail_context)
            # RGPD : log level is info
            LOGGER.debug("checking for download request {}/{} for {}".format(collection, item_id, send_to))
            item: Item = AprocProcess.__get_item_from_arlas__(collection=collection, item_id=item_id, headers=headers)
            if item is None:
                error_msg = "{}/{} not found".format(collection, item_id)
                LOGGER.error(error_msg)
                LOGGER.info("Download failed", extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", "event.reason": error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                mail_context["error"] = error_msg
                Notifications.report(None, Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                raise RegisterException(error_msg)
            else:
                LOGGER.debug("{} can access {}/{}".format(send_to, collection, item_id))
        return {}

    @staticmethod
    def __get_user_email__(authorization: str):
        import jwt
        send_to: str = "anonymous"
        user_id: str = "anonymous"
        try:
            if not not authorization:
                token_content = jwt.decode(authorization.removeprefix("Bearer "), options={"verify_signature": False})
                if not not token_content.get("email"):
                    send_to = token_content.get("email")
                else:
                    LOGGER.error("email not found in token {}".format(token_content))
                if not not token_content.get("sub"):
                    user_id = token_content.get("sub")
                else:
                    LOGGER.error("subject not found in token {}".format(token_content))
            else:
                LOGGER.error("no token in header")
        except Exception as e:
            LOGGER.error("Can not open token from header")
            LOGGER.exception(e)
        return (send_to, user_id)

    @staticmethod
    def __get_download_location__(item: Item, send_to: str) -> str:
        if send_to is None:
            send_to = "anonymous"
        relative_target_directory = os.path.join(send_to.split("@")[0].replace(".", "_").replace("-", "_"), item.id + "_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        target_directory = os.path.join(Configuration.settings.outbox_directory, relative_target_directory)
        if not os.path.exists(target_directory):
            LOGGER.info("create {}".format(target_directory))
            os.makedirs(target_directory)
        return (target_directory, relative_target_directory)

    def get_resource_id(inputs: BaseModel):
        inputs: InputDownloadProcess = InputDownloadProcess(**inputs.model_dump())
        hash_object = hashlib.sha1("/".join(list(map(lambda r: r["collection"] + r["item_id"], inputs.requests))).encode())
        return hash_object.hexdigest()

    @shared_task(bind=True, track_started=True)
    def execute(self, headers: dict[str, str], requests: list[dict[str, str]], crop_wkt: str, target_projection: str = "native", target_format: str = "native", raw_archive: bool = True) -> dict:
        (send_to, user_id) = AprocProcess.__get_user_email__(headers.get("authorization"))
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
            item: Item = AprocProcess.__get_item_from_airs__(collection=collection, item_id=item_id)
            if item is None:
                error_msg = "{}/{} not found".format(collection, item_id)
                LOGGER.error(error_msg)
                LOGGER.info("Download failed", extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", "event.reason": error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                mail_context["error"] = error_msg
                Notifications.report(None, Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                raise RegisterException(error_msg)

            driver: Driver = Drivers.solve(item)
            if driver is not None:
                try:
                    LOGGER.info("Download will be done by {}".format(driver.name))
                    __update_status__(self, state='PROGRESS', meta={"ACTION": "DOWNLOAD", "TARGET": item_id})
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
                    if Configuration.settings.outbox_s3 and Configuration.settings.outbox_s3.bucket:
                        AprocProcess.__dir2s3(target_directory, relative_target_directory, Configuration.settings.outbox_s3)
                        if Configuration.settings.clean_outbox_directory:
                            Driver.LOGGER.debug("clean {}".format(target_directory))
                            shutil.rmtree(target_directory)
                        mail_context["target_directory"] = Configuration.settings.outbox_s3.asset_http_endpoint_url.format(Configuration.settings.outbox_s3.bucket, relative_target_directory)
                    Notifications.report(item, Configuration.settings.email_subject_user, Configuration.settings.email_content_user, to=[send_to], context=mail_context, outcome="success")
                    Notifications.report(item, Configuration.settings.email_subject_admin, Configuration.settings.email_content_admin, Configuration.settings.notification_admin_emails.split(","), context=mail_context)
                    LOGGER.info("Download success", extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "success", USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                    download_locations.append(mail_context["target_directory"])
                except Exception as e:
                    error_msg = "Failed to download the item {}/{} ({})".format(collection, item_id, str(e))
                    LOGGER.info("Download failed", extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", "event.reason": error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                    LOGGER.error(error_msg)
                    LOGGER.exception(e)
                    mail_context["error"] = error_msg
                    Notifications.report(item, Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                    raise Exception(error_msg)
            else:
                error_msg = "No driver found for {}/{}".format(collection, item_id)
                LOGGER.info("Download failed", extra={EVENT_KIND_KEY: "event", EVENT_CATEGORY_KEY: "file", EVENT_TYPE_KEY: USER_ACTION_KEY, EVENT_ACTION: "download", EVENT_OUTCOME_KEY: "failure", "event.reason": error_msg, USER_ID_KEY: user_id, USER_EMAIL_KEY: send_to, EVENT_MODULE_KEY: "aproc-download", ARLAS_COLLECTION_KEY: collection, ARLAS_ITEM_ID_KEY: item_id})
                LOGGER.error(error_msg)
                mail_context["error"] = error_msg
                Notifications.report(item, Configuration.settings.email_subject_error_download, Configuration.settings.email_content_error_download, Configuration.settings.notification_admin_emails.split(","), context=mail_context, outcome="failure")
                raise DriverException(error_msg)
        return OutputDownloadProcess(download_locations=download_locations).model_dump()

    def __dir2s3(directory: str, s3_dir: str, s3_conf: S3Configuration):
        s3_client = s3.get_client_from_configuration(s3_conf)

        uploadFileNames = []
        for (sourceDir, dirname, files) in os.walk(directory):
            for file in files:
                uploadFileNames.append(os.path.join(sourceDir, file)[len(directory):])

        for key in uploadFileNames:
            local_path = os.path.join(directory, key.strip("/"))
            destpath = os.path.join(s3_dir, key.strip("/"))
            type, encpoding = mimetypes.guess_type(local_path, strict=False)
            if type:
                extra = {"ContentType": type}
            else:
                extra = None
            LOGGER.info("Copy {} ({}) to {}/{}".format(local_path, type, s3_conf.bucket, destpath))
            with open(local_path, 'rb') as file:
                s3_client.upload_fileobj(file, s3_conf.bucket, destpath, ExtraArgs=extra)

    @staticmethod
    def __get_item_from_arlas__(collection: str, item_id: str, headers: dict[str, str] = {}):
        try:
            url = Configuration.settings.arlas_url_search.format(collection=collection, item=item_id)
            r = requests.get(url=url, headers={"authorization": headers.get("authorization"), "arlas-org-filter": headers.get("arlas-org-filter")})
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

    @staticmethod
    def __get_item_from_airs__(collection: str, item_id: str):
        try:
            r = requests.get(url=os.path.join(AprocConfiguration.settings.airs_endpoint, "collections", collection, "items", item_id))
            if r.ok:
                return mapper.item_from_json(r.content)
            else:
                return None
        except Exception:
            return None

    @staticmethod
    def __update_paths__(mail_context: dict[str, str]):
        try:
            if mail_context.get("target_directory"):
                if not not Configuration.settings.email_path_prefix_add:
                    mail_context["target_directory"] = os.path.join(Configuration.settings.email_path_prefix_add, mail_context["target_directory"].removeprefix(Configuration.settings.outbox_directory).removeprefix("/"))
                if Configuration.settings.email_path_to_windows:
                    mail_context["target_directory"] = mail_context["target_directory"].replace("/", "\\")
        except Exception as e:
            LOGGER.exception(e)
        return mail_context
