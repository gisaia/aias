from importlib import metadata
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, find_or_none, geotiff_to_jpg, get_epsg_from_gdal_info,
    get_geom_bbox_centroid_from_coordinates)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
from dateutil import parser


class Driver(IngestDriver):
    ns = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}  # NOSONAR

    def __init__(self):
        super().__init__()
        self.thumbnail_path = None
        self.quicklook_path = None
        self.dim_path = None
        self.tif_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        ImageDriverHelper.add_asset(assets, self.tif_path, Role.data,
                                    MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        ImageDriverHelper.add_asset(assets, self.dim_path, Role.metadata,
                                    MimeType.JSON, AssetFormat.json, ResourceType.other)

        if self.thumbnail_path:
            ImageDriverHelper.add_asset(assets, self.thumbnail_path, Role.thumbnail,
                                        MimeType.JPG, AssetFormat.jpg, ResourceType.other, airs__managed=True)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_overview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None and AccessManager.is_local(self.tif_path):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, output_path=quicklook.href, bands_list=[1, 2, 3])
            quicklook.size = AccessManager.get_size(quicklook.href)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        if self.thumbnail_path is None and self.quicklook_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)

        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.dim_path) as local_dim_path:
            tree = ET.parse(local_dim_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        coords = []
        # Calculate bbox
        for vertex in self.__find_value__(root, './Dataset_Frame').iter('Vertex'):
            coord = [float(self.__find_value__(vertex, 'FRAME_LON').text), float(self.__find_value__(vertex, 'FRAME_LAT').text)]
            coords.append(coord)
        coords.append(coords[0])
        geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(coords)

        start_time_str = root.find("./Dataset_Sources/Source_Information/Scene_Source/START_TIME", Driver.ns)
        if start_time_str is not None:
            date_time = parser.parse(start_time_str.text)
            start_time = date_time
        else:
            date_time_str = self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE").text + self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME").text
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d%H:%M:%S")

        stop_time_str = root.find("./Dataset_Sources/Source_Information/Scene_Source/STOP_TIME", Driver.ns)
        if stop_time_str is not None:
            stop_time = parser.parse(stop_time_str.text)

        constellation = self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/MISSION").text
        mission_index = root.find("./Dataset_Sources/Source_Information/Scene_Source/MISSION_INDEX", Driver.ns)
        if mission_index is not None:
            satellite = constellation + " " + mission_index.text
        else:
            satellite = constellation
        source_id = root.find("./Dataset_Sources/Source_Information/SOURCE_ID", Driver.ns)
        if source_id is not None:
            source_id = source_id.text

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                satellite=satellite,
                sensor_type=SensorType.OPTIC.value,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.geosat.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )
        if start_time_str:
            item.properties.start_datetime = start_time
        if stop_time_str:
            item.properties.end_datetime = stop_time
        if source_id:
            item.properties.secondary_id = source_id
        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.proj__epsg = get_epsg_from_gdal_info(self.tif_path)
        item.properties.gsd = find_or_none(root, "./Dataset_Sources/Source_Information/Scene_Source/THEORETICAL_RESOLUTION", lambda x: float(x), Driver.ns)
        item.properties.processing__level = find_or_none(root, "./Production/PRODUCT_TYPE", Driver.ns)
        item.properties.secondary_id = self.tif_path.removesuffix(".tif")
        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        item.properties.instrument = find_or_none(root, "./Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT", ns=Driver.ns)
        item.properties.sensor = item.properties.constellation

        item.properties.view__incidence_angle = find_or_none(root, "./Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE", lambda x: float(x), Driver.ns)
        item.properties.view__sun_azimuth = find_or_none(root, "./Dataset_Sources/Source_Information/Scene_Source/SUN_AZIMUTH", lambda x: float(x), Driver.ns)
        item.properties.view__sun_elevation = find_or_none(root, "./Dataset_Sources/Source_Information/Scene_Source/SUN_ELEVATION", lambda x: float(x), Driver.ns)

        for param in root.iter("Quality_Parameter"):
            code = self.__find_value__(param, "./QUALITY_PARAMETER_CODE").text
            if code == "SPACEMETRIC:CLOUDCOVER_PERCENT":
                item.properties.eo__cloud_cover = find_or_none(param, "./QUALITY_PARAMETER_VALUE", lambda x: float(x))

        return item

    def __check_path__(self, path: str):
        self.__init__()

        if not AccessManager.is_dir(path):
            return False

        for file in AccessManager.listdir(path):
            if file.is_dir:
                continue

            # Check that they have the same name?
            if file.name.endswith(".dim"):
                self.dim_path = file.path
            elif file.name.endswith(".tif"):
                self.tif_path = file.path
            elif file.name.endswith(".jpg"):
                self.thumbnail_path = file.path
            elif file.name.endswith("_QL.png"):
                self.quicklook_path = file.path

        return self.dim_path is not None \
            and self.tif_path is not None \
            and os.path.basename(self.dim_path).split(".")[0] \
            == os.path.basename(self.tif_path).split(".")[0] \
            and (self.thumbnail_path is not None
                 or self.quicklook_path is not None)

    def __find_value__(self, root: ET.Element, key: str) -> ET.Element:
        value = root.find(key, Driver.ns)
        if value is None:
            raise DriverException(f"Couldn't find {key}")
        return value
