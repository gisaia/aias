import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Properties, ResourceType, Role,
                                    SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import get_epsg
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.md_path = None
        self.thumbnail_path = None

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    def identify_assets(self, url: str):
        assets: list[Asset] = []

        if self.thumbnail_path:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.PNG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.png.value))

        assets.append(Asset(href=self.tif_path, size=AccessManager.get_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.md_path, size=AccessManager.get_size(self.md_path),
                      roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.JSON.value,
                      description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.json.value, asset_type=ResourceType.other.value))
        return assets

    def fetch_assets(self, url: str, assets: list[Asset]):
        ImageDriverHelper.add_overview_if_you_can(self, self.tif_path, Role.overview, self.overview_size, assets)
        return assets

    def transform_assets(self, url: str, assets: list[Asset]):
        return assets

    def to_item(self, url: str, assets: list[Asset]):
        with AccessManager.make_local(self.md_path) as local_md_path:
            with open(local_md_path, 'r') as f:
                data = json.load(f)
                data_take = data["collects"][0]

        geometry = data_take["footprintPolygonLla"]
        centroid = data_take["sceneCenterPointLla"]["coordinates"][:2]

        coordinates = geometry["coordinates"][0]
        bbox = [min(map(lambda xy: xy[0], coordinates)),
                min(map(lambda xy: xy[1], coordinates)),
                max(map(lambda xy: xy[0], coordinates)),
                max(map(lambda xy: xy[1], coordinates))]
        # Remove altitude
        for idx, coords in enumerate(coordinates):
            coordinates[idx] = coords[:2]

        start_datetime = datetime.strptime(data_take["startAtUTC"].split("+")[0], "%Y-%m-%dT%H:%M:%S")
        end_datetime = datetime.strptime(data_take["endAtUTC"].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f")
        constellation = "UMBRA"
        satellite = data["umbraSatelliteName"]
        sensor_mode = data["imagingMode"]
        gsd = data["baseIpr"]
        view__incidence_angle = data_take["angleIncidenceDegrees"]
        view__azimuth = data_take["angleAzimuthDegrees"]
        acq__acquisition_orbit_direction = data_take["satelliteTrack"]
        acq__acquisition_type = data["orderType"]
        acq__request_id = data_take["taskId"]
        sar__frequency_band = data_take["radarBand"]
        sar__center_frequency = data_take["radarCenterFrequencyHz"]
        sar__polarizations = data_take["polarizations"]
        sar__resolution_range = data_take["maxGroundResolution"]["rangeMeters"]
        sar__resolution_azimuth = data_take["maxGroundResolution"]["azimuthMeters"]
        sar__observation_direction = data_take["observationDirection"]

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_datetime,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                constellation=constellation,
                satellite=satellite,
                instrument=constellation,
                sensor=constellation,
                sensor_type=SensorType.SAR,
                sensor_mode=sensor_mode,
                gsd=gsd,
                item_format=ItemFormat.umbra.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                view__incidence_angle=view__incidence_angle,
                view__azimuth=view__azimuth,
                acq__acquisition_orbit_direction=acq__acquisition_orbit_direction,
                acq__acquisition_type=acq__acquisition_type,
                acq__request_id=acq__request_id,
                sar__frequency_band=sar__frequency_band,
                sar__center_frequency=sar__center_frequency,
                sar__polarizations=sar__polarizations,
                sar__resolution_range=sar__resolution_range,
                sar__resolution_azimuth=sar__resolution_azimuth,
                sar__observation_direction=sar__observation_direction,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.tif_path)),
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
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
                        self.thumbnail_path = f.path
            return self.tif_path is not None and self.md_path is not None
        return False
