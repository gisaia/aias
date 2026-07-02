from abc import abstractmethod
import hashlib
import os
from typing import Any
from airs.core.models.model import Asset, Item, Role
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver


class EnrichDriver(AbstractDriver):

    def __init__(self):
        super().__init__()
        self.thumbnail_size = 256
        self.overview_size = 1024

    def supports_format(self, resource: Item, extra_params: dict[str, Any], supported_assets: list[str]) -> bool:
        return extra_params.get("enrichments", []) and set([e.lower() for e in extra_params.get("enrichments", [])]).issubset(set(supported_assets))

    @staticmethod
    def init(configuration: dict) -> None:
        ...

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

    def get_target_asset_filepath(self, url: str, asset_name: str) -> str:
        """Provides the name of the file for storing the asset

        Args:
            url (str): the original url
            asset_name (str): the name of the asset to be stored

        Returns:
            str: the path to the file for storing the asset's file
        """
        assets_dir = self.get_assets_dir(url)
        return os.path.sep.join([assets_dir, asset_name])

    def get_asset_href(self, item: Item) -> str | None:
        data = item.assets.get(Role.data.value)
        return data.href if data else None

    @abstractmethod
    def create_enrichment(self, item: Item, enrichment: str) -> list[Asset]:
        """Create the assets metadata (Asset) and data (file) for a given item

        Args:
            item (Item): The item to be enriched
            enrichment (list[str]): names of the enrichment to create, e.g. 'cog'. This can lead to multiple asset creation.

        Returns:
            list[Asset]: the list of the created assets
        """
        ...

    def create_enrichments(self, item: Item, enrichments: list[str]) -> list[Asset]:
        assets = []
        for enrichment in enrichments:
            self.LOGGER.info("creating {} for item {}".format(enrichment, item.id))
            assets.extend(self.create_enrichment(item, enrichment))
        return assets
