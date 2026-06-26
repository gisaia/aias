import os
import tempfile
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.enrich_process import supported_assets_for_enrichment
from extensions.aproc.proc.utils.cog_helper import helper_build_cog, helper_create_asset_from_location


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower(), AssetFormat.all_bands_cog.value.lower()]
    configuration: dict = {}

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        EnrichDriver.init(configuration)
        supported_assets_for_enrichment.update(Driver.SUPPORTED_ASSET_TYPES)
        Driver.configuration['cog_overview_max_resolution_m'] = Driver.configuration.get('cog_overview_max_resolution_m', 500)
        Driver.configuration['cog_overview_downscale_factor'] = Driver.configuration.get('cog_overview_downscale_factor', 10)
        Driver.configuration['cog_max_resolution_m'] = Driver.configuration.get('cog_overview_max_resolution_m', -1)
        Driver.configuration['cog_downscale_factor'] = Driver.configuration.get('cog_overview_downscale_factor', -1)
        Driver.configuration['asset_suffixes_as_source_for_cog_generation'] = Driver.configuration.get('asset_suffixes_as_source_for_cog_generation', ["_b8.tif"])

    def __find_asset_name(self, item: Item) -> str | None:
        return next((asset_name for asset_name in item.assets.keys() if asset_name.lower().endswith(tuple(Driver.configuration['asset_suffixes_as_source_for_cog_generation']))), None)
        
    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        return self.__supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES, [ItemFormat.landsat.value.lower()]) and self.__find_asset_name(resource) is not None

    # Implements drivers method
    def create_enrichement(self, item: Item, enrichment: str) -> list[Asset]:
        target = self.get_asset_filepath(item.id, enrichment)
        if enrichment.lower() == AssetFormat.cog.value.lower() or enrichment.lower() == AssetFormat.overview_cog.value.lower():
            asset_source = item.assets.get(self.__find_asset_name(resource))
            if asset_source and asset_source.href:
                max_resolution_m = Driver.configuration['cog_max_resolution_m']
                downscale_factor = Driver.configuration['cog_downscale_factor']
                if enrichment == AssetFormat.overview_cog.value.lower():
                    max_resolution_m = Driver.configuration['cog_overview_max_resolution_m']
                    downscale_factor = Driver.configuration['cog_overview_downscale_factor']
                helper_build_cog(asset_source.href, target, params={}, downscale_factor=downscale_factor, max_resolution_m=max_resolution_m)
                return [helper_create_asset_from_location(item, enrichment, target)]
            else:
                raise DriverException(f"No asset found for enrichment {enrichment} with prefix {Driver.configuration['asset_suffixes_as_source_for_cog_generation']}")

        if enrichment.lower() == AssetFormat.all_bands_cog.value.lower():
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
            with AccessManager.make_local_list(data_href) as local_assets:
                # Build VRT to facilitate COG built
                from osgeo import gdal
                kwargs = {"separate": True, "resolution": "highest"}
                gdal.BuildVRT(vrt_file, local_assets, **kwargs)

                helper_build_cog(vrt_file, asset_location, params={}, downscale_factor=Driver.configuration['cog_downscale_factor'], max_resolution_m=Driver.configuration['cog_max_resolution_m'])

            AccessManager.clean(vrt_file)  # !DELETE!
        else:
            raise DriverException("Data assets not found for {}/{}".format(item.collection, item.id))
