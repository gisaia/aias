import datetime
import json
import os

import requests
from celery import shared_task
from pydantic import BaseModel, Field

from aproc.core.logger import Logger
from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.execute import Execute
from aproc.core.processes.process import Process, Subscriber
from aproc.core.models.ogc.execute import Subscriber as OGCSubscriber
from aproc.core.utils import add_msg_to_text, base_model2description
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from extensions.aproc.proc.ingest.model import Archive
from extensions.aproc.proc.ingest.settings import Configuration
from extensions.aproc.proc.ingest.settings import \
    Configuration as IngestConfiguration
from extensions.aproc.proc.processes.process_model import InputProcess, OutputProcess

AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")
DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.get_logger()


class InputDirectoryIngestProcess(InputProcess):
    collection: str = Field(title="Collection name", description="Name of the collection where the items will be registered", minOccurs=1, maxOccurs=1)
    catalog: str = Field(title="Catalog name", description="Name of the catalog, within the collection, where the items will be registered", minOccurs=1, maxOccurs=1)
    directory: str = Field(title="Directory URL", description="URL pointing at a directory containing one or more archives", minOccurs=1, maxOccurs=1)
    annotations: str = Field(title="Item annotations", description="Item annotations", minOccurs=1, maxOccurs=1)
    enrichments: list[str] = Field(default=[], title="Enrichments", description="List of enrichments to apply on the item", minOccurs=0, maxOccurs=-1)


class OutputDirectoryIngestProcess(OutputProcess):
    archives: list[str] = Field(title="List of archive urls", description="URL of the archives identified in the directory and that will be ingested")


summary: ProcessSummary = ProcessSummary(
    title="Ingest all archive contained in a directory in AIRS.",
    description="Extract the items and assets information from the archives founbd in the directory and register the items and assets in ARLAS Item Registration Services.",
    keywords=["AIRS", "ARLAS Item Registration Services"],
    id="directory_ingest",
    version=AIAS_VERSION,
    jobControlOptions=[JobControlOptions.async_execute],
    outputTransmission=[TransmissionMode.reference],
    # TODO: provide the links if any => link could be the execute endpoint
    links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(exclude_none=True, exclude_unset=True),
    inputs=base_model2description(InputDirectoryIngestProcess),
    outputs=base_model2description(OutputDirectoryIngestProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            IngestConfiguration.init(configuration_file=configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME))
            DriverManager.init(summary.id, IngestConfiguration.settings.drivers)
        else:
            raise DriverException("Invalid configuration for ingest drivers ({})".format(configuration))
        AprocProcess.input_model = InputDirectoryIngestProcess
        LOGGER.info("Service configuration:")
        LOGGER.info(IngestConfiguration.settings.model_dump_json())

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    @staticmethod
    def get_resource_id(inputs: BaseModel) -> str:
        return InputDirectoryIngestProcess(**inputs.model_dump(exclude_none=True, exclude_unset=True)).directory

    @shared_task(bind=True, track_started=True)
    def execute(self, headers: dict[str, str], subscriber: dict[str, str], directory: str, collection: str, catalog: str, annotations: str, include_drivers: list[str] = [], exclude_drivers: list[str] = [], enrichments: list[str] = [], cascade_subscriber: bool = False) -> dict:
        # self is a celery task because bind=True
        """ ingest the archives contained in the directory url. Every archive ingestion becomes a new process

        Args:
            directory (str): directory containing the archives
            collection (str): target collection
            catalog (str): target catalog

        Returns:
            list: List of archives(urls) (OutputDirectoryIngestProcess)
        """
        if not directory.startswith(Configuration.settings.inputs_directory):
            msg = "Can not ingest directory {} : it is not prefixed with {}".format(directory, Configuration.settings.inputs_directory)
            LOGGER.error(msg)
            raise Exception(msg)

        archives: list[Archive] = AprocProcess.list_archives(directory, max_size=Configuration.settings.max_number_of_archive_for_ingest)
        LOGGER.info("{} archives to be ingested from {}".format(len(archives), directory))
        sub_jobs: list[str] = []
        message = ""
        for archive in archives:
            LOGGER.info(archive.model_dump_json(exclude_none=True, exclude_unset=True))
            try:
                inputs = InputIngestProcess(url=archive.path, collection=collection, catalog=catalog, annotations=annotations, include_drivers=include_drivers, exclude_drivers=exclude_drivers, enrichments=enrichments, cascade_subscriber=cascade_subscriber)
                execute = Execute(inputs=json.loads(inputs.model_dump_json(exclude_unset=True, exclude_none=True)), subscriber=OGCSubscriber(**subscriber) if cascade_subscriber else None)
                r: requests.Response = requests.post("/".join([Configuration.settings.aproc_endpoint, "processes", "ingest", "execution"]), data=json.dumps(execute.model_dump()), headers=headers)
                if not r.ok:
                    msg = "Failed to submit the ingest request for {} ({}): {}".format(archive.path, archive.id, str(r.status_code) + ":" + str(r.content))
                    LOGGER.error(msg)
                    raise Exception(msg)
                else:
                    sub_jobs.append(json.loads(r.content).get("jobID"))
                    msg = "Ingest request for {} ({}) submitted successfully".format(archive.path, archive.id)
                    message = add_msg_to_text(msg, message)
                    LOGGER.debug("Send ingestion request for {} ({}) ok".format(archive.path, archive.id))
            except Exception as e:
                msg = "Failed to submit the ingest request for {} ({}): {}".format(archive.path, archive.id, str(e))
                LOGGER.error(msg)
                LOGGER.exception(e)
                raise Exception(msg)
        return OutputDirectoryIngestProcess(process="directory_ingest", archives=[a.path for a in archives], sub_jobs=sub_jobs, message=message, error="").model_dump(exclude_none=True, exclude_unset=True)

    @staticmethod
    def list_archives(path: str, size: int = 0, max_size: int = 10) -> list[Archive]:
        if not AccessManager.exists(path):
            LOGGER.error("{} does not exist, directory/file can no be scanned to find archives".format(path))
            return []
        if size >= max_size or os.path.basename(path).startswith("."):
            return []
        driver: IngestDriver = DriverManager.solve(summary.id, path)
        if driver is not None:
            lm: float | None = AccessManager.get_last_modification_time(path)
            cd: float | None = AccessManager.get_creation_time(path)
            if lm:
                lm = datetime.datetime.fromtimestamp(lm)
            if cd:
                cd = datetime.datetime.fromtimestamp(cd)
            archive = Archive(id=driver.get_item_id(path),
                              name=os.path.basename(path),
                              driver_name=driver.name,
                              path=path,
                              is_dir=AccessManager.is_dir(path),
                              last_modification_date=lm,
                              creation_date=cd)
            return [archive]
        else:
            if AccessManager.is_dir(path):
                archives: list[Archive] = []
                for file in AccessManager.listdir(path):
                    sub_archives = AprocProcess.list_archives(file.path, size=size, max_size=max_size)
                    size = size + len(sub_archives)
                    archives = archives + sub_archives
                return archives
            else:
                # it is a file but no driver supports it, so it is not an archive.
                return []
