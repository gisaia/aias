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
    def getProcessDescription() -> ProcessDescription:
        ...

    @staticmethod
    @abstractmethod
    def getProcessSummary() -> ProcessSummary:
        ...

    @abstractmethod
    def execute(inputs: BaseModel):
        ...