import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Properties, ResourceType, Role,
                                    SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (get_bbox,
                                                             get_centroid,
                                                             get_epsg)
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

    def identify_assets(self, url: str):
        assets: list[Asset] = []
        ImageDriverHelper.add_archive(assets, url)

        if self.thumbnail_path:
            ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail, MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.pan_tif_path, Role.pan_sharpened, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other)
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

        geometry = data["geometry"]
        centroid = get_centroid(geometry)
        bbox = get_bbox(geometry["coordinates"][0])

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
                sensor_type=SensorType.OPTIC,
                gsd=gsd,
                item_format=ItemFormat.bsg.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                view__off_nadir=view__off_nadir,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.tif_path)),
            ),
            assets={asset.name: asset for asset in assets}
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
