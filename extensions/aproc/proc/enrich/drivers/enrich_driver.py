from abc import abstractmethod
import hashlib
import os
from airs.core.models.model import Asset, Item, Role
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver


class EnrichDriver(AbstractDriver):
    alternative_asset_href_field = None

    def __init__(self):
        super().__init__()
        self.thumbnail_size = 256
        self.overview_size = 1024

    @staticmethod
    def init(configuration: dict) -> None:
        if configuration:
            EnrichDriver.alternative_asset_href_field = configuration.get("alternative_asset_href_field")

    def get_assets_dir(self, url: str) -> str:
        """Provides the directory for storing the assets

        Args:
            url (str): the original url

        Returns:
            str: the directory for storing the assets
        """
        unique = hashlib.md5(url.encode("utf-8")).hexdigest()
        assets_dir = os.path.sep.join([self.assets_dir, unique])

        AccessManager.makedir(self.assets_dir)
        AccessManager.makedir(assets_dir)
        return assets_dir

    def get_asset_filepath(self, url: str, asset: Asset) -> str:
        """Provides the name of the file for storing the asset

        Args:
            url (str): the original url
            asset (Asset): the asset to be stored, it's name must be provided.

        Returns:
            str: the path to the file for storing the asset's file
        """
        assets_dir = self.get_assets_dir(url)
        return os.path.sep.join([assets_dir, asset.name])

    def get_asset_href(self, item: Item) -> str | None:
        if self.alternative_asset_href_field:
            return item.properties[self.alternative_asset_href_field]
        data = item.assets.get(Role.data.value)
        return data.href if data else None

    @abstractmethod
    def create_asset(self, item: Item, asset_type: str) -> tuple[Asset, str]:
        """Create the asset metadata (Asset) and data (file) for a given item

        Args:
            item (Item): The item to be enriched
            asset_type (str): name of the asset type to create, e.g. 'cog'

        Returns:
            tuple[Asset, str]: a tuple containing the Asset metadata and the file location
        """
        ...
