from abc import ABC, abstractmethod

from airs.core.models.model import Item
from aproc.core.logger import Logger


class Driver(ABC):
    """ Driver for exporting files for download
    """
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

    @staticmethod
    @abstractmethod
    def supports(item: Item, asset_name: str) -> bool:
        """Return True if the provided url points to an archive supported by this driver.

        Args:
            url (str): archive's url

        Returns:
            bool: True if the driver supports the archive format, False otherwise
        """
        ...

    @abstractmethod
    def fetch_and_transform(self, item: Item, asset_name: str, target_directory: str, file_name: str, crop_wkt: str, target_projection: str, target_format: str):
        """ Fetch and transform the asset, given the wanted projection, format and crop. The file must be placed in the provided target directory.

        Args:
            item (Item): item containing the asset to export
            asset_name (Asset): asset's name to export (must be in the Item)
            target_directory (str): where the file must be placed
            file_name (str): name of the file to use
            crop_wkt (str): geometry to crop the raster with
            target_projection (str): target projection
            target_format (str): target format
        """
        ...
