import os
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager, AnyStorage
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.utils.cog_helper import helper_build_cog, helper_create_asset_from_location
from extensions.aproc.proc.enrich.enrich_process import supported_assets_for_enrichment


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower()]
    configuration: dict = {}

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        EnrichDriver.init(configuration)
        if configuration:
            Driver.configuration = configuration
        supported_assets_for_enrichment.update(Driver.SUPPORTED_ASSET_TYPES)
        Driver.configuration['asset_name_as_source_for_cog_generation'] = Driver.configuration.get('asset_name_as_source_for_cog_generation', Role.data.value)
        Driver.configuration['cog_overview_max_resolution_m'] = Driver.configuration.get('cog_overview_max_resolution_m', 500)
        Driver.configuration['cog_overview_downscale_factor'] = Driver.configuration.get('cog_overview_downscale_factor', 10)
        Driver.configuration['cog_max_resolution_m'] = Driver.configuration.get('cog_max_resolution_m', -1)
        Driver.configuration['cog_downscale_factor'] = Driver.configuration.get('cog_downscale_factor', 10)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        if self.supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES):
            asset_source = resource.assets.get(Driver.configuration['asset_name_as_source_for_cog_generation'])
            if asset_source is not None and asset_source.href is not None and asset_source.type in [MimeType.TIFF.value, MimeType.COG.value, MimeType.JPEG2000.value]:
                return True
        return False

    # Implements drivers method
    def create_enrichement(self, item: Item, enrichment: str) -> list[Asset]:
        data_asset = item.assets.get(Driver.configuration['asset_name_as_source_for_cog_generation'])
        if not data_asset or not data_asset.href:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        source = data_asset.href
        target = self.get_asset_filepath(item.id, enrichment)
        max_resolution_m = Driver.configuration['cog_max_resolution_m']
        downscale_factor = Driver.configuration['cog_downscale_factor']
        if enrichment == AssetFormat.overview_cog.value.lower():
            max_resolution_m = Driver.configuration['cog_overview_max_resolution_m']
            downscale_factor = Driver.configuration['cog_overview_downscale_factor']

        helper_build_cog(source, target, params={}, downscale_factor=downscale_factor, max_resolution_m=max_resolution_m)
        return [helper_create_asset_from_location(item, enrichment, target)]
