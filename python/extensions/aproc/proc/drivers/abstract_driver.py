from abc import ABC, abstractmethod
from typing import Any
from aproc.core.logger import Logger


class AbstractDriver(ABC):
    priority: int = 0
    name: str = ""
    LOGGER = Logger.logger
    assets_dir: str = ""

    def __init__(self):
        ...

    @staticmethod
    @abstractmethod
    def init(configuration: dict) -> None:
        """Method called at init time by the service.

        Args:
            configuration (dict): Driver's configuration
        """
        ...

    @abstractmethod
    def supports(self, resource, extra_params: dict[str, Any] = {}) -> bool:
        """Return True if the provided url points to an archive supported by this driver.

        Args:
            resource (str): archive's url

        Returns:
            bool: True if the driver supports the archive format, False otherwise
        """
        ...
