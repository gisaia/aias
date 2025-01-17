import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    geotiff_to_jpg, get_epsg, get_geom_bbox_centroid, get_hash_url)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    output_folder = None

    def __init__(self):
        super().__init__()
        self.browse_path = None
        self.quicklook_path = None
        self.thumbnail_path = None
        self.tif_path = None
        self.tfw_path = None
        self.met_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.output_folder = configuration['tmp_directory']  # todo: this should use self.get_asset_filepath instead

    # Implements drivers method
    def supports(self, url: str) -> bool:
        # url variable must be a folder path begining with a /
        try:
            result = self.__check_path__(url)
            return result
        except Exception as e:
            self.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if self.browse_path is not None:
            browse_path = AccessManager.prepare(self.browse_path)
            thumbnail_path = self.output_folder + '/terrasarx/' + self.get_item_id(url) + '/thumbnail'
            os.makedirs(thumbnail_path, exist_ok=True)
            self.thumbnail_path = thumbnail_path + '/thumbnail.jpg'
            geotiff_to_jpg(browse_path, 50, 50, self.thumbnail_path)
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_file_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
            quicklook_path = self.output_folder + '/terrasarx/' + self.get_item_id(url) + '/quicklook'
            os.makedirs(quicklook_path, exist_ok=True)
            self.quicklook_path = quicklook_path + '/quicklook.jpg'
            geotiff_to_jpg(browse_path, 250, 250, self.quicklook_path)
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type=MimeType.JPG.value,
                                description=Role.overview.value, size=AccessManager.get_file_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))

            if browse_path != self.browse_path:
                os.remove(browse_path)

        assets.append(Asset(href=self.met_path, size=AccessManager.get_file_size(self.met_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.TEXT.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.tif_path, size=AccessManager.get_file_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_file_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        met_path = AccessManager.prepare(self.met_path)
        tree = ET.parse(met_path)
        root = tree.getroot()
        # Some data dont have this balise in xml metadata
        if root.find("productSpecific/geocodedImageInfo") is not None:
            ul_lat = self.__get_coord__(root, "upperLeftLatitude")
            ul_lon = self.__get_coord__(root, "upperLeftLongitude")
            ur_lat = self.__get_coord__(root, "upperRightLatitude")
            ur_lon = self.__get_coord__(root, "upperRightLongitude")
            lr_lat = self.__get_coord__(root, "lowerRightLatitude")
            lr_lon = self.__get_coord__(root, "lowerRightLongitude")
            ll_lat = self.__get_coord__(root, "lowerLeftLatitude")
            ll_lon = self.__get_coord__(root, "lowerLeftLongitude")
            geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)
            x_pixel_size = float(root.find("productSpecific/geocodedImageInfo/geoParameter/pixelSpacing/easting").text)
            y_pixel_size = float(root.find("productSpecific/geocodedImageInfo/geoParameter/pixelSpacing/northing").text)
        else:
            coords = []
            # order lower left; lower right: upper left ; upper right
            for vertex in root.findall('productInfo/sceneInfo/sceneCornerCoord'):
                coord = [float(vertex.find('lon').text), float(vertex.find('lat').text)]
                coords.append(coord)
            geometry, bbox, centroid = get_geom_bbox_centroid(coords[2][0], coords[2][1], coords[3][0], coords[3][1],
                                                              coords[1][0], coords[1][1], coords[0][0], coords[0][1])
            x_pixel_size = float(root.find("productInfo/imageDataInfo/imageRaster/columnSpacing").text)
            y_pixel_size = float(root.find("productInfo/imageDataInfo/imageRaster/rowSpacing").text)

        gsd = (x_pixel_size + y_pixel_size) / 2
        processing__level = root.find("setup/orderInfo/orderType").text
        constellation = root.find("productInfo/missionInfo/mission").text
        instrument = root.find("productInfo/missionInfo/mission").text
        sensor = root.find("productInfo/missionInfo/mission").text
        sensor_type = root.find("productInfo/acquisitionInfo/sensor").text
        view__incidence_angle = float(root.find("productInfo/sceneInfo/sceneCenterCoord/incidenceAngle").text)
        date_time = int(datetime.strptime(root.find("productInfo/sceneInfo/start/timeUTC").text, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())

        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly
        tif_path = AccessManager.prepare(self.tif_path)
        src_ds = gdal.Open(tif_path, GA_ReadOnly)
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                gsd=gsd,
                proj__epsg=get_epsg(src_ds),
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                sensor_type=sensor_type,
                view__incidence_angle=view__incidence_angle,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.terrasar.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.radar.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )

        if met_path != self.met_path:
            os.remove(met_path)
        if tif_path != self.tif_path:
            os.remove(tif_path)
        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                if f.endswith(".xml"):
                    self.met_path = os.path.join(path, f)
                    for folder in AccessManager.listdir(path):
                        # check if current folder is a folder
                        if AccessManager.is_dir(os.path.join(path, folder)):
                            if folder == "PREVIEW":
                                self.browse_path = os.path.join(path, folder, "BROWSE.tif")
                            if folder == "IMAGEDATA":
                                for file in AccessManager.listdir(os.path.join(path, folder)):
                                    if file.endswith(".tif"):
                                        self.tif_path = os.path.join(path, folder, file)
                                        tfw_path = str(Path(self.tif_path).with_suffix(".tfw"))
                                        if AccessManager.exists(tfw_path):
                                            self.tfw_path = tfw_path
                    return self.met_path is not None and self.tif_path is not None and self.browse_path is not None
        return False

    def __get_coord__(self, root, field):
        return float(root.find("productSpecific/geocodedImageInfo/geoParameter/sceneCoordsGeographic/" + field).text)
