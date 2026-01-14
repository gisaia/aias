import json
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image, geotiff_to_jpg,
                                                             get_bbox,
                                                             get_centroid,
                                                             get_epsg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.pan_tif_path = None
        self.md_path = None
        self.quicklook_path = None

    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    def identify_assets(self, url: str):
        assets: list[Asset] = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.pan_tif_path, Role.pan_sharpened, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata, MimeType.JSON, AssetFormat.json, ResourceType.other)
        return assets

    def fetch_assets(self, url: str, assets: list[Asset]):
        # Make the quicklook local to downsample it
        if self.quicklook_path is not None:
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

    def load_metadata(self, url: str) -> object:
        with AccessManager.stream(self.md_path) as fb:
            md = json.load(fb)

        return md

    def build_core_item(self, url: str, assets: list[Asset], metadata: object) -> Item:
        geometry = metadata["geometry"]
        centroid = get_centroid(geometry)
        bbox = get_bbox(geometry["coordinates"][0])

        date = datetime.strptime(metadata["acquisitionDate"], "%Y-%m-%dT%H:%M:%S.%f")

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=[centroid[0][0], centroid[0][1]],
            properties=Properties(
                datetime=date,
                constellation="BlackSkyGlobal",
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.bsg.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic,
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: object) -> Item:
        item.properties.satellite = item.properties.constellation
        item.properties.gsd = metadata["gsd"]
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: object) -> Item:
        item.properties.instrument = item.properties.constellation
        item.properties.sensor = metadata["sensorName"]

        item.properties.view__off_nadir = metadata["offNadirAngle"]
        item.properties.view__sun_azimuth = metadata["sunAzimuth"]
        item.properties.view__sun_elevation = metadata["sunElevation"]

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                if not f.is_dir:
                    if f.path.lower().endswith("ortho.tif"):
                        self.tif_path = f.path
                    elif f.path.lower().endswith("ortho-pan.tif"):
                        self.pan_tif_path = f.path
                    elif f.path.endswith("_metadata.json"):
                        self.md_path = f.path
                    elif f.path.endswith("_browse.png"):
                        self.quicklook_path = f.path
            return self.tif_path is not None and self.pan_tif_path is not None and self.md_path is not None
        return False
