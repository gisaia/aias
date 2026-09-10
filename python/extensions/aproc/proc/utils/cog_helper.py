import os
import tempfile

from aias_common.access.manager import AccessManager, AnyStorage
from airs.core.models.model import ResourceType, AssetFormat, MimeType, Item, Asset
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from time import time


def helper_create_asset_from_location(item: Item, asset_type: str, asset_location: str, resource_type=ResourceType.gridded.value, asset_format=AssetFormat.cog.value, mime_type=MimeType.TIFF.value) -> Asset:
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


def helper_build_cog(source: str, target: str, max_px_width_or_height: int = 2000, options: dict = {}):
    """ Generate a COG from a source file and store it in the target location.

    Args:
        source (str): source file location (can be a local path or a remote URL like VSI)
        target (str): target file location
        max_px_width_or_height (int, optional): maximum width or height for the COG.
        options (dict, optional): additional GDAL options provided to WARP. See osgeo.gdal.WarpOptions in https://gdal.org/en/stable/api/python/utilities.html
        stretch (bool, optional): whether to stretch the band 1 of the image (if nb bands != 3).
    """
    from osgeo import gdal
    gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())
    LOGGER = EnrichDriver.LOGGER
    storage: AnyStorage = AccessManager.resolve_storage(source)
    source = storage.gdal_transform_href_vsi(source)
    temp_scaled_path = ""
    try:
        with gdal.config_options(storage.get_gdal_stream_options()):
            warp_params = {'format': 'COG', 'dstSRS': 'EPSG:3857', 'resampleAlg': 'average'}
            with gdal.Open(source) as ds:
                src_width = ds.RasterXSize
                src_height = ds.RasterYSize
                raster_count = ds.RasterCount
                # If the raster has 3 bands, we assume it is RGB.
                # If the raster has 4 bands, we assume it is RGBAlpha.
                # otherwise, we assume it is grayscale and we stretch the first band to 0-255, we ignore the others.
                if (raster_count != 3 and raster_count != 4) or (raster_count == 4 and ds.GetRasterBand(4).GetColorInterpretation() != gdal.GCI_AlphaBand):
                    warp_params['srcBands'] = [1]  # type: ignore

                    scale_params = []
                    band_min, band_max = ds.GetRasterBand(1).ComputeRasterMinMax(approx_ok=True)
                    if band_min < 0 or band_max > 255:
                        LOGGER.debug(f"Stretching band 1 ({band_min}, {band_max}) of {source} to 0-255 for COG creation")
                        scale_params.append([band_min, band_max])

                        temp_scaled = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
                        temp_scaled_path = temp_scaled.name
                        temp_scaled.close()
                        translate_options = gdal.TranslateOptions(
                            format='GTiff',
                            bandList=[1],
                            outputType=gdal.GDT_Byte,
                            scaleParams=scale_params
                        )
                        gdal.Translate(temp_scaled_path, source, options=translate_options)
                        LOGGER.debug(f"Band 1 of {source} scaled to 0-255 and saved to {temp_scaled_path}")
                        source = temp_scaled_path

            if max_px_width_or_height > 0:
                # We take the max between the width and the height and we compute the scale factor.
                # We use the min between the scale factor and 1 because
                # we do not want to upscale the image if the width or height < max_px.
                factor = min(1, max_px_width_or_height / max(src_width, src_height))
                target_width = int(src_width * factor)
                target_height = int(src_height * factor)
                warp_params['width'] = str(target_width)  # type: ignore
                warp_params['height'] = str(target_height)  # type: ignore
            else:
                warp_params['resolution'] = "highest"
            warp_params.update(options)
            LOGGER.info(f"Building COG from {source} to {target} with parameters={warp_params}")
            start = time()
            gdal.Warp(target, source, **warp_params)
            LOGGER.info("Creating COG took {} s".format(time() - start))
    finally:
        if temp_scaled_path:
            try:
                os.remove(temp_scaled_path)
                LOGGER.debug(f"Temporary scaled file {temp_scaled_path} removed")
            except Exception as e:
                LOGGER.warning(f"Failed to remove temporary scaled file {temp_scaled_path}: {e}")
