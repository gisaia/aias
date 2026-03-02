import json
import os
from datetime import datetime

from PIL import Image as PILImage

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Band, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from extensions.aproc.proc.drivers.exceptions import DriverException


class Driver(IngestDriver):
    """
    Ingest driver for Satellogic L1D_SR multispectral products.

    Supports extracted product directories containing:
    - STAC GeoJSON metadata (*_metadata_stac.geojson)
    - TOA raster (rasters/*_TOA_0.tif) - main data asset
    - Visual raster (rasters/*_VISUAL_0.tif) - optional
    - Cloud mask (rasters/*_CLOUD_0.tif) - optional
    - Thumbnail PNG (*_thumbnail.png) - optional
    - Preview PNG (*_preview.png) - optional
    """

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.toa_path = None
        self.visual_path = None
        self.cloud_path = None
        self.thumbnail_path = None
        self.preview_path = None
        self._cached_metadata = None  # Cache metadata to avoid double reads

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []

        # Add archive asset (the directory)
        ImageDriverHelper.add_archive(assets, url)

        # Load and cache STAC metadata to extract band information
        md = self._get_cached_metadata()

        # Extract eo:bands from STAC metadata for the analytic asset
        eo_bands = self._extract_bands(md)

        # Add TOA data asset (main data) with band information
        assets.append(Asset(
            href=self.toa_path,
            size=AccessManager.get_size(self.toa_path),
            roles=[Role.data.value],
            name=Role.data.value,
            type=MimeType.GEOTIFF.value,
            description="TOA multispectral data",
            airs__managed=False,
            asset_format=AssetFormat.geotiff.value,
            asset_type=ResourceType.gridded.value,
            eo__bands=eo_bands
        ))

        # Add visual asset if present
        if self.visual_path:
            ImageDriverHelper.add_asset(
                assets, self.visual_path, Role.visual,
                MimeType.GEOTIFF, AssetFormat.geotiff, ResourceType.gridded
            )

        # Add cloud mask asset if present
        if self.cloud_path:
            ImageDriverHelper.add_asset(
                assets, self.cloud_path, Role.cloud,
                MimeType.GEOTIFF, AssetFormat.geotiff, ResourceType.gridded
            )

        # Add metadata asset
        ImageDriverHelper.add_asset(
            assets, self.md_path, Role.metadata,
            MimeType.GEOJSON, AssetFormat.geojson, ResourceType.other
        )

        # Add thumbnail if present (use existing, no generation needed)
        if self.thumbnail_path:
            ImageDriverHelper.add_asset(
                assets, self.thumbnail_path, Role.thumbnail,
                MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True
            )

        # Add preview as overview if present (use existing, no generation needed)
        if self.preview_path:
            ImageDriverHelper.add_asset(
                assets, self.preview_path, Role.overview,
                MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True
            )

        return assets

    def _get_cached_metadata(self) -> dict:
        """Load and cache STAC metadata to avoid double reads."""
        if self._cached_metadata is None:
            with AccessManager.stream(self.md_path) as fb:
                self._cached_metadata = json.load(fb)
        return self._cached_metadata

    def _extract_bands(self, md: dict) -> list[Band]:
        """Extract band information from STAC metadata."""
        bands = []
        stac_assets = md.get("assets", {})
        analytic_asset = stac_assets.get("analytic", {})
        eo_bands_raw = analytic_asset.get("eo:bands", [])

        if not eo_bands_raw:
            self.LOGGER.warn("No eo:bands found in STAC metadata analytic asset")

        for b in eo_bands_raw:
            name = b.get("name")
            common_name = b.get("common_name")
            if not (name or common_name):
                continue
            bands.append(Band(
                name=name,
                eo__common_name=common_name,
                eo__center_wavelength=b.get("center_wavelength"),
                eo__full_width_half_max=b.get("full_width_half_max")
            ))

        return bands if bands else []

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        # All assets are local files, no fetching needed
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        has_overview = any(a.name == Role.overview.value for a in assets)
        has_thumbnail = any(a.name == Role.thumbnail.value for a in assets)

        if has_overview:
            # Satellogic preview PNGs have large black borders that cause the
            # quicklook to appear "too small" when positioned on the map using
            # the item bbox. Crop the overview before upload.
            for asset in assets:
                if asset.name == Role.overview.value:
                    self._crop_black_borders(url, asset)
        elif AccessManager.is_local(self.toa_path):
            # Fallback: generate overview from TOA data if no preview PNG
            tif_path = self.visual_path if self.visual_path else self.toa_path
            bands = [1, 2, 3] if self.visual_path else [3, 2, 1]
            quicklook = ImageDriverHelper.prepare_preview_asset(
                self, url, Role.overview, MimeType.JPG, AssetFormat.jpg
            )
            geotiff_to_jpg(
                tif_path,
                Driver.OVERVIEW_FROM_LARGE_TIFF_PCT,
                Driver.OVERVIEW_FROM_LARGE_TIFF_PCT,
                output_path=quicklook.href,
                bands_list=bands,
                stretch=not self.visual_path
            )
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)
            has_overview = True

        if not has_thumbnail and has_overview:
            # Generate thumbnail by downsampling the overview
            overview_href = next(
                a.href for a in assets if a.name == Role.overview.value
            )
            thumbnail = ImageDriverHelper.prepare_preview_asset(
                self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg
            )
            downsample_image(overview_href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)

        return assets

    def _crop_black_borders(self, url: str, asset: Asset):
        """Remove black padding from a PNG asset and save cropped version locally."""
        try:
            with AccessManager.stream(asset.href) as fb:
                img = PILImage.open(fb)
                img.load()  # Force read before stream closes

            w, h = img.size

            # getbbox() returns the bounding box of non-zero pixels as (left, top, right, bottom)
            # For near-black compression artifacts, point() thresholds first
            grayscale = img.convert("L")
            mask = grayscale.point(lambda px: 255 if px > 5 else 0)
            content_box = mask.getbbox()

            if content_box is None:
                return  # Entirely black, nothing to crop

            left, top, right, bottom = content_box

            # Only crop if borders are significant (>3% on any side)
            if top / h < 0.03 and (h - bottom) / h < 0.03 and left / w < 0.03 and (w - right) / w < 0.03:
                return

            cropped = img.crop(content_box)

            # Save to the driver's local assets directory
            role = Role.overview if asset.name == Role.overview.value else Role.thumbnail
            local_asset = ImageDriverHelper.prepare_preview_asset(
                self, url, role, MimeType.PNG, AssetFormat.png
            )
            os.makedirs(os.path.dirname(local_asset.href), exist_ok=True)
            cropped.save(local_asset.href, format="PNG")

            self.LOGGER.info(
                "Cropped %s black borders: %dx%d -> %dx%d",
                asset.name, w, h, right - left, bottom - top
            )
            asset.href = local_asset.href
            asset.size = os.path.getsize(local_asset.href)

        except Exception as e:
            self.LOGGER.warning("Failed to crop black borders from %s: %s", asset.name, e)

    def load_metadata(self, url: str) -> dict:
        return self._get_cached_metadata()

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        # Geometry and bbox directly from STAC (already in correct format)
        geometry = metadata.get("geometry")
        bbox = metadata.get("bbox")

        # Early validation for required STAC fields
        if not geometry:
            raise DriverException(f"Missing required 'geometry' in STAC metadata for {url}")
        if not bbox:
            raise DriverException(f"Missing required 'bbox' in STAC metadata for {url}")

        # Calculate centroid from bbox
        if bbox and len(bbox) >= 4:
            centroid_lon = (bbox[0] + bbox[2]) / 2
            centroid_lat = (bbox[1] + bbox[3]) / 2
            centroid = [centroid_lon, centroid_lat]
        else:
            centroid = None

        # Parse datetime fields from properties
        properties = metadata.get("properties", {})
        datetime_str = properties.get("datetime")
        if datetime_str:
            date_time = self._parse_datetime(datetime_str)
        else:
            raise DriverException(f"Missing required 'datetime' in STAC metadata for {url}")

        # Extract eo:bands for properties-level band info
        md = self._get_cached_metadata()
        eo_bands = self._extract_bands(md)

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation="Satellogic",  # Hardcoded (not "Aleph1" from STAC)
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.satellogic.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value,
                eo__bands=eo_bands if eo_bands else None,
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """Parse ISO 8601 datetime string, with or without microseconds."""
        try:
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        properties = metadata.get("properties", {})

        # GSD from properties.gsd
        item.properties.gsd = properties.get("gsd")

        # Platform from properties.platform
        item.properties.platform = properties.get("platform")

        # Satellite from properties.satl:sat_id
        item.properties.satellite = properties.get("satl:sat_id")

        # Projection from properties.proj:epsg
        item.properties.proj__epsg = properties.get("proj:epsg")

        # Processing level from properties.satl:product_name
        item.properties.processing__level = properties.get("satl:product_name")

        # License
        item.properties.license = properties.get("license")

        # Secondary ID from STAC id
        item.properties.secondary_id = metadata.get("id")

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        properties = metadata.get("properties", {})

        # Cloud cover
        item.properties.eo__cloud_cover = properties.get("eo:cloud_cover")

        # View angles
        item.properties.view__sun_azimuth = properties.get("view:sun_azimuth")
        item.properties.view__sun_elevation = properties.get("view:sun_elevation")
        item.properties.view__azimuth = properties.get("view:azimuth")
        item.properties.view__off_nadir = properties.get("view:off_nadir")
        item.properties.view__incidence_angle = properties.get("view:incidence_angle")

        # Instrument from properties.instruments[0]
        instruments = properties.get("instruments", [])
        if instruments:
            item.properties.instrument = instruments[0]

        # Sensor = satellite value
        item.properties.sensor = item.properties.satellite

        return item

    def __check_path__(self, path: str) -> bool:
        """
        Detect Satellogic product by checking for:
        - *_metadata_stac.geojson (required)
        - rasters/*_TOA_0.tif (required)
        - Optionally: *_VISUAL_0.tif, *_CLOUD_0.tif, *_thumbnail.png, *_preview.png
        """
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        # Scan main directory for metadata and preview files
        for file in AccessManager.listdir(path):
            if file.is_dir:
                continue

            if file.name.endswith("_metadata_stac.geojson"):
                self.md_path = file.path
            elif file.name.endswith("_thumbnail.png"):
                self.thumbnail_path = file.path
            elif file.name.endswith("_preview.png"):
                self.preview_path = file.path

        # Scan rasters subdirectory for TIF files
        rasters_path = os.path.join(path, "rasters")
        if AccessManager.is_dir(rasters_path):
            for file in AccessManager.listdir(rasters_path):
                if file.is_dir:
                    continue

                if file.name.endswith("_TOA_0.tif"):
                    self.toa_path = file.path
                elif file.name.endswith("_VISUAL_0.tif"):
                    self.visual_path = file.path
                elif file.name.endswith("_CLOUD_0.tif"):
                    self.cloud_path = file.path

        # Product is valid if we have metadata AND TOA data
        return self.md_path is not None and self.toa_path is not None
