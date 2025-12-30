import importlib
import json
import os
from datetime import datetime
from threading import Thread
from time import sleep
from urllib.parse import urlparse

from celery import Celery, Task, states
from celery.result import AsyncResult
from pydantic import BaseModel
from redis import Redis
from redis.sentinel import Sentinel
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from celery.signals import task_postrun, task_prerun

from celery.signals import Signal
import requests

from aias_common.access.manager import AccessManager
from airs.core.models.mapper import serialize_datetime
from aproc.core.logger import Logger
from aproc.core.models.ogc.job import (JobType, StatusCode, StatusInfo,
                                       StatusInfoList)
from aproc.core.processes.exception import ProcessException
from aproc.core.processes.process import InputProcess, Process, Subscriber
from aproc.core.settings import DEFAULT_PROCESS_QUEUE_NAME, Configuration

LOGGER = Logger.logger
LOGGER.info("Loading configuration {}".format(os.environ.get("APROC_CONFIGURATION_FILE")))
Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))
AccessManager.init(Configuration.settings.access_manager)

LOGGER.debug("Celery broker: {}".format(Configuration.settings.celery_broker_url))
LOGGER.debug("Celery backend: {}".format(Configuration.settings.celery_result_backend))
LOGGER.debug("Celery backend transport options: {}".format(Configuration.settings.celery_result_backend_transport_options))

APROC_CELERY_APP = Celery(
    name='aproc',
    broker=Configuration.settings.celery_broker_url,
    backend=Configuration.settings.celery_result_backend,
    result_backend_transport_options=Configuration.settings.celery_result_backend_transport_options)

APROC_JOBS_INDEX="idx:aproc_jobs"

