import logging
from abc import ABC, abstractmethod

from pydantic import BaseModel

from aproc.core.models.ogc import ProcessDescription, ProcessSummary


class Process(ABC):
    name: str = None
    LOGGER = logging.getLogger(__name__)
    input_model: type[BaseModel]
    __task_name__: str = None

    @classmethod
    def set_logger(cls, logger) -> None:
        """ Sets the driver's logger

        Args:
            logger (logger): the driver's logger
        """
        cls.LOGGER = logger

    @staticmethod
    @abstractmethod
    def init(configuration: dict):
        ...

    @staticmethod
    @abstractmethod
    def get_process_description() -> ProcessDescription:
        ...

    @staticmethod
    @abstractmethod
    def get_process_summary() -> ProcessSummary:
        ...

    @abstractmethod
    def execute(self, **kwargs) -> BaseModel:
        ...

    @abstractmethod
    def get_ressource_id(self, inputs: BaseModel):
        ...
