import os
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager, AnyStorage
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.drivers.impl.cog_constants import COG_MAX_WIDTH_OR_HEIGHT, COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT
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
        Driver.configuration['cog_overview_max_width_or_height'] = Driver.configuration.get('cog_overview_max_width_or_height', COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT)
        Driver.configuration['cog_max_width_or_height'] = Driver.configuration.get('cog_max_width_or_height', COG_MAX_WIDTH_OR_HEIGHT)

    def has_mime_type(self, mime_type: str, mime_types: list[str]) -> bool:
        return any(s.lower() == mime_type.lower() for s in mime_types)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        if self.supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES):
            asset_source = resource.assets.get(Role.data.value)
            if asset_source is not None and asset_source.href:
                if self.has_mime_type(asset_source.type, [MimeType.TIFF.value, MimeType.COG.value]) or asset_source.asset_format in [AssetFormat.cog.value, AssetFormat.geotiff.value]:
                    return True
        return False

    # Implements drivers method
    def create_enrichment(self, item: Item, enrichment: str) -> list[Asset]:
        data_asset = item.assets.get(Role.data.value)
        if not data_asset or not data_asset.href:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        source = data_asset.href
        target = self.get_target_asset_filepath(item.id, enrichment)
        cog_max_width_or_height = Driver.configuration['cog_max_width_or_height']
        if enrichment == AssetFormat.overview_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_overview_max_width_or_height']

        helper_build_cog(source, target, max_px_width_or_height=cog_max_width_or_height)
        return [helper_create_asset_from_location(item, enrichment, target)]