class Processes:
    processes: list[Process] = []
    __REDIS_PREFIX__ = "airs_job_id:"

    @staticmethod
    def __update_satus(task_id: str, new_status: str, result, message: str, subscriber: Subscriber = Subscriber()):
        if new_status:
            status_info: StatusInfo = Processes.__retrieve_status_info__(task_id)
            if status_info is None:
                sleep(5)  # task is sent before its data are stored, this means that we can get the event before we're able to retrieve it. We get here a second chance.
                status_info = Processes.__retrieve_status_info__(task_id)
            if status_info :
                if status_info.status is None or not status_info.status.is_final():
                    status_info.status = Processes.__to_status_info_code__(new_status)
                    status_info.updated = round(datetime.now().timestamp())
                    if status_info.status.is_final():
                        status_info.finished = round(datetime.now().timestamp())
                        if new_status == states.SUCCESS:
                            status_info.message = json.dumps(result, default=serialize_datetime, indent=2)
                        else:
                            status_info.message = str(result)
                    Processes.__save_status_info__(status_info)
                    LOGGER.debug(f"Task {task_id} updated to status {status_info.status}")
                    if status_info.status.is_final():
                        if new_status == states.SUCCESS and subscriber.successUri:
                            Processes.__notify(subscriber.successUri.replace("{jobID}", task_id), json.dumps(result, default=serialize_datetime, indent=2))
                        if new_status == states.FAILURE and subscriber.failedUri:
                            result = Processes.result(task_id)
                            Processes.__notify(subscriber.failedUri.replace("{jobID}", task_id), status_info.model_dump_json(exclude_none=True, exclude_unset=True))
                    LOGGER.debug(f"Status after update of {task_id}: {Processes.__retrieve_status_info__(task_id).model_dump_json()  }")
                else:
                    LOGGER.debug(f"Status of {task_id} is already final ({status_info.status}). No update to {new_status} performed.")
        else:
            LOGGER.warning(f"Status info is not found for task {task_id}. No update performed.")        
        

    @staticmethod
    @task_prerun.connect
    def before_run_task(task_id: str = "", **kwargs):
        if task_id:
            s = Processes.__subscriber_from_kwargs(kwargs)
            Processes.__update_satus(task_id, states.STARTED, None, "", s)

    @staticmethod
    @task_postrun.connect
    def after_run_task(task_id: str = "", state: str = "", retval=None, **kwargs):
        if task_id and state:
            s = Processes.__subscriber_from_kwargs(kwargs)
            Processes.__update_satus(task_id, state, retval, "", s)

    @staticmethod
    def __listen_status__():
        state = APROC_CELERY_APP.events.State()

        def update_status_from_event_fct(event):
            try:
                state.event(event)
                task_id = event.get('uuid', None)
                if task_id:
                    status_info: StatusInfo = Processes.__retrieve_status_info__(task_id)
                    if status_info is None:
                        sleep(5)  # task is sent before its data are stored, this means that we can get the event before we're able to retrieve it. We get here a second chance.
                        status_info: StatusInfo = Processes.__retrieve_status_info__(task_id)
                    if status_info is None:
                        LOGGER.warn("Can not retrieve task {} . Its status will not be updated with this event.".format(task_id))
                    else:
                        Processes.__update_satus(task_id, event.get('state'), None, "")
                else:
                    LOGGER.warn("Task id not found in event {}".format(event))
            except Exception as e:
                LOGGER.error("STATUS UPDATE ERROR !!!")
                LOGGER.exception(e)

        sleep_time = 0
        while True:
            try:
                with APROC_CELERY_APP.connection() as connection:
                    recv = APROC_CELERY_APP.events.Receiver(connection, handlers={
                        'task-sent': update_status_from_event_fct,
                        'task-revoked': update_status_from_event_fct,
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
    def __notify(subscriber: str, result):
        try:
            LOGGER.debug(f"notify {subscriber} with result {result}")
            r = requests.post(url=subscriber, data=result, timeout=Configuration.settings.subscriber_post_timeout)
            if r.status_code >= 200 and r.status_code < 300:
                LOGGER.debug(f"notified {subscriber} successfully")
            else:
                LOGGER.warning(f"Notification post to {subscriber} returned status code {r.status_code}, response: {r.content}")
        except Exception as e:
            LOGGER.error(f"can not notify {subscriber}")
            LOGGER.exception(e)

    @staticmethod
    def __subscriber_from_kwargs(kwargs) -> Subscriber:
        if kwargs is not None and type(kwargs) is dict:
            inputs: dict = kwargs.get("kwargs")
            if inputs is not None:
                ip = InputProcess(**inputs)
                if ip is not None and ip.subscriber is not None:
                    return ip.subscriber
        return Subscriber()

    @staticmethod
    def init(is_service: bool = False):
        if is_service:
            Processes.__init_redis__()
        Processes.processes = []
        queue_names = set()
        queue_names.add(DEFAULT_PROCESS_QUEUE_NAME)
        for configuration in Configuration.settings.processes:
            if not configuration.enabled:
                LOGGER.info("Process {} is disabled. Skipping its registration.".format(configuration.name))
            else:
                try:
                    process: Process = importlib.import_module(configuration.class_name).AprocProcess
                    process.name = configuration.name
                    LOGGER.info("Register {} as {}".format(configuration.class_name, process.name))
                    process.init(configuration.configuration)
                    if configuration.queue_name:
                        process.queue_name = configuration.queue_name
                        queue_names.add(process.queue_name)
                    task = importlib.import_module(configuration.class_name).Process.execute
                    process.__task_name__ = ".".join([configuration.class_name, "execute"])
                    APROC_CELERY_APP.task(task)
                    Processes.processes.append(process)
                except ModuleNotFoundError:
                    raise ProcessException(f"Process {configuration.class_name} not found.")
        LOGGER.info("Configured queues: {}".format(", ".join(queue_names)))
        if is_service:
            Thread(target=Processes.__listen_status__).start()

    @staticmethod
    def get_process(process_name: str) -> Process:
        for p in Processes.processes:
            if p.name == process_name:
                return p
        raise ProcessException(f"Process {process_name} not found.")

    @staticmethod
    def send_task(task_name: str, queue_name: str, kwargs: dict) -> str:
        job: AsyncResult = APROC_CELERY_APP.send_task(name=task_name, queue=queue_name, kwargs=kwargs)
        return job.task_id

    @staticmethod
    def result(task_id: str):
        res = AsyncResult(task_id, app=APROC_CELERY_APP)
        if res.status == states.SUCCESS:
            return res.result
        else:
            return None

    @staticmethod
    def interrupt(task_id: str):
        res = AsyncResult(task_id, app=APROC_CELERY_APP)
        res.revoke(terminate=True, signal='SIGKILL')
        return Processes.__retrieve_status_info__(task_id)

    @staticmethod
    def execute(process_name, headers: dict[str, str], input: InputProcess = None) -> StatusInfo | BaseModel:
        LOGGER.debug("received process request {}".format(process_name))
        process: Process = Processes.get_process(process_name=process_name)
        kwargs = input.model_dump(exclude_none=True, exclude_unset=True)
        kwargs["headers"] = headers
        LOGGER.debug("before_execute {}".format(process_name))
        extra = process.before_execute(**kwargs)
        kwargs.update(extra)
        LOGGER.debug("send task {} on {}".format(process.__task_name__, process.queue_name))
        job_id = Processes.send_task(task_name=process.__task_name__, queue_name=process.queue_name, kwargs=kwargs)
        LOGGER.debug("create and save status info")
        status_info: StatusInfo = StatusInfo(
            processID=process_name,
            type=JobType.process,
            jobID=job_id,
            resourceID=process.get_resource_id(input),
            status=StatusCode.accepted,
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

    @staticmethod
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

    @staticmethod
    def __retrieve_status_info__(job_id) -> StatusInfo:
        return Processes.__to_status_info__(Processes.__get_redis_client__().json().get(Processes.__REDIS_PREFIX__ + job_id))

    @staticmethod
    def __retrieve_status_info_by_resource_id__(resource_id: str) -> list[StatusInfo]:
        docs = Processes.__get_redis_client__().ft(APROC_JOBS_INDEX).search(query="@resource_id:{'" + resource_id.replace("-", "\\-") + "'}").docs
        return list(map(lambda d: Processes.__to_status_info__(json.loads(d.json)), docs))

    @staticmethod
    def __retrieve_status_info_list__(offset: int = 0, limit: int = 100, process_id: str = None, status: str = None) -> StatusInfoList:
        query_str = ""
        if process_id:
            query_str = "@process_id:{'" + process_id + "'}"
        if status:
            query_str = query_str + " @status:{'" + status + "'}"
        if (not process_id) and (not status):
            query_str = "*"
        q = Query(query_str).paging(offset=offset, num=limit).sort_by("modification_date", asc=False)
        r = Processes.__get_redis_client__().ft(APROC_JOBS_INDEX).search(q)
        return StatusInfoList(total=r.total, status_list=list(map(lambda d: Processes.__to_status_info__(json.loads(d.json)), r.docs)))

    @staticmethod
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

    @staticmethod
    def __to_status_info_code__(code: str) -> StatusCode:
        match code:
            case states.RECEIVED:
                status_code = StatusCode.accepted
            case states.PENDING:
                status_code = StatusCode.accepted
            case states.REVOKED:
                status_code = StatusCode.dismissed
            case states.REJECTED:
                status_code = StatusCode.dismissed
            case states.STARTED:
                status_code = StatusCode.running
            case states.RETRY:
                status_code = StatusCode.accepted
            case states.FAILURE:
                status_code = StatusCode.failed
            case states.SUCCESS:
                status_code = StatusCode.successful
            case _:
                status_code = StatusCode.accepted
        return status_code

    @staticmethod
    def __init_redis__():
        # At startup we clear and recreate the index.
        try:
            Processes.__get_redis_client__().ft(APROC_JOBS_INDEX).dropindex()
        except Exception:
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
        rs = Processes.__get_redis_client__().ft(APROC_JOBS_INDEX)
        try:
            rs.create_index(schema,
                            definition=IndexDefinition(
                                prefix=[Processes.__REDIS_PREFIX__],
                                index_type=IndexType.JSON
                            )
                            )
        except Exception as e:
            LOGGER.error("Index not created ({})".format(e))

    @staticmethod
    def __get_redis_client__() -> Redis:
        uri = urlparse(Configuration.settings.celery_result_backend)
        if uri.scheme == "redis":
            params = {
                "host": uri.hostname,
                "port": uri.port,
                "decode_responses": True
            }
            if uri.username:
                params["username"] = uri.username
            if uri.password:
                params["password"] = uri.password
            return Redis(**params)
        elif uri.scheme == "sentinel":
            celery_result_backend_transport_options = Configuration.settings.celery_result_backend_transport_options
            if celery_result_backend_transport_options is None or celery_result_backend_transport_options.get("master_name") is None:
                raise ConnectionError("Invalid configuration: master_name and sentinel_password must be provided")
            sentinel_kwargs = celery_result_backend_transport_options.get("sentinel_kwargs")
            sentinels: list[tuple[str, int]] = [(urlparse(s).hostname, urlparse(s).port) for s in Configuration.settings.celery_result_backend.split(";")]
            host, port = Sentinel(sentinels, sentinel_kwargs=celery_result_backend_transport_options.get("sentinel_kwargs")).discover_master(Configuration.settings.celery_result_backend_transport_options.get("master_name"))
            con = {
                "host": host,
                "port": port,
                "decode_responses": True,
            }
            pwd = celery_result_backend_transport_options.get("sentinel_kwargs", {}).get("password")
            if pwd:
                con["password"] = pwd
            return Redis(**con)
        else:
            raise Exception("Unsupported backend {}".format(uri.scheme))

Processes.init()
