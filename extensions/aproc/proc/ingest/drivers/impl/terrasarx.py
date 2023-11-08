import os
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    ObservationType, Properties, ResourceType,
                                    Role)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import \
    get_geom_bbox_centroid, get_hash_url, geotiff_to_jpg
import xml.etree.ElementTree as ET


class Driver(ProcDriver):
    browse_path = None
    quicklook_path = None
    thumbnail_path = None
    tif_path = None
    met_path = None
    output_folder = None
    # Implements drivers method
    def init(configuration: Configuration):
        Driver.output_folder = configuration['tmp_directory']
        return

    # Implements drivers method
    def supports(url: str) -> bool:
        # url variable must be a folder path begining with a /
        try:
            result = Driver.__check_path__(url)
            return result
        except Exception as e:
            Driver.LOGGER.debug(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if self.browse_path is not None:
            thumbnail_path = self.output_folder +'/terrasarx/'+ self.get_item_id(url) +'/thumbnail'
            os.makedirs(thumbnail_path, exist_ok=True)
            self.thumbnail_path = thumbnail_path +'/thumbnail.jpg'
            geotiff_to_jpg(self.browse_path,50,50,self.thumbnail_path)
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                                description=Role.thumbnail.value))
            quicklook_path = self.output_folder+'/terrasarx/'+  self.get_item_id(url) +'/quicklook'
            os.makedirs(quicklook_path, exist_ok=True)
            self.quicklook_path = quicklook_path +'/quicklook.jpg'
            geotiff_to_jpg(self.browse_path,250,250,self.quicklook_path)
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                                description=Role.overview.value))
        assets.append(Asset(href=self.met_path,
                            roles=[Role.metadata.value], name=Role.metadata.value, type="text/xml",
                            description=Role.metadata.value, airs__managed=False))

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
        tree = ET.parse(self.met_path)
        root = tree.getroot()
        ul_lat = self.__get_coord__(root, "upperLeftLatitude")
        ul_lon = self.__get_coord__(root, "upperLeftLongitude")
        ur_lat = self.__get_coord__(root, "upperRightLatitude")
        ur_lon = self.__get_coord__(root, "upperRightLongitude")
        lr_lat = self.__get_coord__(root, "lowerRightLatitude")
        lr_lon = self.__get_coord__(root, "lowerRightLongitude")
        ll_lat = self.__get_coord__(root, "lowerLeftLatitude")
        ll_lon = self.__get_coord__(root, "lowerLeftLongitude")
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon,ul_lat,ur_lon,ur_lat,lr_lon,lr_lat,ll_lon,ll_lat)
        x_pixel_size = float(root.find("productSpecific/geocodedImageInfo/geoParameter/pixelSpacing/easting").text)
        y_pixel_size = float(root.find("productSpecific/geocodedImageInfo/geoParameter/pixelSpacing/northing").text)
        gsd = (x_pixel_size+y_pixel_size)/2
        processing__level = root.find("setup/orderInfo/orderType").text
        constellation = root.find("productInfo/missionInfo/mission").text
        instrument = root.find("productInfo/missionInfo/mission").text
        sensor = root.find("productInfo/missionInfo/mission").text
        sensor_type = root.find("productInfo/acquisitionInfo/sensor").text
        view__incidence_angle = float(root.find("productInfo/sceneInfo/sceneCenterCoord/incidenceAngle").text)
        date_time =  int(datetime.strptime(root.find("productInfo/sceneInfo/start/timeUTC").text, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                gsd=gsd,
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                sensor_type=sensor_type,
                view__incidence_angle=view__incidence_angle,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.terrasar.value,
                main_asset_format=AssetFormat.geotiff.value,
                observation_type=ObservationType.radar.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(file_path: str):
        Driver.tif_path = None
        Driver.met_path = None
        Driver.browse_path = None
        valid_and_exist = os.path.isfile(file_path) and os.path.exists(file_path)
        file_name = os.path.basename(file_path)
        path = os.path.dirname(file_path)
        if valid_and_exist is True and file_name.endswith(".xml"):
            Driver.met_path = file_path
            for folder in os.listdir(path):
                # check if current folder is a folder
                if os.path.isdir(os.path.join(path, folder)):
                    if folder == "PREVIEW":
                        Driver.browse_path = os.path.join(path, folder, "BROWSE.tif")
                    if folder == "IMAGEDATA":
                        for file in os.listdir(os.path.join(path, folder)):
                            if file.endswith(".tif"):
                                Driver.tif_path = os.path.join(path, folder, file)
            return Driver.met_path is not None and \
                   Driver.tif_path is not None and \
                   Driver.browse_path is not None
        else:
            Driver.LOGGER.debug("The reference {} is not a file or does not exist.".format(path))
            return False

    @staticmethod
    def __get_coord__(root,field):
        return float(root.find("productSpecific/geocodedImageInfo/geoParameter/sceneCoordsGeographic/"+field).text)