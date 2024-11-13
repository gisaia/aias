import os
import shutil
from pathlib import Path

from airs.core.models.model import Asset, AssetFormat, Item, ItemFormat, ResourceType, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.enrich.drivers.driver import \
    Driver as EnrichDriver
from extensions.aproc.proc.enrich.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_file_size)


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = ["cog"]

    # Implements drivers method
    @staticmethod
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        return item.properties.item_format and item.properties.item_format.lower() == ItemFormat.safe.value.lower()

    # Implements drivers method
    def create_asset(self, item: Item, asset_type: str) -> tuple[Asset, str]:
        if asset_type:
            if asset_type.lower() in Driver.SUPPORTED_ASSET_TYPES:
                Driver.LOGGER.info("adding {} to item {}".format(asset_type, item.id))
                asset = Asset(
                    name=Role.cog.value,
                    size=0,     # set once asset created
                    href=None,  # set below
                    asset_type=ResourceType.gridded.value,
                    asset_format=AssetFormat.geotiff.value,
                    roles=[Role.cog.value],
                    type="image/tiff",
                    title="{} for {}/{}".format(asset_type, item.collection, item.id),
                    description="{} for {}/{}".format(asset_type, item.collection, item.id),
                    proj__epsg=3857,
                    airs__managed=True
                )
                asset_location = self.get_asset_filepath(item.id, asset)
                asset.href = asset_location
                Path(asset_location).touch()
                Driver.__build_asset(item, asset_type, asset_location)
                asset.size = get_file_size(asset_location)
                return asset, asset_location
            else:
                raise DriverException("Unsupported asset type {} . Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
        else:
            raise DriverException("Asset type must be provided.")

    def __build_asset(item: Item, asset_type: str, asset_location: str):
        if asset_type.lower() == "cog":
            data_asset = item.assets.get(Role.data.value)
            if data_asset:
                Driver.LOGGER.info("Building cog for {}".format(item.id))
                ######################################
                # TODO : add the code to build the COG
                ######################################
            else:
                raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))
        else:
            raise DriverException("Unsupported asset type {} . Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
