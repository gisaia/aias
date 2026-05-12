import os
import tempfile
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower()]

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        EnrichDriver.init(configuration)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        return self.__supports__(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES, [ItemFormat.landsat.value.lower()])

    # Implements drivers method
    def create_enrichement(self, item: Item, enrichment: str) -> list[Asset]:
        return [self.__create_all_bands_asset(item, enrichment)]

    def __create_all_bands_asset(self, item: Item, asset_type: str) -> Asset:
        asset = Asset(
            name='all_bands_cog',
            size=0,     # set once asset created
            href=None,  # set below
            asset_type=ResourceType.gridded.value,
            asset_format=AssetFormat.geotiff.value,
            roles=[Role.cog.value],
            type=MimeType.TIFF.value,
            title="all bands COG for {}/{}".format(item.collection, item.id),
            description="all bands COG for {}/{}".format(item.collection, item.id),
            proj__epsg=3857,
            airs__managed=True
        )
        asset_location = self.get_asset_filepath(item.id, asset.name)
        asset.href = asset_location
        self.__build_all_bands_COG(item, asset_location)
        asset.size = AccessManager.get_size(asset_location)

        return asset

    def __build_all_bands_COG(self, item: Item, asset_location: str):
        data_assets = list(filter(lambda a: Role.data.value in a.roles or Role.data in a.roles, item.assets.values()))
        data_href = [a.href for a in data_assets]

        if data_href:
            data_href.sort()
            self.LOGGER.info("Building all bands cog for {}".format(item.id))
            vrt_file = tempfile.NamedTemporaryFile("w+", suffix=".vrt", delete=False).name

            from osgeo import gdal
            with AccessManager.make_local_list(data_href) as local_assets:
                start = time()

                # Build VRT to facilitate COG built
                kwargs = {"separate": True, "resolution": "highest"}
                gdal.BuildVRT(vrt_file, local_assets, **kwargs)

                # Build COG from VRT
                kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
                gdal.Warp(asset_location, vrt_file, **kwargs)
                self.LOGGER.info("Creating all bands COG took {} s".format(time() - start))

            AccessManager.clean(vrt_file)  # !DELETE!
        else:
            raise DriverException("Data assets not found for {}/{}".format(item.collection, item.id))
