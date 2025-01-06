from abc import abstractmethod

from airs.core.models.model import Item, Role
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver


class DownloadDriver(AbstractDriver):
    """ Driver for exporting files for download
    """

    def __init__(self):
        super().__init__()
        self.alternative_asset_href_field: str = None

    def init(self, configuration: dict) -> None:
        self.alternative_asset_href_field = configuration.get("alternative_asset_href_field")

    def get_asset_href(self, item: Item) -> str | None:
        if self.alternative_asset_href_field:
            return item.properties[self.alternative_asset_href_field]
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
