import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, get_epsg_from_gdal_info,
    get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.md_path = None
        self.tif_path = None
        self.quicklook_path = None
        self.thumbnail_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data,
                                    MimeType.GEOTIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.md_path, Role.metadata,
                                    MimeType.XML, AssetFormat.xml, ResourceType.other)
        ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview,
                                    MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)

        if self.thumbnail_path:
            ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail,
                                        MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        quicklook = ImageDriverHelper.make_local_overview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
        self.quicklook_path = quicklook.href
        assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.thumbnail_path is None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR_LARGE)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.md_path) as local_md_path:
            tree = ET.parse(local_md_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        [_, _, ul_lat, ul_lon] = root.find("coord_first_near").text.split(" ")
        [_, _, ur_lat, ur_lon] = root.find("coord_first_far").text.split(" ")
        [_, _, lr_lat, lr_lon] = root.find("coord_last_far").text.split(" ")
        [_, _, ll_lat, ll_lon] = root.find("coord_last_near").text.split(" ")

        geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(float(ul_lon), float(ul_lat), float(ur_lon), float(ur_lat), float(lr_lon), float(lr_lat), float(ll_lon), float(ll_lat))

        start_time = root.find("acquisition_start_utc").text
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
        stop_time = root.find("acquisition_end_utc").text
        stop_time = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%f")

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=start_time,
                start_datetime=start_time,
                end_datetime=stop_time,
                constellation="ICEYE",
                sensor_type=SensorType.SAR.value,
                item_format=ItemFormat.iceye,
                item_type=ResourceType.gridded.value,
                main_asset_format=AssetFormat.geotiff,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.satellite = find_or_none(root, "satellite_name")
        item.properties.processing__level = find_or_none(root, "product_level")
        item.properties.secondary_id = find_or_none(root, "product_name")
        range_spacing = find_or_none(root, "range_spacing", lambda x: float(x))
        azimuth_spacing = find_or_none(root, "azimuth_spacing", lambda x: float(x))
        if range_spacing and azimuth_spacing:
            item.properties.gsd = (range_spacing + azimuth_spacing) / 2

        item.properties.proj__epsg = get_epsg_from_gdal_info(self.tif_path)

        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.instrument = item.properties.satellite
        item.properties.sensor = item.properties.satellite

        item.properties.acq__acquisition_orbit_direction = find_or_none(root, "orbit_direction")
        item.properties.acq__acquisition_orbit = find_or_none(root, "orbit_absolute_number")
        item.properties.sar__polarizations = find_or_none(root, "polarization", lambda x: [x.upper()])

        return item

    def __check_path__(self, path: str):
        self.__init__()

        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if file.name.startswith("ICEYE") and file.name.endswith(".tif"):
                    self.tif_path = file.path
                elif file.name.startswith("ICEYE") and file.name.endswith(".xml"):
                    self.md_path = file.path
                elif file.name.startswith("ICEYE") and file.name.find("QUICKLOOK") != -1 and file.name.endswith(".png"):
                    self.quicklook_path = file.path
                elif file.name.startswith("ICEYE") and file.name.find("THUMBNAIL") != -1 and file.name.endswith(".png"):
                    self.thumbnail_path = file.path

            return self.tif_path is not None \
                and self.md_path is not None \
                and self.quicklook_path is not None

        return False
