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
from aproc.core.processes.process import Process as Process
from aproc.core.utils import base_model2description
from extensions.aproc.proc.ingest.drivers.drivers import Drivers
from extensions.aproc.proc.ingest.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.ingest_process import InputIngestProcess
from extensions.aproc.proc.ingest.model import Archive
from extensions.aproc.proc.ingest.settings import Configuration

DRIVERS_CONFIGURATION_FILE_PARAM_NAME = "drivers"
LOGGER = Logger.logger


class InputDirectoryIngestProcess(BaseModel):
    collection: str = Field(title="Collection name", description="Name of the collection where the items will be registered", minOccurs=1, maxOccurs=1)
    catalog: str = Field(title="Catalog name", description="Name of the catalog, within the collection, where the items will be registered", minOccurs=1, maxOccurs=1)
    directory: str = Field(title="Directory URL", description="URL pointing at a directory containing one or more archives", minOccurs=1, maxOccurs=1)
    annotations: str = Field(title="Item annotations", description="Item annotations", minOccurs=1, maxOccurs=1)


class OutputDirectoryIngestProcess(BaseModel):
    archives: list[str] = Field(title="List of archive urls", description="URL of the archives identified in the directory and that will be ingested")


summary: ProcessSummary = ProcessSummary(
    title="Ingest all archive contained in a directory in AIRS.",
    description="Extract the items and assets information from the archives founbd in the directory and register the items and assets in ARLAS Item Registration Services.",
    keywords=["AIRS", "ARLAS Item Registration Services"],
    id="directory_ingest",
    version="0.1",
    jobControlOptions=[JobControlOptions.async_execute],
    outputTransmission=[TransmissionMode.reference],
    # TODO: provide the links if any => link could be the execute endpoint
    links=[]
)

description: ProcessDescription = ProcessDescription(
    **summary.model_dump(),
    inputs=base_model2description(InputDirectoryIngestProcess),
    outputs=base_model2description(OutputDirectoryIngestProcess)
)


class AprocProcess(Process):

    @staticmethod
    def init(configuration: dict):
        if configuration.get(DRIVERS_CONFIGURATION_FILE_PARAM_NAME):
            Drivers.init(configuration_file=configuration[DRIVERS_CONFIGURATION_FILE_PARAM_NAME])
        else:
            raise DriverException("Invalid configuration for ingest drivers ({})".format(configuration))
        AprocProcess.input_model = InputDirectoryIngestProcess

    @staticmethod
    def get_process_description() -> ProcessDescription:
        return description

    @staticmethod
    def get_process_summary() -> ProcessSummary:
        return summary

    def get_resource_id(inputs: BaseModel):
        return InputDirectoryIngestProcess(**inputs.model_dump()).directory

    @shared_task(bind=True, track_started=True)
    def execute(self, headers: dict[str, str], directory: str, collection: str, catalog: str, annotations: str) -> dict:
        # self is a celery task because bind=True
        """ ingest the archives contained in the directory url. Every archive ingestion becomes a new process

        Args:
            directory (str): directory containing the archives
            collection (str): target collection
            catalog (str): target catalog

        Returns:
            list: List of archives(urls) (OutputDirectoryIngestProcess)
        """
        archives: list[Archive] = AprocProcess.list_archives(Configuration.settings.inputs_directory, directory, max_size=Configuration.settings.max_number_of_archive_for_ingest)
        LOGGER.info("{} archives to be ingested from {}".format(len(archives), os.path.join(Configuration.settings.inputs_directory, directory)))
        for archive in archives:
            LOGGER.info(archive.model_dump_json())
            try:
                inputs = InputIngestProcess(url=os.path.join(Configuration.settings.inputs_directory, archive.path), collection=collection, catalog=catalog, annotations=annotations)
                execute = Execute(inputs=inputs.model_dump())
                r = requests.post("/".join([Configuration.settings.aproc_endpoint, "processes", "ingest", "execution"]), data=json.dumps(execute.model_dump()), headers=headers)
                if not r.ok:
                    msg = "Failed to submit the ingest request for {} ({}): {}".format(archive.path, archive.id, str(r.status_code) + ":" + str(r.content))
                    LOGGER.error(msg)
                    raise Exception(msg)
                else:
                    LOGGER.debug("Send ingestion request for {} ({}) ok".format(archive.path, archive.id))
            except Exception as e:
                msg = "Failed to submit the ingest request for {} ({}): {}".format(archive.path, archive.id, str(e))
                LOGGER.error(msg)
                LOGGER.exception(e)
                raise Exception(msg)
        return list(map(lambda a: a.model_dump(), archives))

    def list_archives(prefix: str, path: str, size: int = 0, max_size: int = 10) -> list[Archive]:
        full_path = os.path.join(prefix, path)
        if not os.path.exists(full_path):
            LOGGER.error("{} does not exist, directory/file can no be scanned to find archives")
            return []
        if size >= max_size or os.path.basename(path).startswith("."):
            return []
        driver = Drivers.solve(full_path)
        if driver is not None:
            archive = Archive(id=driver.get_item_id(full_path),
                              name=os.path.basename(path),
                              driver_name=driver.name,
                              path=path,
                              is_dir=os.path.isdir(full_path),
                              last_modification_date=datetime.datetime.fromtimestamp(os.path.getmtime(full_path)),
                              creation_date=datetime.datetime.fromtimestamp(os.path.getctime(full_path)))
            return [archive]
        else:
            if os.path.isdir(full_path):
                archives: list[Archive] = []
                for file in os.listdir(full_path):
                    sub_archives = AprocProcess.list_archives(prefix, os.path.join(path, file), size=size, max_size=max_size)
                    size = size + len(sub_archives)
                    archives = archives + sub_archives
                return archives
            else:
                # it is a file but no driver supports it, so it is not an archive.
                return []
