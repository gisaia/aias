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
    geotiff_to_jpg, get_epsg_from_gdal_info,
    get_geom_bbox_centroid_from_coordinates)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

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
        if self.quicklook_path:
            ImageDriverHelper.add_asset(assets, self.quicklook_path, Role.overview,
                                        MimeType.PNG, AssetFormat.png, ResourceType.other, airs__managed=True)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None:
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, 25, 25, output_path=quicklook.href, bands_list=[1, 2, 3])
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

        if self.thumbnail_path is None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, 10, 10, output_path=thumbnail.href, bands_list=[1, 2, 3])
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        with AccessManager.make_local(self.dim_path) as local_dim_path:
            tree = ET.parse(local_dim_path)
            root = tree.getroot()

        coords = []
        # Calculate bbox
        for vertex in self.__find_value__(root, './Dataset_Frame').iter('Vertex'):
            coord = [float(self.__find_value__(vertex, 'FRAME_LON').text), float(self.__find_value__(vertex, 'FRAME_LAT').text)]
            coords.append(coord)
        coords.append(coords[0])
        geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(coords)

        mission = self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/MISSION").text
        instrument = self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/INSTRUMENT").text
        date_time = self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/IMAGING_DATE").text \
            + self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/IMAGING_TIME").text
        date_time = datetime.strptime(date_time, "%Y-%m-%d%H:%M:%S")

        view__incidence_angle = float(self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/INCIDENCE_ANGLE").text)
        view__sun_azimuth = float(self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/SUN_AZIMUTH").text)
        view__sun_elevation = float(self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/SUN_ELEVATION").text)
        gsd = float(self.__find_value__(root, "./Dataset_Sources/Source_Information/Scene_Source/THEORETICAL_RESOLUTION").text)

        eo__cloud_cover = None
        for param in root.iter("Quality_Parameter"):
            code = self.__find_value__(param, "./QUALITY_PARAMETER_CODE").text
            if code == "SPACEMETRIC:CLOUDCOVER_PERCENT":
                eo__cloud_cover = float(self.__find_value__(param, "./QUALITY_PARAMETER_VALUE").text)

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                gsd=gsd,
                proj__epsg=get_epsg_from_gdal_info(self.tif_path),
                instrument=instrument,
                constellation=mission,
                sensor=mission,
                sensor_type=SensorType.OPTIC.value,
                eo__cloud_cover=eo__cloud_cover,
                view__incidence_angle=view__incidence_angle,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.geosat.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

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
        ns = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}  # NOSONAR

        value = root.find(key, ns)
        if value is None:
            raise DriverException(f"Couldn't find {key}")
        return value
