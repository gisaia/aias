import importlib
import json
import os
from itertools import chain
from urllib.parse import urlparse

from celery import Celery, states
from celery.result import AsyncResult
from pydantic import BaseModel
from redis import Redis, ResponseError
from redis.commands.json.path import Path
from redis.commands.search.document import Document
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Filter, NumericFilter, Query

from aproc.core.logger import Logger
from aproc.core.models.ogc.job import JobType, StatusCode, StatusInfo
from aproc.core.processes.exception import ProcessException
from aproc.core.processes.process import Process
from aproc.core.settings import Configuration

LOGGER = Logger.logger
LOGGER.info("Loading configuration {}".format(os.environ.get("APROC_CONFIGURATION_FILE")))
Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))
APROC_CELERY_APP = Celery(name='aproc', broker=Configuration.settings.celery_broker_url, backend=Configuration.settings.celery_result_backend)


class Processes:
    processes: list[Process] = []
    __REDIS_PREFIX__ = "airs_job_id:"
    __REDIS_CONNECTION__: Redis = None

    @staticmethod
    def init():
        Processes.__init_redis__()
        Processes.processes = []
        for configuration in Configuration.settings.processes:
            try:
                process: Process = importlib.import_module(configuration.class_name).AprocProcess
                process.name = configuration.name
                LOGGER.info("Register {} as {}".format(configuration.class_name,  process.name))
                print("Register {} as {}".format(configuration.class_name,  process.name))
                process.init(configuration.configuration)
                task = importlib.import_module(configuration.class_name).Process.execute
                process.__task_name__ = ".".join([configuration.class_name, "execute"])
                APROC_CELERY_APP.task(task)
                Processes.processes.append(process)
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
    def status_by_resource_id(resource_id: str) -> list[StatusInfo]:
        jobs = Processes.__retrieve_job_by_resource_id__(resource_id)
        return list(map(lambda j: Processes.status(j["job_id"]), jobs))
    
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
        
        status = StatusInfo(jobID=task_id, status=status_code, type=JobType.process)
        job = Processes.__retrieve_job__(task_id)
        status.resourceID = job["resource_id"]
        status.processID = job["process_id"]
        return status

    @staticmethod
    def result(task_id: str):
        res = AsyncResult(task_id, app=APROC_CELERY_APP)
        if res.status == states.SUCCESS:
            return res.result
        else:
            return None
        
    @staticmethod
    def list_jobs() -> list[str]:
        list_of_list_of_jobs = list(APROC_CELERY_APP.control.inspect().reserved().values()) + list(APROC_CELERY_APP.control.inspect().active().values())
        return list(map(lambda job: job["id"], [item for sublist in list_of_list_of_jobs for item in sublist]))

    @staticmethod
    def execute(process_name, headers: dict[str, str], input: BaseModel = None) -> StatusInfo | BaseModel:
        process: Process = Processes.get_process(process_name=process_name)
        kwargs = input.model_dump()
        kwargs["headers"] = headers
        job_id = Processes.send_task(task_name=process.__task_name__, kwargs=kwargs)
        Processes.__store_job__(job_id, process_name, process.get_resource_id(input))
        return Processes.status(job_id)

    def __store_job__(job_id, process_id, resource_id):
        Processes.__get_redis_client__().json().set(Processes.__REDIS_PREFIX__+job_id, "$",  {"job_id": job_id,  "process_id": process_id, "resource_id": resource_id})

    def __retrieve_job__(job_id):
        return Processes.__get_redis_client__().json().get(Processes.__REDIS_PREFIX__+job_id)

    def __retrieve_job_by_resource_id__(resource_id) -> list:
        docs = Processes.__get_redis_client__().ft("idx:airs_jobs").search(query="@resource_id:{'"+resource_id+"'}").docs
        return list(map(lambda d: json.loads(d.json), docs))

    def __init_redis__():
        try:
            rs = Processes.__get_redis_client__().ft("idx:airs_jobs").info()
        except ResponseError:
            schema = (
                TagField("$.process_id", as_name="process_id"),
                TagField("$.job_id", as_name="job_id"),
                TagField("$.resource_id", as_name="resource_id")
            )
            rs = Processes.__get_redis_client__().ft("idx:airs_jobs")
            rs.create_index(schema,
                            definition=IndexDefinition(
                                prefix=[Processes.__REDIS_PREFIX__],
                                index_type=IndexType.JSON
                                )
                            )

    def __get_redis_client__() -> Redis:
        if Processes.__REDIS_CONNECTION__ is None:
            uri = urlparse(Configuration.settings.celery_result_backend)
            if uri.scheme == "redis":
                Processes.__REDIS_CONNECTION__ = Redis(host=uri.hostname, port=uri.port, decode_responses=True)
            else:
                raise Exception("Unsupported backend {}".format(uri.scheme))
        return Processes.__REDIS_CONNECTION__


Processes.init()
