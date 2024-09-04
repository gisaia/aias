import os
from datetime import datetime
from pathlib import Path

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    ObservationType, Properties, ResourceType,
                                    Role)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import \
    get_geom_bbox_centroid, get_hash_url, geotiff_to_jpg, get_file_size, get_epsg
import xml.etree.ElementTree as ET


class Driver(ProcDriver):
    browse_path = None
    quicklook_path = None
    thumbnail_path = None
    tif_path = None
    tfw_path = None
    h5_path = None
    h5pdf_path = None
    met_path = None
    attr_path = None
    prefix_key = None
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
            Driver.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if self.browse_path is not None:
            thumbnail_path = self.output_folder + '/' + self.get_item_id(url) + '/thumbnail'
            os.makedirs(thumbnail_path, exist_ok=True)
            self.thumbnail_path = thumbnail_path + '/thumbnail.jpg'
            geotiff_to_jpg(self.browse_path, 50, 50, self.thumbnail_path)
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                                description=Role.thumbnail.value, size=get_file_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
            quicklook_path = self.output_folder + '/' + self.get_item_id(url) + '/quicklook'
            os.makedirs(quicklook_path, exist_ok=True)
            self.quicklook_path = quicklook_path + '/quicklook.jpg'
            geotiff_to_jpg(self.browse_path, 250, 250, self.quicklook_path)
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                                description=Role.overview.value, size=get_file_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))
        assets.append(Asset(href=self.tif_path, size=get_file_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type="image/tif",
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.met_path, size=get_file_size(self.met_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type="text/xml",
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.attr_path, size=get_file_size(self.attr_path),
                            roles=[Role.metadata.value], name="attributes", type="text/xml",
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.h5_path, size=get_file_size(self.h5_path),
                            roles=[Role.metadata.value], name="h5", type="text/xml",
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        if Driver.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=get_file_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type="text/plain",
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        if Driver.h5pdf_path:
            assets.append(Asset(href=self.h5pdf_path, size=get_file_size(self.h5pdf_path),
                                roles=[Role.metadata.value], name="tfw", type="application/pdf",
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.pdf.value, asset_type=ResourceType.other.value))
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
        ul_lat = self.__get_coord__(root, self.prefix_key,"Top_Left_Geodetic_Coordinates", 0)
        ul_lon = self.__get_coord__(root, self.prefix_key,"Top_Left_Geodetic_Coordinates", 1)
        ur_lat = self.__get_coord__(root, self.prefix_key,"Top_Right_Geodetic_Coordinates", 0)
        ur_lon = self.__get_coord__(root, self.prefix_key,"Top_Right_Geodetic_Coordinates", 1)
        lr_lat = self.__get_coord__(root, self.prefix_key,"Bottom_Right_Geodetic_Coordinates", 0)
        lr_lon = self.__get_coord__(root, self.prefix_key,"Bottom_Right_Geodetic_Coordinates", 1)
        ll_lat = self.__get_coord__(root, self.prefix_key,"Bottom_Left_Geodetic_Coordinates", 0)
        ll_lon = self.__get_coord__(root, self.prefix_key,"Bottom_Left_Geodetic_Coordinates", 1)
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon,ul_lat,ur_lon,ur_lat,lr_lon,lr_lat,ll_lon,ll_lat)
        x_pixel_size = float(root.find("PAMRasterBand/Metadata/MDI[@key='"+self.prefix_key + "Column_Spacing" + "']").text)
        y_pixel_size = float(root.find("PAMRasterBand/Metadata/MDI[@key='"+self.prefix_key + "Line_Spacing" + "']").text)
        gsd = (x_pixel_size+y_pixel_size)/2
        instrument = root.find("Metadata/MDI[@key='Satellite_ID']").text
        sensor = root.find("Metadata/MDI[@key='Satellite_ID']").text
        near_incidence_angle = float(root.find("PAMRasterBand/Metadata/MDI[@key='"+self.prefix_key + "Near_Incidence_Angle" + "']").text)
        far_incidence_angle = float(root.find("PAMRasterBand/Metadata/MDI[@key='"+self.prefix_key + "Far_Incidence_Angle" + "']").text)
        view__incidence_angle = (near_incidence_angle+far_incidence_angle)/2
        date_time = int(datetime.strptime(root.find("Metadata/MDI[@key='Scene_Sensing_Start_UTC']").text[:-3], "%Y-%m-%d %H:%M:%S.%f").timestamp())
        h5_tree = ET.parse(self.h5_path)
        h5_root = h5_tree.getroot()
        processing__level = h5_root.find("ProcessingInfo/ProcessingLevel").text
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly
        src_ds = gdal.Open(self.tif_path, GA_ReadOnly)
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
                constellation="COSMO-SkyMed",
                sensor=sensor,
                sensor_type="SAR",
                view__incidence_angle=view__incidence_angle,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.csk.value,
                main_asset_format=AssetFormat.geotiff.value,
                observation_type=ObservationType.radar.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(file_path: str):
        Driver.tif_path = None
        Driver.met_path = None
        Driver.attr_path = None
        Driver.browse_path = None
        Driver.prefix_key = None
        Driver.h5_path = None
        Driver.h5pdf_path = None
        Driver.quicklook_path = None
        Driver.thumbnail_path = None
        valid_and_exist = os.path.isfile(file_path) and os.path.exists(file_path)
        file_name = os.path.basename(file_path)
        path = os.path.dirname(file_path)
        if valid_and_exist is True and file_name.endswith(".tif") and file_name.find(".QLK.") < 0:
            Driver.tif_path = file_path
            if os.path.isfile(file_path + '.aux.xml') and os.path.exists(file_path + '.aux.xml'):
                Driver.met_path = file_path + '.aux.xml'
            attr_path = path + '/' + file_name.split(".")[0] + ".attribs.xml"
            if os.path.isfile(attr_path) and os.path.exists(attr_path):
                Driver.attr_path = attr_path
            browse_path = path + '/' + file_name.split(".")[0] + "." + file_name.split(".")[1] + '.QLK.tif'
            if os.path.isfile(browse_path) and os.path.exists(browse_path):
                Driver.browse_path = browse_path
            if len(file_name.split(".")) > 2:
                Driver.prefix_key = file_name.split(".")[1] + "_" + file_name.split(".")[2] + "_"
            h5_path = path + '/' + "DFDN_" + file_name.split(".")[0] + ".h5.xml"
            if os.path.isfile(h5_path) and os.path.exists(h5_path):
                Driver.h5_path = h5_path
            h5pdf_path = path + '/' + "DFDN_" + file_name.split(".")[0] + ".h5.pdf"
            if os.path.isfile(h5pdf_path) and os.path.exists(h5pdf_path):
                Driver.h5pdf_path = h5pdf_path
            tfw_path = Path(Driver.tif_path).with_suffix(".tfw")
            if tfw_path.exists():
                Driver.tfw_path = str(tfw_path)
            return Driver.met_path is not None and \
                   Driver.tif_path is not None and \
                   Driver.attr_path is not None and \
                   Driver.prefix_key is not None and \
                   Driver.browse_path is not None and \
                   Driver.h5_path is not None
        return False

    @staticmethod
    def __get_coord__(root,prefix,value,index):
        field = prefix + value
        return float(root.find("PAMRasterBand/Metadata/MDI[@key='"+field+"']").text.split(" ")[index])