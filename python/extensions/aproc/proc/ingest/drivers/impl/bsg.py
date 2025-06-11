import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat, MimeType,
                                    Properties, ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (get_epsg,
                                                             get_hash_url)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.pan_tif_path = None
        self.md_path = None
        self.thumbnail_path = None

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def supports(self, url: str) -> bool:
        try:
            result = self.__check_path__(url)
            return result
        except Exception as e:
            self.LOGGER.warn(e)
            return False

    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    def identify_assets(self, url: str):
        assets: list[Asset] = []

        if self.thumbnail_path:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.PNG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.png.value))
        ImageDriverHelper.add_overview_if_you_can(self, self.tif_path, Role.overview, self.overview_size, assets)

        assets.append(Asset(href=self.tif_path, size=AccessManager.get_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.pan_tif_path, size=AccessManager.get_size(self.pan_tif_path),
                            roles=[Role.data.value], name=Role.pan_sharpened.value, type=MimeType.TIFF.value,
                            description=Role.pan_sharpened.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.md_path, size=AccessManager.get_size(self.md_path),
                      roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.JSON.value,
                      description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.json.value, asset_type=ResourceType.other.value))
        return assets

    def fetch_assets(self, url: str, assets: list[Asset]):
        return assets

    def transform_assets(self, url: str, assets: list[Asset]):
        return assets

    def to_item(self, url: str, assets: list[Asset]):
        import shapely

        with AccessManager.make_local(self.md_path) as local_md_path:
            with open(local_md_path, 'r') as f:
                data = json.load(f)

        geometry = data["geometry"]
        centroid = [*shapely.centroid(shapely.from_geojson(json.dumps(geometry))).coords]

        coordinates = geometry["coordinates"][0]
        bbox = [min(map(lambda xy: xy[0], coordinates)),
                min(map(lambda xy: xy[1], coordinates)),
                max(map(lambda xy: xy[0], coordinates)),
                max(map(lambda xy: xy[1], coordinates))]

        date = datetime.strptime(data["acquisitionDate"], "%Y-%m-%dT%H:%M:%S.%f")
        constellation = "BlackSkyGlobal"
        sensor = data["sensorName"]
        gsd = data["gsd"]

        view__off_nadir = data["offNadirAngle"]
        view__sun_azimuth = data["sunAzimuth"]
        view__sun_elevation = data["sunElevation"]

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=[centroid[0][0], centroid[0][1]],
            properties=Properties(
                datetime=date,
                constellation=constellation,
                satellite=constellation,
                instrument=constellation,
                sensor=sensor,
                sensor_type=SensorType.SAR,
                gsd=gsd,
                item_format=ItemFormat.bsg.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                view__off_nadir=view__off_nadir,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
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
                    if f.path.lower().endswith("ortho.tif"):
                        self.tif_path = f.path
                    if f.path.lower().endswith("ortho-pan.tif"):
                        self.pan_tif_path = f.path
                    if f.path.endswith("_metadata.json"):
                        self.md_path = f.path
                    if f.path.endswith("_browse.png"):
                        self.thumbnail_path = f.path
            return self.tif_path is not None and self.pan_tif_path is not None and self.md_path is not None
        return False
