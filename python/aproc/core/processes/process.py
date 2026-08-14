import logging
from abc import ABC, abstractmethod

from celery import Task
from pydantic import BaseModel, Field

from aproc.core.models.ogc import ProcessDescription, ProcessSummary
from aproc.core.models.ogc.execute import Subscriber
from aproc.core.settings import DEFAULT_PROCESS_QUEUE_NAME
from aproc.core.logger import Logger


class InputProcess(BaseModel):
    subscriber: Subscriber = Field(default=Subscriber(), title="Subscriber to be notified of success, progress and failure")


class Process(ABC):
    name: str = ""
    queue_name: str = DEFAULT_PROCESS_QUEUE_NAME
    LOGGER = Logger.get_logger()
    input_model: type[InputProcess]
    __task_name__: str = ""

    @staticmethod
    def update_task_status(LOGGER: logging.Logger, task: Task, state: str, meta: dict = {}):
        if task.request.id is not None:
            task.update_state(state=state, meta=meta)
        else:
            LOGGER.debug(task.name + " " + state + " " + str(meta))

    @staticmethod
    @abstractmethod
    def init(configuration: dict):
        ...

    @staticmethod
    def before_execute(**kwargs) -> dict[str, str]:
        return {}

    @staticmethod
    @abstractmethod
    def get_process_description() -> ProcessDescription:
        ...

    @staticmethod
    @abstractmethod
    def get_process_summary() -> ProcessSummary:
        ...

    @abstractmethod
    def execute(self, context: dict[str, str], subscriber: dict[str, str], sub_jobs_subscriber: dict | None, cascade_subscriber: bool, **kwargs) -> BaseModel:
        ...

    @staticmethod
    @abstractmethod
    def get_resource_id(inputs: BaseModel) -> str:
        ...
