import logging
from abc import ABC, abstractmethod

from celery import Task
from pydantic import BaseModel

from aproc.core.models.ogc import ProcessDescription, ProcessSummary


class Process(ABC):
    name: str = ""
    LOGGER = logging.getLogger(__name__)
    input_model: type[BaseModel]
    __task_name__: str = ""

    @classmethod
    def set_logger(cls, logger) -> None:
        """ Sets the driver's logger

        Args:
            logger (logger): the driver's logger
        """
        cls.LOGGER = logger

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
    def execute(self, context: dict[str, str], **kwargs) -> BaseModel:
        ...

    @staticmethod
    @abstractmethod
    def get_resource_id(inputs: BaseModel):
        ...
