import hashlib
import os
from abc import abstractmethod

from airs.core.models.model import Asset, Item
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver
from extensions.aproc.proc.drivers.exceptions import DriverException


class IngestDriver(AbstractDriver):

    def __init__(self):
        super().__init__()
        self.thumbnail_size = 256
        self.overview_size = 1024

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        return

    def get_assets_dir(self, url: str) -> str:
        """Provides the directory for storing the assets

        Args:
            url (str): the original url

        Returns:
            str: the directory for storing the assets
        """
        if not url:
            raise DriverException("Url can not be None")
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
        if not url:
            raise DriverException("Url can not be None")
        if not asset:
            raise DriverException("Asset can not be None")
        if not asset.name:
            raise DriverException("Asset name is undefined for {}".format(asset.model_dump_json(exclude_none=True, exclude_unset=True)))
        return os.path.sep.join([self.get_assets_dir(url), asset.name])

    @abstractmethod
    def get_item_id(self, url: str) -> str:
        """Return the id of the item currently process by the driver.

        Args:
            url (str): archive's url

        Returns:
            str: the id of the item currently process by the driver
        """
        ...

    @abstractmethod
    def identify_assets(self, url: str) -> list[Asset]:
        """Analyse the archive pointed by the url and returns the list of assets of the archive

        Args:
            url (str): archive's url

        Returns:
            list[Asset]: list of assets of the archive. Assets must have a valid name, href and roles.
        """
        ...

    @abstractmethod
    def fetch_assets(self, url: str, resources: list[Asset]) -> list[Asset]:
        """Copy or download the assets locally

        Args:
            url (str): archive's url
            resources (list[Asset]): list of assets to be fetched

        Returns:
            list[Asset]: list of fetched assets. Assets must have a valid name, href and roles. Assets href must be existing local files.
        """
        ...

    @abstractmethod
    def transform_assets(self, url: str, resources: list[Asset]) -> list[Asset]:
        """Transform the assets, if necessary

        Args:
            url (str): archive's url
            resources (list[Asset]): list of assets to be transformed

        Returns:
            list[Asset]: list of transformed assets. Assets must have a valid name, href and roles. Assets href must be existing local files.
        """
        ...

    @abstractmethod
    def to_item(self, url: str, resources: list[Asset]) -> Item:
        """Analyse an archive assets to create an item

        Args:
            url (str): archive's url
            resources (list[Asset]): list of assets. Assets must have a valid name, href and roles. Assets href must be existing local files.

        Returns:
            Item: the item. An item must have a valid id and valid assets.
        """
        ...
