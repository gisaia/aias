import tempfile
from time import time

from aias_common.access.manager import AccessManager, AnyStorage
from airs.core.models.model import (Asset, AssetFormat, Item, MimeType,
                                    ResourceType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.enrich_process import \
    supported_assets_for_enrichment

COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT = 2000
COG_MAX_WIDTH_OR_HEIGHT = 10000
ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT = 10000


class CogBuilderHelper:
    @staticmethod
    def init(driver: type[EnrichDriver], configuration: dict):
        """
        Initializes the configuration of a driver
        """
        EnrichDriver.init(configuration)
        driver.configuration = configuration or {}
        supported_assets_for_enrichment.update(driver.SUPPORTED_ASSET_TYPES)
        driver.configuration['cog_overview_max_width_or_height'] = driver.configuration.get('cog_overview_max_width_or_height', COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT)
        driver.configuration['cog_max_width_or_height'] = driver.configuration.get('cog_max_width_or_height', COG_MAX_WIDTH_OR_HEIGHT)
        driver.configuration['all_bands_cog_max_width_or_height'] = driver.configuration.get('all_bands_cog_max_width_or_height', ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT)

    @staticmethod
    def build(source: str, target: str, max_px_width_or_height: int = 2000, options: dict = {}):
        """ Generate a COG from a source file and store it in the target location.

        Args:
            source (str): source file location (can be a local path or a remote URL like VSI)
            target (str): target file location
            max_px_width_or_height (int, optional): maximum width or height for the COG.
            options (dict, optional): additional GDAL options provided to WARP. See osgeo.gdal.WarpOptions in https://gdal.org/en/stable/api/python/utilities.html
        """
        from osgeo import gdal
        gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())
        LOGGER = EnrichDriver.LOGGER
        storage: AnyStorage = AccessManager.resolve_storage(source)
        source = storage.gdal_transform_href_vsi(source)
        with gdal.config_options(storage.get_gdal_stream_options()):
            kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857', 'resampleAlg': 'average'}
            if max_px_width_or_height > 0:
                with gdal.Open(source) as ds:
                    src_width = ds.RasterXSize
                    src_height = ds.RasterYSize
                # We take the max between the width and the height and we compute the scale factor.
                # We use the min between the scale factor and 1 because
                # we do not want to upscale the image if the width or height < max_px.
                factor = min(1, max_px_width_or_height / max(src_width, src_height))
                target_width = int(src_width * factor)
                target_height = int(src_height * factor)
                kwargs['width'] = str(target_width)
                kwargs['height'] = str(target_height)
            else:
                kwargs['resolution'] = "highest"

            kwargs.update(options)
            LOGGER.info(f"Building COG from {source} to {target} with parameters={kwargs}")
            start = time()
            gdal.Warp(target, source, **kwargs)

            if not AccessManager.exists(target):
                raise DriverException(f"Failed to build a COG from {source}")
            LOGGER.info("Creating COG took {} s".format(time() - start))

    @staticmethod
    def create_asset(item: Item, asset_type: str, asset_location: str, resource_type=ResourceType.gridded.value, asset_format=AssetFormat.cog.value, mime_type=MimeType.TIFF.value) -> Asset:
        asset = Asset(
            name=asset_type,
            size=AccessManager.get_size(asset_location),     # set once asset created
            href=asset_location,
            asset_type=resource_type,
            asset_format=asset_format,
            roles=[asset_type],
            type=mime_type,
            title="{} for {}/{}".format(asset_type, item.collection, item.id),
            description="{} for {}/{}".format(asset_type, item.collection, item.id),
            proj__epsg=3857,
            airs__managed=True
        )
        return asset
