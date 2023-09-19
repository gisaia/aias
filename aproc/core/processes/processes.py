import importlib
import os

from celery import Celery, states
from celery.result import AsyncResult
from aproc.core.logger import Logger
from pydantic import BaseModel

from aproc.core.models.ogc.job import JobType, StatusCode, StatusInfo
from aproc.core.processes.exception import ProcessException
from aproc.core.processes.process import Process
from aproc.core.settings import Configuration

LOGGER = Logger.get_logger()
LOGGER.info("Loading configuration {}".format(os.environ.get("APROC_CONFIGURATION_FILE")))
Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))

APROC_CELERY_APP = Celery(name='aproc', broker=Configuration.settings.celery_broker_url, backend=Configuration.settings.celery_result_backend)


class Processes:
    processes: list[Process] = []

    @staticmethod
    def init():
        Processes.processes = []
        for configuration in Configuration.settings.processes:
            try:
                process: Process = importlib.import_module(configuration.class_name).Process
                process.name = configuration.name
                LOGGER.info("Register {} as {}".format(configuration.class_name,  process.name))
                process.init(configuration.configuration)
                Processes.processes.append(process)
                task = importlib.import_module(configuration.class_name).Process.execute
                process.__task_name__ = ".".join([configuration.class_name, "execute"])
                APROC_CELERY_APP.task(task)
            except ModuleNotFoundError:
                raise ProcessException(f"Process {configuration.class_name} not found.")

    @staticmethod
    def get_process(process_name: str) -> Process:
        for p in Processes.processes:
            if p.name == process_name:
                return p
        raise ProcessException(f"Process {process_name} not found.")

    @staticmethod
    def send_task(task_name: str, kwargs: dict) -> str:
        job: AsyncResult = APROC_CELERY_APP.send_task(name=task_name, kwargs=kwargs)
        return job.task_id

    @staticmethod
    def status(task_id: str) -> StatusInfo:
        res = AsyncResult(task_id, app=APROC_CELERY_APP)

        status_code = StatusCode.accepted
        if res.state == states.EXCEPTION_STATES:
            status_code = StatusCode.failed

        if res.state == states.RECEIVED:
            status_code = StatusCode.accepted

        if res.state == states.PENDING:
            status_code = StatusCode.accepted

        if res.state == states.REVOKED:
            status_code = StatusCode.dismissed

        if res.state == states.REJECTED:
            status_code = StatusCode.dismissed

        if res.state == states.STARTED:
            status_code = StatusCode.running

        if res.state == states.RETRY:
            status_code = StatusCode.accepted

        if res.state == states.FAILURE:
            status_code = StatusCode.failed

        if res.state == states.SUCCESS:
            status_code = StatusCode.successful

            # TODO: find a way to retrieve the task name (it's not in the AsyncResult)
        return StatusInfo(processID="UNKNOWN", jobID=task_id, status=status_code, type=JobType.process)

    @staticmethod
    def execute(process_name, input: BaseModel = None) -> StatusInfo | BaseModel:
        return Processes.status(Processes.send_task(task_name=Processes.get_process(process_name=process_name).__task_name__, kwargs=input.model_dump()))


Processes.init()
