import importlib
import json
import os
from threading import Thread
from urllib.parse import urlparse
from datetime import datetime
from time import sleep

from celery import Celery, states
from celery.result import AsyncResult
from pydantic import BaseModel
from redis import Redis
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from aproc.core.logger import Logger
from aproc.core.models.ogc.job import JobType, StatusCode, StatusInfo, StatusInfoList
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

    def __listen_status__():
        state = APROC_CELERY_APP.events.State()

        def update_status_fct(event):
            try:
                state.event(event)
                task_id = event.get('uuid', None)
                if task_id:
                    status_info: StatusInfo = Processes.__retrieve_status_info__(task_id)
                    if status_info is None:
                        sleep(5) # task is sent before its data are stored, this means that we can get the event before we're able to retrieve it. We get here a second chance.
                        status_info: StatusInfo = Processes.__retrieve_status_info__(task_id)
                    if status_info is None:
                        LOGGER.error("Can not retrieve task {} . Its status will not be updated with this event.".format(task_id))
                    else:
                        status_info.status = Processes.__to_status_info_code__(event.get('state'))
                        status_info.updated = round(datetime.now().timestamp())
                        if status_info.status.is_final():
                            status_info.finished = round(datetime.now().timestamp())
                        if event.get('state') == states.STARTED:
                            status_info.started = round(datetime.now().timestamp())
                        status_info.message = event.get('result', status_info.message)
                        Processes.__save_status_info__(status_info)
            except Exception as e:
                LOGGER.exception(e)

        sleep_time = 0
        while True:
            try:
                with APROC_CELERY_APP.connection() as connection:
                    recv = APROC_CELERY_APP.events.Receiver(connection, handlers={
                        'task-failed': update_status_fct,
                        'task-succeeded': update_status_fct,
                        'task-sent': update_status_fct,
                        'task-received': update_status_fct,
                        'task-revoked': update_status_fct,
                        'task-started': update_status_fct,
                    }, app=APROC_CELERY_APP)
                    LOGGER.info("Capturing events for status tracking ...")
                    recv.capture(limit=None, timeout=None, wakeup=True)
            except Exception as e:
                LOGGER.error("Failed to capture events for status tracking")
                LOGGER.error(e)
                sleep_time = min(sleep_time + 5, 300)
                LOGGER.error("Sleep {} seconds and try to connect again ...".format(sleep_time))
                sleep(sleep_time)

    @staticmethod
    def init(is_service: bool = False):
        if is_service:
            Processes.__init_redis__()
        Processes.processes = []
        for configuration in Configuration.settings.processes:
            try:
                process: Process = importlib.import_module(configuration.class_name).AprocProcess
                process.name = configuration.name
                LOGGER.info("Register {} as {}".format(configuration.class_name, process.name))
                process.init(configuration.configuration)
                task = importlib.import_module(configuration.class_name).Process.execute
                process.__task_name__ = ".".join([configuration.class_name, "execute"])
                APROC_CELERY_APP.task(task)
                Processes.processes.append(process)
            except ModuleNotFoundError:
                raise ProcessException(f"Process {configuration.class_name} not found.")

        if is_service:
            Thread(target=Processes.__listen_status__).start()

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
    def result(task_id: str):
        res = AsyncResult(task_id, app=APROC_CELERY_APP)
        if res.status == states.SUCCESS:
            return res.result
        else:
            return None
        
    @staticmethod
    def execute(process_name, headers: dict[str, str], input: BaseModel = None) -> StatusInfo | BaseModel:
        LOGGER.debug("received process request {}".format(process_name))
        process: Process = Processes.get_process(process_name=process_name)
        kwargs = input.model_dump()
        kwargs["headers"] = headers
        LOGGER.debug("before_execute {}".format(process_name))
        extra = process.before_execute(**kwargs)
        kwargs.update(extra)
        LOGGER.debug("send task {}".format(process.__task_name__))
        job_id = Processes.send_task(task_name=process.__task_name__, kwargs=kwargs)
        LOGGER.debug("create and save status info")
        status_info: StatusInfo = StatusInfo(
            processID=process_name,
            type=JobType.process,
            jobID=job_id,
            resourceID=process.get_resource_id(input),
            status=StatusCode.accepted.value,
            message="",
            created=round(datetime.now().timestamp()),
            updated=round(datetime.now().timestamp()),
            started=None,
            finished=None,
            progress=None,
            links=[]
        )
        Processes.__save_status_info__(status_info)
        return Processes.status(job_id)

    @staticmethod
    def status_by_resource_id(resource_id: str) -> list[StatusInfo]:
        return Processes.__retrieve_status_info_by_resource_id__(resource_id)

    @staticmethod
    def status(task_id: str) -> StatusInfo:
        return Processes.__retrieve_status_info__(task_id)

    @staticmethod
    def list_jobs(offset: int = 0, limit: int = 100, process_id: str = None, status: str = None) -> StatusInfoList:
        return Processes.__retrieve_status_info_list__(offset, limit, process_id, status)

    def __save_status_info__(status_info: StatusInfo):
        Processes.__get_redis_client__().json().set(Processes.__REDIS_PREFIX__ + status_info.jobID, "$",
                                                    {"job_id": status_info.jobID,
                                                     "process_id": status_info.processID,
                                                     "resource_id": status_info.resourceID,
                                                     "modification_date": status_info.updated,
                                                     "started_date": status_info.started,
                                                     "finished_date": status_info.finished,
                                                     "creation_date": status_info.created,
                                                     "status": status_info.status.value,
                                                     "message": status_info.message})

    def __retrieve_status_info__(job_id) -> StatusInfo:
        return Processes.__to_status_info__(Processes.__get_redis_client__().json().get(Processes.__REDIS_PREFIX__ + job_id))

    def __retrieve_status_info_by_resource_id__(resource_id: str) -> list[StatusInfo]:
        docs = Processes.__get_redis_client__().ft("idx:airs_jobs").search(query="@resource_id:{'" + resource_id.replace("-", "\\-") + "'}").docs
        return list(map(lambda d: Processes.__to_status_info__(json.loads(d.json)), docs))

    def __retrieve_status_info_list__(offset: int = 0, limit: int = 100, process_id: str = None, status: str = None) -> StatusInfoList:
        query_str = ""
        if process_id:
            query_str = "@process_id:{'" + process_id + "'}"
        if status:
            query_str = query_str + " @status:{'" + status + "'}"
        if (not process_id) and (not status):
            query_str = "*"
        q = Query(query_str).paging(offset=offset, num=limit).sort_by("modification_date", asc=False)
        r = Processes.__get_redis_client__().ft("idx:airs_jobs").search(q)
        return StatusInfoList(total=r.total, status_list=list(map(lambda d: Processes.__to_status_info__(json.loads(d.json)), r.docs)))

    def __to_status_info__(o: dict) -> StatusInfo:
        if o:
            return StatusInfo(
                processID=o.get("process_id", None),
                type=JobType.process,
                jobID=o.get("job_id", None),
                status=StatusCode[o.get("status", StatusCode.accepted.value)],
                message=o.get("message", None),
                created=o.get("creation_date", None),
                started=o.get("started_date", None),
                finished=o.get("finished_date", None),
                updated=o.get("modification_date", None),
                progress=None,
                resourceID=o.get("resource_id", None)
            )
        else:
            return None

    def __to_status_info_code__(code: states) -> StatusCode:
        status_code = StatusCode.accepted
        if code == states.EXCEPTION_STATES:
            status_code = StatusCode.failed

        if code == states.RECEIVED:
            status_code = StatusCode.accepted

        if code == states.PENDING:
            status_code = StatusCode.accepted

        if code == states.REVOKED:
            status_code = StatusCode.dismissed

        if code == states.REJECTED:
            status_code = StatusCode.dismissed

        if code == states.STARTED:
            status_code = StatusCode.running

        if code == states.RETRY:
            status_code = StatusCode.accepted

        if code == states.FAILURE:
            status_code = StatusCode.failed

        if code == states.SUCCESS:
            status_code = StatusCode.successful
        return status_code


    def __init_redis__():
        # At startup we clear and recreate the index.
        try:
            Processes.__get_redis_client__().ft("idx:airs_jobs").dropindex()
        except :
            ...
        schema = (
            TagField("$.process_id", as_name="process_id"),
            TagField("$.job_id", as_name="job_id"),
            TagField("$.resource_id", as_name="resource_id"),
            NumericField("$.creation_date", as_name="creation_date"),
            NumericField("$.started_date", as_name="started_date"),
            NumericField("$.modification_date", as_name="modification_date"),
            NumericField("$.finished_date", as_name="finished_date"),
            TagField("$.status", as_name="status"),
            TextField("$.message", as_name="message")
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
