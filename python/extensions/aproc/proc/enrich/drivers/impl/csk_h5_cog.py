import os
import tempfile
from typing import Any

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Role)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.drivers.impl.cog_constants import (
    COG_MAX_WIDTH_OR_HEIGHT, COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT)
from extensions.aproc.proc.enrich.enrich_process import \
    supported_assets_for_enrichment
from extensions.aproc.proc.ingest.drivers.impl.cosmoskymed import \
    csk_h5_scenes_to_geotiffs
from extensions.aproc.proc.utils.cog_helper import (
    helper_build_cog, helper_create_asset_from_location)


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

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        if self.supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES):
            Driver.LOGGER.warn(resource.properties.item_format)
            if resource.properties.item_format == ItemFormat.csk.value:
                asset_source = resource.assets.get(Role.data.value)
                if asset_source is not None and asset_source.href is not None:
                    Driver.LOGGER.warn(asset_source.type)
                    return asset_source.type == MimeType.HDF5.value
        return False

    # Implements drivers method
    def create_enrichment(self, item: Item, enrichment: str) -> list[Asset]:
        from osgeo import gdal
        gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())

        data_asset = item.assets.get(Role.data.value)
        if not data_asset or not data_asset.href:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

        source = data_asset.href
        target = self.get_target_asset_filepath(item.id, enrichment)

        cog_max_width_or_height = Driver.configuration['cog_max_width_or_height']
        if enrichment == AssetFormat.overview_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_overview_max_width_or_height']

        metadata = self.__load_metadata(source)

        merged_tif = tempfile.NamedTemporaryFile("w+", suffix=".tif", delete=False).name
        with csk_h5_scenes_to_geotiffs(source, metadata) as tiffs:
            gdal.Warp(merged_tif, tiffs, format="GTiff")

        helper_build_cog(merged_tif, target, max_px_width_or_height=cog_max_width_or_height)
        os.remove(merged_tif)  # !DELETE!

        return [helper_create_asset_from_location(item, enrichment, target)]

    def __load_metadata(self, data_path: str) -> dict:
        from osgeo import gdal

        options = gdal.InfoOptions(format="json")
        metadata = AccessManager.get_gdal_info(data_path, options)

        return metadata
