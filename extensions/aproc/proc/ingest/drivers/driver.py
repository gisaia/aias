import hashlib
import os
from abc import ABC, abstractmethod
from airs.core.models.model import Asset, Item
from aproc.core.logger import Logger


class Driver(ABC):
    priority: int = 0
    name: str = None
    __assets_dir__: str = None
    LOGGER = Logger.logger
    thumbnail_size = 256
    overview_size = 1024

    def get_assets_dir(self, url: str) -> str:
        """Provides the directory for storing the assets

        Args:
            url (str): the original url

        Returns:
            str: the directory for storing the assets
        """
        unique = hashlib.md5(url.encode("utf-8")).hexdigest()
        dir = os.path.sep.join([self.__assets_dir__, unique])
        if not os.path.exists(self.__assets_dir__):
            os.makedirs(self.__assets_dir__)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def get_asset_filepath(self, url: str, asset: Asset) -> str:
        """Provides the name of the file for storing the asset

        Args:
            url (str): the original url
            asset (Asset): the asset to be stored, it's name must be provided.

        Returns:
            str: the path to the file for storing the asset's file
        """
        dir = self.get_assets_dir(url)
        return os.path.sep.join([dir, asset.name])

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
    def supports(url: str) -> bool:
        """Return True if the provided url points to an archive supported by this driver.

        Args:
            url (str): archive's url

        Returns:
            bool: True if the driver supports the archive format, False otherwise
        """
        ...
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
