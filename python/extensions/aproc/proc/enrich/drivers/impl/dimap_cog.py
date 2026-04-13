import os
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower()]

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        EnrichDriver.init(configuration)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        return extra_params.get("asset_type", "") == "cog" and resource.properties is not None and resource.properties.item_format is not None and resource.properties.item_format.lower() == ItemFormat.dimap.value.lower()

    # Implements drivers method
    def create_assets(self, item: Item, asset_type: str) -> list[Asset]:
        if asset_type:
            if asset_type.lower() in Driver.SUPPORTED_ASSET_TYPES:
                self.LOGGER.info("adding {} to item {}".format(asset_type, item.id))
                assets = [self.__create_cog_asset(item, asset_type)]
                return assets
            else:
                raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
        else:
            raise DriverException("Asset type must be provided.")

    def __create_cog_asset(self, item: Item, asset_type: str) -> Asset:
        asset = Asset(
            name=Role.cog.value,
            size=0,     # set once asset created
            href=None,  # set below
            asset_type=ResourceType.gridded.value,
            asset_format=AssetFormat.geotiff.value,
            roles=[Role.cog.value],
            type=MimeType.TIFF.value,
            title="{} for {}/{}".format(asset_type, item.collection, item.id),
            description="{} for {}/{}".format(asset_type, item.collection, item.id),
            proj__epsg=3857,
            airs__managed=True
        )
        asset_location = self.get_asset_filepath(item.id, asset)
        asset.href = asset_location
        self.__build_cog(item, asset_location)
        asset.size = AccessManager.get_size(asset_location)
        return asset

    def __build_cog(self, item: Item, asset_location: str):
        data_asset = item.assets.get(Role.data.value)
        if not data_asset:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        href = data_asset.href
        if href:
            self.LOGGER.info("Building cog for {}".format(item.id))

            from osgeo import gdal
            
            start = time()
            # Download file
            tci_file_path = os.path.join(AccessManager.tmp_dir, os.path.basename(href))
            AccessManager.pull(href, tci_file_path)
            self.LOGGER.info("Fetching the data took {} s".format(time() - start))

            start = time()
            kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
            gdal.Warp(asset_location, tci_file_path, **kwargs)
            self.LOGGER.info("Creating COG took {} s".format(time() - start))

            os.remove(tci_file_path)  # !DELETE!
        else:
            raise DriverException("Data asset href is missing for {}/{}".format(item.collection, item.id))
