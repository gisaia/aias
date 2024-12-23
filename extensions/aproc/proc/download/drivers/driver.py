from abc import ABC, abstractmethod

from airs.core.models.model import Item, Role
from aproc.core.logger import Logger


class Driver(ABC):
    """ Driver for exporting files for download
    """
    priority: int = 0
    name: str = None
    LOGGER = Logger.logger
    alternative_asset_href_field: str = None

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
    def supports(item: Item) -> bool:
        """Whether the driver support the item or not

        Args:
            item (Item): the item to download

        Returns:
            bool: True if supported
        """
        ...

    @staticmethod
    def get_asset_href(item: Item) -> str | None:
        if Driver.alternative_asset_href_field:
            return item.properties[Driver.alternative_asset_href_field]
        data = item.assets.get(Role.data.value)
        return data.href if data else None

    @abstractmethod
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        """ Fetch and transform the item, given the wanted projection, format and crop. The file must be placed in the provided target directory.

        Args:
            item (Item): item containing the asset to export
            target_directory (str): where the file must be placed
            crop_wkt (str): geometry to crop the raster with
            target_projection (str): target projection
            target_format (str): target format
            raw_archive (bool): if true fetch raw archive
        """
        ...
