import hashlib
import os
from abc import abstractmethod
from typing import Any

from aias_common.access.manager import AccessManager
from airs.core.models.model import Asset, Item, Role
from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import get_hash_url


class IngestDriver(AbstractDriver):
    # Factor to apply when downsampling an overview
    THUMBNAIL_DOWNSAMPLE_FACTOR = 4
    # Factor to apply when downsampling a large overview
    THUMBNAIL_DOWNSAMPLE_FACTOR_LARGE = 8
    # When generating an overview from a browse, keep the whole image
    OVERVIEW_FROM_BROWSE_PCT = 100
    # When generating an overview from a tiff, reduce the tiff resolution
    OVERVIEW_FROM_TIFF_PCT = 25
    # When generating an overview from a large tiff, reduce the tiff resolution
    OVERVIEW_FROM_LARGE_TIFF_PCT = 10

    def __init__(self):
        super().__init__()

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

    # Implements drivers method
    def supports(self, resource: str, extra_params: dict[str, Any] = {}) -> bool:
        try:
            result = self.__check_path__(resource)
            return result
        except Exception as e:
            self.LOGGER.warning(e)
            return False

    def get_item_id(self, url: str) -> str:
        """Return the id of the item currently process by the driver.

        Args:
            url (str): archive's url

        Returns:
            str: the id of the item currently process by the driver
        """
        return get_hash_url(url)

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
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        """Copy or download the assets locally

        Args:
            url (str): archive's url
            assets (list[Asset]): list of assets to be fetched

        Returns:
            list[Asset]: list of fetched assets. Assets must have a valid name, href and roles.
        """
        ...

    @abstractmethod
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        """Transform the assets, if necessary

        Args:
            url (str): archive's url
            assets (list[Asset]): list of assets to be transformed

        Returns:
            list[Asset]: list of transformed assets. Assets must have a valid name, href and roles.
        """
        ...

    def to_item(self, url: str, assets: list[Asset]) -> Item:
        """Analyse an archive assets to create an item

        Args:
            url (str): archive's url
            assets (list[Asset]): list of assets. Assets must have a valid name, href and roles.

        Returns:
            Item: the item. An item must have a valid id and valid assets.
        """
        metadata = self.load_metadata(url)

        try:
            item = self.build_core_item(url, assets, metadata)
            item.id = self.get_item_id(url)
        except Exception as e:
            raise DriverException(e)

        self.validate_item(url, item)

        try:
            item = self.add_major_metadata(url, item, metadata)
        except Exception as e:
            self.LOGGER.warning(f"Failed to retrieve additional information: {e}")

        self.log_if_missing(url, item)

        try:
            item = self.add_minor_metadata(url, item, metadata)
        except Exception:
            ...

        return item

    def validate_item(self, url: str, item: Item):
        """
        Validate that the created item contains all the mandatory properties

        Args:
            url (str): archive's url
            item (Item): the item
        """
        if item.geometry is None:
            raise DriverException(f"No geometry was found for {url}")
        elif item.bbox is None:
            raise DriverException(f"No bbox was found for {url}")
        elif item.centroid is None:
            raise DriverException(f"No centroid was found for {url}")
        elif item.properties.datetime is None:
            raise DriverException(f"No datetime was found for {url}")
        elif item.properties.constellation is None:
            raise DriverException(f"No constellation was found for {url}")
        elif item.properties.item_type is None:
            raise DriverException(f"No item_type was found for {url}")
        elif item.properties.item_format is None:
            raise DriverException(f"No item_format was found for {url}")
        elif item.properties.main_asset_format is None:
            raise DriverException(f"No main_asset_format was found for {url}")
        elif item.properties.main_asset_name is None:
            raise DriverException(f"No main_asset_name was found for {url}")
        elif item.assets.get(item.properties.main_asset_name) is None:
            raise DriverException(f"No {item.properties.main_asset_name} asset was found for {url}")
        elif item.properties.observation_type is None:
            raise DriverException(f"No observation_type was found for {url}")
        elif item.assets.get(Role.archive.value) is None:
            raise DriverException(f"No archive asset was found for {url}")

        # Check that there is at least one asset with data asset
        roles = [a.roles for a in item.assets.values()]
        unique_roles = set()
        for role in roles:
            for r in role:
                unique_roles.add(r)

        if Role.data.value not in unique_roles:
            raise DriverException(f"No asset has the data role for {url}")

    def log_if_missing(self, url: str, item: Item):
        """
        Checks if some of the item properties are missing. If they are, log a warning

        Args:
            url (str): archive's url
            item (Item): the item
        """
        if item.properties.sensor_type is None:
            self.LOGGER.warning(f"No sensor type was found for {url}")
        if item.properties.secondary_id is None:
            self.LOGGER.warning(f"No ID was found for {url}")
        if item.properties.satellite is None:
            self.LOGGER.warning(f"No satellite was found for {url}")
        if item.properties.gsd is None:
            self.LOGGER.warning(f"No resolution was found for {url}")
        if item.properties.processing__level is None:
            self.LOGGER.warning(f"No processing level was found for {url}")
        if item.properties.proj__epsg is None:
            self.LOGGER.warning(f"No projection was found for {url}")
        if item.assets.get(Role.thumbnail.value) is None:
            self.LOGGER.warning(f"No thumbnail was found for {url}")
        if item.assets.get(Role.overview.value) is None:
            self.LOGGER.warning(f"No overview was found for {url}")

    @abstractmethod
    def load_metadata(self, url: str) -> object:
        """Load the archive's metadata to prepare the item creation

        Args:
            url (str): archive's url

        Returns:
            Object: A structure containing the metadata (diictionary, parsed xml, ...)
        """
        ...

    @abstractmethod
    def build_core_item(self, url: str, assets: list[Asset], metadata: object) -> Item:
        """Create an item containing all the mandatory metadata:
            - id
            - geometry
            - centroid
            - bbox
            - datetime
            - constellation
            - item_type
            - item_format
            - main_asset_format
            - main_asset_name
            - observation_type
            - assets

        Args:
            url (str): archive's url
            assets (list[Asset]): list of assets. Assets must have a valid name, href and roles.
            metadata (object): metadata describing the item

        Returns:
            Item: the item
        """
        ...

    @abstractmethod
    def add_major_metadata(self, url: str, item: Item, metadata: object) -> Item:
        """Add to the item major metadata:
            - satellite
            - resolution
            - processing level
            - projection

        Args:
            url (str): archive's url
            item (Item): the item
            metadata (object): metadata describing the item

        Returns:
            Item: the item
        """
        ...

    @abstractmethod
    def add_minor_metadata(self, url: str, item: Item, metadata: object) -> Item:
        """Add to the item the rest of the metadata

        Args:
            url (str): archive's url
            item (Item): the item
            metadata (object): metadata describing the item

        Returns:
            Item: the item
        """
        ...

    @abstractmethod
    def __check_path__(self, path: str) -> bool:
        """Checks whether the given archive's path is supported by the driver

        Args:
            path (str): archive's path to check

        Returns:
            bool: Whether the archive is supported
        """
        ...
