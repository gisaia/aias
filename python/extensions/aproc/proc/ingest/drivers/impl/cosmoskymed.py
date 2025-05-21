import os
import xml.etree.ElementTree as ET
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    geotiff_to_jpg, get_epsg, get_geom_bbox_centroid, get_hash_url)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    output_folder: str | None = None  # todo: this should use self.get_asset_filepath instead

    def __init__(self):
        super().__init__()
        self.tif_path = None
        self.tfw_path = None
        self.met_path = None
        self.attr_path = None
        self.browse_path = None
        self.prefix_key = None
        self.h5_path = None
        self.h5pdf_path = None
        self.quicklook_path = None
        self.thumbnail_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.output_folder = configuration['tmp_directory']

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
            thumbnail_path = Driver.output_folder + '/' + self.get_item_id(url) + '/thumbnail'
            AccessManager.makedir(thumbnail_path)
            self.thumbnail_path = thumbnail_path + '/thumbnail.jpg'
            geotiff_to_jpg(self.browse_path, 50, 50, self.thumbnail_path)
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))

            quicklook_path = Driver.output_folder + '/' + self.get_item_id(url) + '/quicklook'
            AccessManager.makedir(quicklook_path)
            self.quicklook_path = quicklook_path + '/quicklook.jpg'
            geotiff_to_jpg(self.browse_path, 250, 250, self.quicklook_path)
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type=MimeType.JPG.value,
                                description=Role.overview.value, size=AccessManager.get_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))

        assets.append(Asset(href=self.tif_path, size=AccessManager.get_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.met_path, size=AccessManager.get_size(self.met_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.attr_path, size=AccessManager.get_size(self.attr_path),
                            roles=[Role.metadata.value], name="attributes", type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.h5_path, size=AccessManager.get_size(self.h5_path),
                            roles=[Role.metadata.value], name="h5", type=MimeType.XML.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        if self.h5pdf_path:
            assets.append(Asset(href=self.h5pdf_path, size=AccessManager.get_size(self.h5pdf_path),
                                roles=[Role.metadata.value], name=Role.metadata.value + "_pdf", type=MimeType.PDF.value,
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
        with AccessManager.make_local(self.met_path) as local_met_path:
            tree = ET.parse(local_met_path)
            root = tree.getroot()
        ul_lat = self.__get_coord__(root, self.prefix_key, "Top_Left_Geodetic_Coordinates", 0)
        ul_lon = self.__get_coord__(root, self.prefix_key, "Top_Left_Geodetic_Coordinates", 1)
        ur_lat = self.__get_coord__(root, self.prefix_key, "Top_Right_Geodetic_Coordinates", 0)
        ur_lon = self.__get_coord__(root, self.prefix_key, "Top_Right_Geodetic_Coordinates", 1)
        lr_lat = self.__get_coord__(root, self.prefix_key, "Bottom_Right_Geodetic_Coordinates", 0)
        lr_lon = self.__get_coord__(root, self.prefix_key, "Bottom_Right_Geodetic_Coordinates", 1)
        ll_lat = self.__get_coord__(root, self.prefix_key, "Bottom_Left_Geodetic_Coordinates", 0)
        ll_lon = self.__get_coord__(root, self.prefix_key, "Bottom_Left_Geodetic_Coordinates", 1)
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)
        x_pixel_size = float(root.find("PAMRasterBand/Metadata/MDI[@key='" + self.prefix_key + "Column_Spacing" + "']").text)
        y_pixel_size = float(root.find("PAMRasterBand/Metadata/MDI[@key='" + self.prefix_key + "Line_Spacing" + "']").text)
        gsd = (x_pixel_size + y_pixel_size) / 2
        instrument = root.find("Metadata/MDI[@key='Satellite_ID']").text
        sensor = root.find("Metadata/MDI[@key='Satellite_ID']").text
        near_incidence_angle = float(root.find("PAMRasterBand/Metadata/MDI[@key='" + self.prefix_key + "Near_Incidence_Angle" + "']").text)
        far_incidence_angle = float(root.find("PAMRasterBand/Metadata/MDI[@key='" + self.prefix_key + "Far_Incidence_Angle" + "']").text)
        view__incidence_angle = (near_incidence_angle + far_incidence_angle) / 2
        date_time = int(datetime.strptime(root.find("Metadata/MDI[@key='Scene_Sensing_Start_UTC']").text[:-3], "%Y-%m-%d %H:%M:%S.%f").timestamp())
        h5_tree = ET.parse(self.h5_path)
        h5_root = h5_tree.getroot()
        processing__level = h5_root.find("ProcessingInfo/ProcessingLevel").text

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

    def __check_path__(self, file_path: str):
        self.__init__()
        file_name = os.path.basename(file_path)
        path = AccessManager.dirname(file_path)
        if AccessManager.is_file(file_path) and file_name.endswith(".tif") and file_name.find(".QLK.") < 0:
            self.tif_path = file_path
            met_path = file_path + '.aux.xml'
            if AccessManager.is_file(met_path):
                self.met_path = met_path
            attr_path = path + '/' + file_name.split(".")[0] + ".attribs.xml"
            if AccessManager.is_file(attr_path):
                self.attr_path = attr_path
            browse_path = path + '/' + file_name.split(".")[0] + "." + file_name.split(".")[1] + '.QLK.tif'
            if AccessManager.is_file(browse_path):
                self.browse_path = browse_path
            if len(file_name.split(".")) > 2:
                self.prefix_key = file_name.split(".")[1] + "_" + file_name.split(".")[2] + "_"
            h5_path = path + '/' + "DFDN_" + file_name.split(".")[0] + ".h5.xml"
            if AccessManager.is_file(h5_path):
                self.h5_path = h5_path
            h5pdf_path = path + '/' + "DFDN_" + file_name.split(".")[0] + ".h5.pdf"
            if AccessManager.is_file(h5pdf_path):
                self.h5pdf_path = h5pdf_path
            tfw_path = os.path.splitext(self.tif_path)[0] + ".tfw"
            if AccessManager.exists(tfw_path):
                self.tfw_path = tfw_path
            return (
                self.met_path is not None
                and self.tif_path is not None
                and self.attr_path is not None
                and self.prefix_key is not None
                and self.browse_path is not None
                and self.h5_path is not None
            )
        return False

    def __get_coord__(self, root, prefix, value, index):
        field = prefix + value
        return float(root.find("PAMRasterBand/Metadata/MDI[@key='" + field + "']").text.split(" ")[index])
