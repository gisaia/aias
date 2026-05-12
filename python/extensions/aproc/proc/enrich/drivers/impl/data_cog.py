import os
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager, AnyStorage
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.utils.cog_helper import helper_build_cog, helper_create_asset_from_location


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower()]
    configuration: dict = {}

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        EnrichDriver.init(configuration)
        Driver.configuration.update(configuration or {})
        Driver.configuration['asset_name_for_cog'] = Driver.configuration.get('asset_name_for_cog', Role.data.value)            
        Driver.configuration['cog_size'] = Driver.configuration.get('cog_size', 500)            
            

    def supported_formats(self) -> list[str]:
        return [ItemFormat.digitalglobe.value.lower(),
                ItemFormat.dimap.value.lower(),
                ItemFormat.geoeye.value.lower(),
                ItemFormat.wyvern.value.lower()]

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        return resource.assets.get(Driver.configuration['asset_name_for_cog']) is not None and resource.assets.get(Driver.configuration['asset_name_for_cog']).href is not None and  self.__supports__(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES, self.supported_formats())


    # Implements drivers method
    def create_enrichement(self, item: Item, enrichment: str) -> list[Asset]:
        data_asset = item.assets.get(Driver.configuration['asset_name_for_cog'])
        if not data_asset or not data_asset.href:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        source = data_asset.href
        target = self.get_asset_filepath(item.id, enrichment)
        Driver.LOGGER.debug(f"build cog on {source} and place it in {target}")
        if enrichment == AssetFormat.cog.value.lower() and source:
            helper_build_cog(source, target)
            return [helper_create_asset_from_location(item, enrichment, target)]
        if enrichment == AssetFormat.overview_cog.value.lower() and source:
            helper_build_cog(source, target, params={"ts":str(Driver.configuration['cog_size'])})
            return [helper_create_asset_from_location(item, enrichment, target)]
        return []
