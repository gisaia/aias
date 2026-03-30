import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg,
                                                             get_epsg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.md_path = None
        self.quicklook_path = None

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration

    def identify_assets(self, url: str):
        assets: list[Asset] = []
        ImageDriverHelper.add_archive(assets, url)

        if self.quicklook_path:
            ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview, MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other)

        return assets

    def fetch_assets(self, url: str, assets: list[Asset]):
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_overview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)
        return assets

    def transform_assets(self, url: str, assets: list[Asset]):
        if self.quicklook_path is None:
            if AccessManager.is_local(self.tif_path) and Driver.configuration.get('build_overview_when_local', True):
                Driver.LOGGER.debug(f"Building overview for local TIFF {self.tif_path}")
                quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
                geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT/5, Driver.OVERVIEW_FROM_TIFF_PCT/5, output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
                quicklook.size = AccessManager.get_size(quicklook.href)
                self.quicklook_path = quicklook.href
                assets.append(quicklook)
            elif Driver.configuration and Driver.configuration.get('build_overview_when_remote', False):
                Driver.LOGGER.debug(f"Building overview for remote TIFF {self.tif_path}")
                overview_folder = self.assets_dir + '/umbra_stac/' + self.get_item_id(url) + '/overview'
                AccessManager.makedir(overview_folder)
                overview_path = overview_folder + '/overview.jpg'
                with AccessManager.make_local(self.tif_path) as local_tif_path:
                    quicklook = ImageDriverHelper.prepare_preview_asset(self, overview_path, Role.overview, MimeType.JPG, AssetFormat.jpg)
                    geotiff_to_jpg(local_tif_path, Driver.OVERVIEW_FROM_TIFF_PCT/5, Driver.OVERVIEW_FROM_TIFF_PCT/5, output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
                    quicklook.size = AccessManager.get_size(quicklook.href)
                    self.quicklook_path = quicklook.href
                    assets.append(quicklook)

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
        with AccessManager.stream(self.md_path) as fb:
            metadata = json.load(fb)

        return metadata

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        geometry = metadata["geometry"]
        bbox = metadata["bbox"]

        coordinates = geometry["coordinates"][0]
        # Remove altitude
        for idx, coords in enumerate(coordinates):
            coordinates[idx] = coords[:2]

        centroid = [
            (bbox[0] + bbox[2]) / 2.0,
            (bbox[1] + bbox[3]) / 2.0
        ]

        def parse_dt(dt_str):
            if not dt_str:
                return None
            if dt_str.endswith("Z"):
                dt_str = dt_str[:-1] + "+00:00"
            return datetime.fromisoformat(dt_str).replace(tzinfo=None)

        props = metadata.get("properties", {})
        dt_str = props.get("start_datetime") or props.get("datetime")
        start_datetime = parse_dt(dt_str)
        
        end_dt_str = props.get("end_datetime") or props.get("datetime")
        end_datetime = parse_dt(end_dt_str)

        constellation = props.get("constellation", "UMBRA").upper()

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
                item_format=ItemFormat.umbra.value,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar.value
            ),
            assets={asset.name: asset for asset in assets}
        )
        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        props = metadata.get("properties", {})
        item.properties.secondary_id = props.get("umbra:collect_id", metadata.get("id"))
        item.properties.satellite = props.get("platform", None)
        item.properties.gsd = props.get("umbra:best_resolution_azimuth_meters", None)
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        props = metadata.get("properties", {})

        item.properties.instrument = item.properties.constellation
        item.properties.sensor = item.properties.constellation
        item.properties.sensor_mode = props.get("sar:instrument_mode", None)

        item.properties.view__incidence_angle = props.get("view:incidence_angle", None)
        item.properties.view__azimuth = props.get("view:azimuth", None)

        item.properties.acq__acquisition_orbit_direction = props.get("sat:orbit_state", None)
        item.properties.acq__request_id = props.get("umbra:task_id", None)

        item.properties.sar__frequency_band = props.get("sar:frequency_band", None)
        item.properties.sar__center_frequency = props.get("sar:center_frequency", None)
        
        polarizations = props.get("sar:polarizations", None)
        if polarizations and isinstance(polarizations, list) and len(polarizations) > 0:
            item.properties.sar__polarizations = polarizations

        item.properties.sar__resolution_range = props.get("sar:resolution_range", None)
        item.properties.sar__resolution_azimuth = props.get("sar:resolution_azimuth", None)
        item.properties.sar__observation_direction = props.get("sar:observation_direction", None)

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                if not f.is_dir:
                    if f.path.lower().endswith((".tif", ".tiff")):
                        self.tif_path = f.path
                    if f.path.endswith(".stac.v2.json") or f.path.endswith(".stac.json"):
                        self.md_path = f.path
                    if f.path.endswith("-thumbnail.png"):
                        self.quicklook_path = f.path
            return self.tif_path is not None and self.md_path is not None
        return False
