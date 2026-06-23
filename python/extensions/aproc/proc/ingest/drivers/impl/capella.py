import json
import os
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg, get_bbox, get_centroid,
                                                             get_epsg, get_epsg_from_gdal_info_gcps)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.extended_md_path = None
        self.digest_md_path = None
        self.big_preview_path = None
        self.quicklook_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration

    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        if self.tif_path:
            ImageDriverHelper.add_asset(assets, self.tif_path, Role.data, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
            
        if self.extended_md_path:
            ImageDriverHelper.add_asset(assets, self.extended_md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other)
            
        if self.digest_md_path:
            ImageDriverHelper.add_asset(assets, self.digest_md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other)

        if self.big_preview_path:
            asset = ImageDriverHelper.add_asset(assets, self.big_preview_path, Role.overview, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
            asset.name = "big_preview"

        if self.quicklook_path:
            ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview, MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)

        return assets

    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_preview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)
        return assets

    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None:
            tif_for_overview = self.big_preview_path if self.big_preview_path else self.tif_path
            if AccessManager.is_local(tif_for_overview) and Driver.configuration.get('build_overview_when_local', True):
                Driver.LOGGER.debug(f"Building overview for local {tif_for_overview}")
                overview = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
                geotiff_to_jpg(tif_for_overview, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, overview.href, [1, 1, 1], Driver.configuration.get('overview_stretch', True))
                overview.size = AccessManager.get_size(overview.href)
                self.quicklook_path = overview.href
                assets.append(overview)
            elif Driver.configuration and Driver.configuration.get('build_overview_when_remote', False):
                Driver.LOGGER.debug(f"Building overview for remote {tif_for_overview}")
                overview_folder = self.assets_dir + '/capella/' + self.get_item_id(url) + '/overview'
                AccessManager.makedir(overview_folder)
                overview_path = overview_folder + '/overview.jpg'
                # File is processed locally as it significantly speeds up processing time
                with AccessManager.make_local(tif_for_overview) as local_big_preview_path:
                    overview = ImageDriverHelper.prepare_preview_asset(self, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg)
                    geotiff_to_jpg(local_big_preview_path, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, Driver.OVERVIEW_FROM_LARGE_TIFF_PCT, overview.href, [1, 1, 1], Driver.configuration.get('overview_stretch', True))
                    overview.size = AccessManager.get_size(overview.href)
                    self.quicklook_path = overview.href
                    assets.append(overview)
            else:
                Driver.LOGGER.debug("Skipping overview generation for TCI {}".format(self.big_preview_path))
        else:
            Driver.LOGGER.debug("Overview exists {}".format(self.quicklook_path))

        if self.quicklook_path is not None:
            thumbnail_type = MimeType.JPG
            thumbanil_format = AssetFormat.jpg
            if self.quicklook_path.endswith(".png"):
                thumbnail_type = MimeType.PNG
                thumbanil_format = AssetFormat.png
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, thumbnail_type, thumbanil_format)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)

        return assets

    def load_metadata(self, url: str) -> dict:
        with AccessManager.stream(self.extended_md_path) as fb:
            metadata = json.load(fb)
        return metadata

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        geometry = ImageDriverHelper.gdal_geometry(self, self.tif_path)
        Driver.LOGGER.debug(f"Extracted geometry for item {url}: {geometry}")
        if geometry is None:
            Driver.LOGGER.warning(f"No geometry found for item {url}")
            raise DriverException(f"Missing required 'geometry' for {url}")

        bbox = get_bbox(geometry["coordinates"][0])

        centroid = metadata.get("properties", {}).get("proj:centroid")
        if centroid is None and geometry is not None:
            centroid = get_centroid(geometry)

        def parse_dt(dt_str):
            if not dt_str:
                return None
            if dt_str.endswith("Z"):
                dt_str = dt_str[:-1] + "+00:00"
            return datetime.fromisoformat(dt_str).replace(tzinfo=None)


        props = metadata.get("collect", {})
        start_datetime = parse_dt(props.get("start_timestamp"))
        end_datetime = parse_dt(props.get("stop_timestamp"))

        constellation = "Capella"

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_datetime,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                constellation=constellation,
                sensor_type=SensorType.SAR.value,
                item_format=ItemFormat.capella.value,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        props = metadata.get("collect", {})
        item.properties.secondary_id = props.get("collect_id", metadata.get("id"))
        item.properties.satellite = props.get("platform", None)
        item.properties.gsd = props.get("image", {}).get("ground_range_resolution", None)
        proj = AccessManager.get_gdal_proj(self.tif_path)
        if proj:
            item.properties.proj__epsg = get_epsg(proj)
        else:
            item.properties.proj__epsg = get_epsg_from_gdal_info_gcps(self.tif_path)

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        props = metadata.get("collect", {})

        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        item.properties.view__incidence_angle = props.get("image", {}).get("center_pixel", {}).get("incidence_angle", None)
        item.properties.view__azimuth = props.get("image", {}).get("azimuth_looks", None)

        item.properties.acq__acquisition_orbit_direction = props.get("state", {}).get("direction", None)

        item.properties.sar__frequency_band = props.get("radar", {}).get("center_frequency", None)
        if item.properties.sar__frequency_band:
            item.properties.sar__frequency_band = str(item.properties.sar__frequency_band)
        item.properties.sar__center_frequency = props.get("radar", {}).get("center_frequency", None)
        if props.get("radar", {}).get("transmit_polarization") and props.get("radar", {}).get("receive_polarization"):
            item.properties.sar__polarizations = [props.get("radar", {}).get("transmit_polarization") + props.get("radar", {}).get("receive_polarization")]

        item.properties.sar__resolution_range = item.properties.gsd
        item.properties.sar__resolution_azimuth = props.get("image", {}).get("ground_azimuth_resolution", None)
        item.properties.sar__observation_direction = item.properties.acq__acquisition_orbit_direction
        item.properties.sar__looks_range = props.get("image", {}).get("range_looks", None)
        item.properties.sar__looks_azimuth = item.properties.view__azimuth
        item.properties.sar__pixel_spacing_range = props.get("image", {}).get("pixel_spacing_row", None)
        item.properties.sar__product_type = metadata.get("product_type", None)
        Driver.LOGGER.debug(f"Extracted metadata for item {item.model_dump_json(exclude_none=True, exclude_unset=True, indent=2)}")
        return item

    def __check_path__(self, path: str):
        self.__init__()
        dir_path = path

        if AccessManager.is_dir(dir_path):
            files = AccessManager.listdir(dir_path)
            for f in files:
                filename = f.name.lower()
                if not f.is_dir and filename.startswith("capella_"):
                    if filename.endswith("_thumb.png"):
                        self.quicklook_path = f.path
                    if filename.endswith("_preview.tif"):
                        self.big_preview_path = f.path
                    elif filename.endswith(".tif"):
                        self.tif_path = f.path
                    elif filename.endswith("_extended.json"):
                        self.extended_md_path = f.path
                    elif filename.endswith("_digest.json"):
                        self.digest_md_path = f.path
            return self.extended_md_path is not None and self.tif_path is not None
        return False
