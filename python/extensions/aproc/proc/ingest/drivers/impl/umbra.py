import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Properties, ResourceType, Role,
                                    SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg,
                                                             get_epsg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.md_path = None
        self.quicklook_path = None

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

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
        if self.quicklook_path is None and AccessManager.is_local(self.tif_path):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, output_path=quicklook.href)
            quicklook.size = AccessManager.get_size(quicklook.href)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        if self.quicklook_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> dict:
        with AccessManager.stream(self.md_path) as fb:
            metadata = json.loads(fb)

        return metadata

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        data_take = metadata["collects"][0]

        geometry = data_take["footprintPolygonLla"]
        centroid = data_take["sceneCenterPointLla"]["coordinates"][:2]

        coordinates = geometry["coordinates"][0]
        bbox = [min(map(lambda xy: xy[0], coordinates)),
                min(map(lambda xy: xy[1], coordinates)),
                max(map(lambda xy: xy[0], coordinates)),
                max(map(lambda xy: xy[1], coordinates))]

        start_datetime = datetime.strptime(data_take["startAtUTC"].split("+")[0], "%Y-%m-%dT%H:%M:%S")
        end_datetime = datetime.strptime(data_take["endAtUTC"].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f")
        constellation = "UMBRA"

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_datetime,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                constellation=constellation,
                sensor_type=SensorType.SAR,
                item_format=ItemFormat.umbra.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value
            ),
            assets={asset.name: asset for asset in assets}
        )
        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        item.properties.secondary_id = metadata.get("collects", [{}])[0].get("id", None)
        item.properties.satellite = metadata.get("umbraSatelliteName", None)
        item.properties.gsd = metadata.get("baseIpr", None)
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        # Used in build_core_item so it is a dictionary
        data_take: dict = metadata["collects"][0]

        item.properties.instrument = item.properties.constellation
        item.properties.sensor = item.properties.constellation
        item.properties.sensor_mode = metadata.get("imagingMode", None)

        item.properties.view__incidence_angle = data_take.get("angleIncidenceDegrees", None)
        item.properties.view__azimuth = data_take.get("angleAzimuthDegrees", None)

        item.properties.acq__acquisition_orbit_direction = data_take.get("satelliteTrack", None)
        item.properties.acq__acquisition_type = metadata.get("orderType", None)
        item.properties.acq__request_id = data_take.get("taskId", None)

        item.properties.sar__frequency_band = data_take.get("radarBand", None)
        item.properties.sar__center_frequency = data_take.get("radarCenterFrequencyHz", None)
        polarization = data_take.get("polarizations", None)
        if polarization:
            item.properties.sar__polarizations = polarization.upper()
        item.properties.sar__resolution_range = data_take.get("maxGroundResolution", {}).get("rangeMeters", None)
        item.properties.sar__resolution_azimuth = data_take.get("maxGroundResolution", {}).get("azimuthMeters", None)
        item.properties.sar__observation_direction = data_take.get("observationDirection", None)

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                if not f.is_dir:
                    if f.path.lower().endswith((".tif", ".tiff")):
                        self.tif_path = f.path
                    if f.path.endswith("_METADATA.json"):
                        self.md_path = f.path
                    if f.path.endswith("-thumbnail.png"):
                        self.quicklook_path = f.path
            return self.tif_path is not None and self.md_path is not None
        return False
