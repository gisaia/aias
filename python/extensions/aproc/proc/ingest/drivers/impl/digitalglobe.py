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
    downsample_image, find_or_none, geotiff_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_corners, setup_gdal)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.quicklook_path = None
        self.xml_path = None
        self.til_path = None
        self.tif_path = None
        self.imd_path = None
        self.tfw_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        assets.append(Asset(href=self.tif_path, size=AccessManager.get_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF.value,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(Asset(href=self.xml_path, size=AccessManager.get_size(self.xml_path),
                      roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
                      description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.til_path, size=AccessManager.get_size(self.til_path),
                      roles=[Role.metadata.value], name=Role.metadata.value + "_imd", type=MimeType.PVL.value,
                      description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.pvl.value, asset_type=ResourceType.other.value))
        assets.append(Asset(href=self.imd_path, size=AccessManager.get_size(self.imd_path),
                      roles=[Role.metadata.value], name=Role.metadata.value + "_til", type=MimeType.PVL.value,
                      description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.pvl.value, asset_type=ResourceType.other.value))
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_size(self.tfw_path),
                                roles=[Role.extent.value], name=Role.extent.value, type=MimeType.TEXT.value,
                                description=Role.extent.value, airs__managed=False, asset_format=AssetFormat.tfw.value, asset_type=ResourceType.other.value))
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_overview_asset(self, url, self.quicklook_path, MimeType.JPG, AssetFormat.jpg)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None and AccessManager.is_local(self.tif_path):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href)
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
        with AccessManager.make_local(self.xml_path) as local_xml_path:
            tree = ET.parse(local_xml_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], metadata: ET.Element) -> Item:
        from osgeo import ogr

        # Calculate bbox
        ul_lat = float(metadata.find("./TIL/TILE/ULLAT").text)
        ul_lon = float(metadata.find("./TIL/TILE/ULLON").text)
        ur_lat = float(metadata.find("./TIL/TILE/URLAT").text)
        ur_lon = float(metadata.find("./TIL/TILE/URLON").text)
        lr_lat = float(metadata.find("./TIL/TILE/LRLAT").text)
        lr_lon = float(metadata.find("./TIL/TILE/LRLON").text)
        ll_lat = float(metadata.find("./TIL/TILE/LLLAT").text)
        ll_lon = float(metadata.find("./TIL/TILE/LLLON").text)
        geometry, bbox, centroid = get_geom_bbox_centroid_from_corners(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)

        # Overwrite geometry and centroid if GIS_FILE is present with order shape file
        d = AccessManager.dirname(url)
        if AccessManager.is_dir(os.path.join(d, "GIS_FILE")):
            for file in AccessManager.listdir(os.path.join(d, "GIS_FILES")):
                if file.name.endswith("_ORDER_SHAPE.shp"):
                    setup_gdal()

                    with AccessManager.make_local(os.path.join(d, "GIS_FILES", file.name)) as order_shape_file:
                        ogr_driver = ogr.GetDriverByName("ESRI Shapefile")
                        component_source = ogr_driver.Open(order_shape_file, 0)  # read-only
                        layer = component_source.GetLayer()
                        component_feature = layer.GetNextFeature()
                        component_geometry = component_feature.geometry()
                        geometry = component_feature.ExportToJson(as_object=True)["geometry"]
                        centroid_geom = component_geometry.Centroid()

                    centroid_geom_list = str(centroid_geom).replace("(", "").replace(")", "").split(" ")
                    centroid = [float(centroid_geom_list[1]), float(centroid_geom_list[2])]
                    break

        date_time_str = metadata.find("./IMD/MAP_PROJECTED_PRODUCT/EARLIESTACQTIME").text
        date_time = int(datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())

        constellation = metadata.find("./IMD/IMAGE/SATID").text

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.digitalglobe.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value,
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: ET.Element) -> Item:
        item.properties.processing__level = find_or_none(metadata, "./IMD/PRODUCTLEVEL")
        item.properties.gsd = find_or_none(metadata, "./IMD/IMAGE/MEANCOLLECTEDGSD", lambda x: float(x))
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: ET.Element) -> Item:
        item.properties.instrument = item.properties.constellation
        item.properties.sensor = item.properties.constellation

        if metadata.find("./IMD/IMAGE/SATAZ") is not None:
            item.properties.view__azimuth = float(metadata.find("./IMD/IMAGE/SATAZ").text)
        elif metadata.find("./IMD/IMAGE/MEANSATAZ") is not None:
            item.properties.view__azimuth = float(metadata.find("./IMD/IMAGE/MEANSATAZ").text)

        if metadata.find("./IMD/IMAGE/SUNAZ") is not None:
            item.properties.view__sun_azimuth = float(metadata.find("./IMD/IMAGE/SUNAZ").text)
        elif metadata.find("./IMD/IMAGE/SUNAZ") is not None:
            item.properties.view__sun_azimuth = float(metadata.find("./IMD/IMAGE/MEANSUNAZ").text)

        if metadata.find("./IMD/IMAGE/SUNEL") is not None:
            item.properties.view__sun_elevation = float(metadata.find("./IMD/IMAGE/SUNEL").text)
        elif metadata.find("./IMD/IMAGE/MEANSUNEL") is not None:
            item.properties.view__sun_elevation = float(metadata.find("./IMD/IMAGE/MEANSUNEL").text)

        eo__cloud_cover = find_or_none(metadata, "./IMD/IMAGE/CLOUDCOVER", lambda x: float(x) * 1000)
        if eo__cloud_cover != -999000.0:
            item.properties.eo__cloud_cover = eo__cloud_cover

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if not file.is_dir:
                    if file.name.endswith('-BROWSE.JPG'):
                        self.quicklook_path = file.path
                    if file.name.endswith('.TIF'):
                        self.tif_path = file.path
                    if file.name.endswith('.XML'):
                        self.xml_path = file.path
                    if file.name.endswith('.TIL'):
                        self.til_path = file.path
                    if file.name.endswith('.IMD'):
                        self.imd_path = file.path
            if self.tif_path:
                tfw_path = os.path.splitext(self.tif_path)[0] + ".TFW"
                if AccessManager.exists(tfw_path):
                    self.tfw_path = tfw_path
            return self.tif_path is not None and self.xml_path is not None and self.til_path is not None and self.imd_path is not None
        return False
