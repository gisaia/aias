from abc import ABC, abstractmethod
from aproc.core.logger import Logger


class Driver(ABC):
    priority: int = 0
    name: str = None
    LOGGER = Logger.logger

    @staticmethod
    @abstractmethod
    def init(configuration: dict) -> None:
        """Method called at init time by the service.

        Args:
            configuration (dict): Driver's configuration
        """
        ...
