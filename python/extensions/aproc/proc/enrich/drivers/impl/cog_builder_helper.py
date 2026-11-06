import os
import tempfile
from time import time

from aias_common.access.manager import AccessManager, AnyStorage
from airs.core.models.model import (Asset, AssetFormat, Band, CogType, Item,
                                    MimeType, ResourceType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.enrich_process import \
    supported_assets_for_enrichment
from extensions.aproc.proc.utils.find_rgb import find_rgb_bands

# COG sizes
# Keys
COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT_KEY = "cog_overview_max_width_or_height"
COG_MAX_WIDTH_OR_HEIGHT_KEY = "cog_max_width_or_height"
ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT_KEY = "all_bands_cog_max_width_or_height"
# Values
COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT = 2000
COG_MAX_WIDTH_OR_HEIGHT = 10000
ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT = 10000

# Stretch parameters
STRETCH_DATA_RANGE_THRESHOLD_KEY = "stretch_data_range_threshold"
STRETCH_LOWER_CUTOFF_PCT_KEY = "stretch_lower_cutoff_pct"
STRETCH_HIGHER_CUTOFF_PCT_KEY = "stretch_higher_cutoff_pct"

# GDAL options
COG_WARP_OPTIONS_KEY = "cog_warp_options"


class CogBuilderHelper:
    @staticmethod
    def init(driver: type[EnrichDriver], configuration: dict):
        """
        Initializes the configuration of a driver
        """
        EnrichDriver.init(configuration)
        driver.configuration = configuration or {}
        supported_assets_for_enrichment.update(driver.SUPPORTED_ASSET_TYPES)
        driver.configuration[COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT_KEY] = driver.configuration.get(COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT_KEY, COG_OVERVIEW_MAX_WIDTH_OR_HEIGHT)
        driver.configuration[COG_MAX_WIDTH_OR_HEIGHT_KEY] = driver.configuration.get(COG_MAX_WIDTH_OR_HEIGHT_KEY, COG_MAX_WIDTH_OR_HEIGHT)
        driver.configuration[ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT_KEY] = driver.configuration.get(ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT_KEY, ALL_BANDS_COG_MAX_WIDTH_OR_HEIGHT)

    @staticmethod
    def build(driver: type[EnrichDriver], source: str, target: str, max_px_width_or_height: int = 2000, visual: bool = False, eo__bands: list[Band] = []):
        """ Generate a COG from a source file and store it in the target location.

        Args:
            source (str): source file location (can be a local path or a remote URL like VSI)
            target (str): target file location
            max_px_width_or_height (int, optional): maximum width or height for the COG.
            visual (bool, optional): whether the generated COG is for direct visualization purposes.
            eo__bands (list[Band], optional): EO bands of the source asset

        Returns:
            cog_type (CogType): type of COG generated
            src_bands (list[int]): list of the band indices used in the source data
            stretched_bands (list[bool]): list of whether each used band was stretched
        """
        # additional GDAL options provided to WARP. See osgeo.gdal.WarpOptions in https://gdal.org/en/stable/api/python/utilities.html
        options = driver.configuration.get(COG_WARP_OPTIONS_KEY, {})
        # for a visual COG, if a band data range is below that threshold, then the band is stretched
        stretch_data_range_threshold = driver.configuration.get(STRETCH_DATA_RANGE_THRESHOLD_KEY, 25.0)
        # for a visual COG, if the band is stretched, designates the cutoff percentage for the lowest value of the distribution
        stretch_lower_cutoff_pct = driver.configuration.get(STRETCH_LOWER_CUTOFF_PCT_KEY, 0.02)
        # for a visual COG, if the band is stretched, designates the cutoff percentage for the highest value of the distribution
        stretch_higher_cutoff_pct = driver.configuration.get(STRETCH_HIGHER_CUTOFF_PCT_KEY, 0.98)

        import numpy as np
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

                    # Create arrays to report. By default (non-visual), no stretching and all bands are used
                    src_bands = [i + 1 for i in range(raster_count)]
                    stretched_bands = [False for _ in range(raster_count)]

                    cog_type = CogType.non_visual
                    # If it is a visual COG, then:
                    if visual:
                        # If the raster has 3 bands, we assume it is RGB.
                        if raster_count == 3:
                            cog_type = CogType.rgb
                        # If the raster has 4 bands, we assume it is RGBAlpha.
                        elif raster_count == 4 and ds.GetRasterBand(4).GetColorInterpretation() == gdal.GCI_AlphaBand:
                            cog_type = CogType.rgba
                        else:
                            if len(eo__bands) >= 3:
                                # If there are more than 3 bands, find the RGB bands
                                src_bands = find_rgb_bands(eo__bands)
                                cog_type = CogType.rgb
                            else:
                                # otherwise, we assume it is grayscale and we stretch the first band to 0-255, we ignore the others.
                                src_bands = [1]
                                cog_type = CogType.grayscale

                            scale_params = []
                            stretched_bands = []
                            # Stretch each band
                            for band_idx in src_bands:
                                min_val, max_val, mean_val, std_val = ds.GetRasterBand(band_idx).GetStatistics(True, True)
                                LOGGER.debug(f"Band {band_idx} of {source} statistics: min={min_val}, max={max_val}, mean={mean_val}, std={std_val}")
                                if min_val == max_val:
                                    stretched_bands.append(False)
                                    LOGGER.warning(f"Band {band_idx} of {source} has min=max={min_val}. Skipping stretch to 0-255 for COG creation.")
                                    max_val = min_val + 1.0
                                elif min_val < 0.0 or max_val > 255.0 or (max_val - min_val < stretch_data_range_threshold):
                                    stretched_bands.append(True)
                                    hist = ds.GetRasterBand(band_idx).GetHistogram(min_val, max_val, 1024, False, True)
                                    cumulative = np.cumsum(hist)
                                    total_pixels = cumulative[-1]
                                    bin_edges = np.linspace(min_val, max_val, 1024)
                                    stretch_min = bin_edges[np.searchsorted(cumulative, total_pixels * stretch_lower_cutoff_pct)]
                                    stretch_max = bin_edges[np.searchsorted(cumulative, total_pixels * stretch_higher_cutoff_pct)]
                                    LOGGER.debug(f"Stretching band {band_idx} ({stretch_min}, {stretch_max}) of {source} to 0-255 for COG creation (inital min/max: {min_val}, {max_val})")
                                    scale_params.append([stretch_min, stretch_max])
                                else:
                                    stretched_bands.append(False)
                            # Generate temporary stretched GeoTiff
                            temp_scaled = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
                            temp_scaled_path = temp_scaled.name
                            temp_scaled.close()
                            translate_options = gdal.TranslateOptions(
                                format='GTiff',
                                bandList=src_bands,
                                outputType=gdal.GDT_Byte,
                                scaleParams=scale_params
                            )
                            gdal.Translate(temp_scaled_path, source, options=translate_options)
                            LOGGER.debug(f"Bands {src_bands} of {source} scaled to 0-255 and saved to {temp_scaled_path}")
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
                warp_params.update(options)
                LOGGER.info(f"Building COG from {source} to {target} with parameters={warp_params}")
                start = time()
                gdal.Warp(target, source, **warp_params)
                LOGGER.info("Creating COG took {} s".format(time() - start))

            return cog_type, src_bands, stretched_bands
        finally:
            if temp_scaled_path:
                try:
                    os.remove(temp_scaled_path)
                    LOGGER.debug(f"Temporary scaled file {temp_scaled_path} removed")
                except Exception as e:
                    LOGGER.warning(f"Failed to remove temporary scaled file {temp_scaled_path}: {e}")

    @staticmethod
    def create_asset(item: Item, enrichment: str, asset_location: str, cog_type: CogType, bands: list[Band]) -> Asset:
        # Get asset_format from enrichment
        if enrichment.lower() == AssetFormat.cog.value.lower():
            asset_format = AssetFormat.cog
        elif enrichment.lower() == AssetFormat.overview_cog.value.lower():
            asset_format = AssetFormat.overview_cog
        elif enrichment.lower() == AssetFormat.all_bands_cog.value.lower():
            asset_format = AssetFormat.all_bands_cog
        else:
            raise DriverException(f"Failed to create the Asset: got unregistered enrichment {enrichment}")

        asset = Asset(
            name=enrichment,
            size=AccessManager.get_size(asset_location),
            href=asset_location,
            asset_type=ResourceType.gridded.value,
            asset_format=asset_format.value,
            roles=[enrichment],
            type=MimeType.TIFF.value,
            title="{} for {}/{}".format(enrichment, item.collection, item.id),
            description="{} for {}/{}".format(enrichment, item.collection, item.id),
            proj__epsg=3857,
            airs__managed=True,
            airs__cog_type=cog_type,
            airs__nb_bands=len(bands),
            eo__bands=bands
        )
        return asset

    @staticmethod
    def create_bands(item: Item, band_indices: list[int], is_stretched_list: list[bool]) -> list[Band]:
        source_bands = item.properties.eo__bands
        cog_bands: list[Band] = []

        for (band_idx, is_stretched) in zip(band_indices, is_stretched_list):
            index_match = [b for b in source_bands if b.index == band_idx]

            if len(index_match) == 0:
                band = Band(index=band_idx, name=f"Band {band_idx}",
                            airs__is_stretched=is_stretched)
            else:
                band = Band(**index_match[0].model_dump())
                band.airs__is_stretched = is_stretched

            cog_bands.append(band)

        return cog_bands
