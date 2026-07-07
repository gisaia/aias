import os
import tempfile
from typing import Any
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager, AnyStorage
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.drivers.impl.cog_constants import ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT, COG_MAX_WIDTH_OR_HEIGHT, COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT
from extensions.aproc.proc.enrich.enrich_process import supported_assets_for_enrichment
from extensions.aproc.proc.utils.cog_helper import helper_build_cog, helper_create_asset_from_location


class Driver(EnrichDriver):

    NEEDED_ASSETS = [Role.red_band.value, Role.green_band.value, Role.blue_band.value]
    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower(), AssetFormat.all_bands_cog.value.lower()]
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
        Driver.configuration['all_bands_cog_max_width_or_height'] = Driver.configuration.get('all_bands_cog_max_width_or_height', ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT)

    def has_needed_assets(self, item: Item) -> bool:
        return all((role in item.assets.keys() and item.assets.get(role).href) for role in Driver.NEEDED_ASSETS)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        # Is it able to build the requested enrichment type?
        if self.supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES):
            # Is it a LANDSAT archive?
            if resource.properties and resource.properties.item_format and resource.properties.item_format.lower() == ItemFormat.landsat.value.lower():
                # Does it have a data asset?
                if self.has_needed_assets(resource):
                    return True
        return False

    def get_vsi_file(self, href: str) -> str:
        storage: AnyStorage = AccessManager.resolve_storage(href)
        return storage.gdal_transform_href_vsi(href)


    # Implements drivers method
    def create_enrichment(self, item: Item, enrichment: str) -> list[Asset]:
        if enrichment.lower() == AssetFormat.cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_max_width_or_height']
            band_files = [self.get_vsi_file(item.assets.get(a.value).href) for a in [Role.red_band, Role.green_band, Role.blue_band]]        
        elif enrichment.lower() == AssetFormat.overview_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_overview_max_width_or_height']
            band_files = [self.get_vsi_file(item.assets.get(a.value).href) for a in [Role.red_band, Role.green_band, Role.blue_band]]        
        elif enrichment.lower() == AssetFormat.all_bands_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['all_bands_cog_max_width_or_height']
            # Assets describing a band (it has eo__bands) is used in the all_bands_cog.
            bands = [b for b in item.assets.values() if b.eo__bands]
            band_files = [self.get_vsi_file(b.href) for b in bands]        
        else:
            raise DriverException("Unsupported asset type {}. Supported types are : {}".format(enrichment, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
        return [self.__create_cog_asset_from_bands(item, enrichment, band_files, cog_max_width_or_height=cog_max_width_or_height)]

    # Landsat has a tiff file per band. The cogs can be built without downloading the tiff files by using gdal virtual file system (vsi).
    def __create_cog_asset_from_bands(self, item: Item, enrichment: str, band_files: list[str], cog_max_width_or_height: int) -> Asset:
        from osgeo import gdal
        asset = Asset(
            name=enrichment,
            size=0,     # set once asset created
            href=None,  # set below
            asset_type=ResourceType.gridded.value,
            asset_format=AssetFormat.cog.value,
            roles=[enrichment],
            type=MimeType.TIFF.value,
            title="{} for {}/{}".format(enrichment, item.collection, item.id),
            description="{} for {}/{}".format(enrichment, item.collection, item.id),
            proj__epsg=3857,
            airs__managed=True
        )
        target_asset_location = self.get_target_asset_filepath(item.id, asset.name)
        asset.href = target_asset_location

        storage: AnyStorage = AccessManager.resolve_storage(item.assets.get(Role.red_band.value).href)
        with gdal.config_options(storage.get_gdal_stream_options()):
            self.LOGGER.info("Building cog for {} made of {}".format(item.id, ", ".join(band_files)))
            source_files_vrt = tempfile.NamedTemporaryFile("w+", suffix=".files", delete=False).name
            # Build VRT to facilitate COG built
            kwargs = {"separate": True, "resolution": "highest"}
            gdal.BuildVRT(source_files_vrt, band_files, **kwargs)
            helper_build_cog(source_files_vrt, target_asset_location, max_px_width_or_height=cog_max_width_or_height)
        AccessManager.clean(source_files_vrt)  # !DELETE!
        asset.size = AccessManager.get_size(target_asset_location)
        return asset
