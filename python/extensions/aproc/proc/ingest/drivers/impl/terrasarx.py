import os
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg, get_epsg, get_geom_bbox_centroid_from_corners)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.browse_path = None
        self.tif_path = None
        self.tfw_path = None
        self.met_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        assets.append(Asset(href=self.met_path, size=AccessManager.get_size(self.met_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.TEXT.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.tif_path, size=AccessManager.get_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        ImageDriverHelper.add_asset(assets, self.browse_path, Role.visual, MimeType.TIFF, AssetFormat.geotiff, ResourceType.gridded)
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
        geotiff_to_jpg(self.browse_path, Driver.OVERVIEW_FROM_BROWSE_PCT, Driver.OVERVIEW_FROM_BROWSE_PCT, quicklook.href)
        quicklook.size = AccessManager.get_size(quicklook.href)
        assets.append(quicklook)

        thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
        downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
        thumbnail.size = AccessManager.get_size(thumbnail.href)
        assets.append(thumbnail)
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        with AccessManager.make_local(self.met_path) as local_met_path:
            tree = ET.parse(local_met_path)
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
            geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)
            x_pixel_size = float(root.find("productSpecific/geocodedImageInfo/geoParameter/pixelSpacing/easting").text)
            y_pixel_size = float(root.find("productSpecific/geocodedImageInfo/geoParameter/pixelSpacing/northing").text)
        else:
            coords = []
            # order lower left; lower right: upper left ; upper right
            for vertex in root.findall('productInfo/sceneInfo/sceneCornerCoord'):
                coord = [float(vertex.find('lon').text), float(vertex.find('lat').text)]
                coords.append(coord)
            geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(coords[2][0], coords[2][1], coords[3][0], coords[3][1],
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

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                gsd=gsd,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.tif_path)),
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
            assets={asset.name: asset for asset in assets}
        )

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for f in AccessManager.listdir(path):
                if f.name.endswith(".xml"):
                    self.met_path = f.path
                    for folder in AccessManager.listdir(path):
                        if folder.is_dir:
                            if folder.name == "PREVIEW":
                                self.browse_path = os.path.join(folder.path, "BROWSE.tif")
                            if folder.name == "IMAGEDATA":
                                for file in AccessManager.listdir(folder.path):
                                    if file.name.endswith(".tif"):
                                        self.tif_path = file.path
                                    if file.name.endswith(".tfw"):
                                        self.tfw_path = file.path

                    return self.met_path is not None and self.tif_path is not None and self.browse_path is not None
        return False

    def __get_coord__(self, root, field):
        return float(root.find("productSpecific/geocodedImageInfo/geoParameter/sceneCoordsGeographic/" + field).text)
