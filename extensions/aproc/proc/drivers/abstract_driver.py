from abc import ABC, abstractmethod
from aproc.core.logger import Logger


class AbstractDriver(ABC):

    def __init__(self):
        self.priority: int = 0
        self.name: str = ""
        self.LOGGER = Logger.logger
        self.assets_dir: str = ""

    @abstractmethod
    def init(self, configuration: dict) -> None:
        """Method called at init time by the service.

        Args:
            configuration (dict): Driver's configuration
        """
        ...

    @abstractmethod
    def supports(self, ressource) -> bool:
        """Return True if the provided url points to an archive supported by this driver.

        Args:
            url (str): archive's url

        Returns:
            bool: True if the driver supports the archive format, False otherwise
        """
        ...
