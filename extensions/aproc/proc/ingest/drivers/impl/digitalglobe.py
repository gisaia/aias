import os
import xml.etree.ElementTree as ET
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_epsg, get_geom_bbox_centroid, get_hash_url, setup_gdal)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.quicklook_path = None
        self.thumbnail_path = None
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
    def supports(self, url: str) -> bool:
        try:
            result = self.__check_path__(url)
            return result
        except Exception as e:
            self.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
        if self.quicklook_path is not None:
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type=MimeType.JPG.value,
                                description=Role.overview.value, size=AccessManager.get_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))
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
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import ogr
        with AccessManager.make_local(self.xml_path) as local_xml_path:
            tree = ET.parse(local_xml_path)
            root = tree.getroot()

        # Calculate bbox
        ul_lat = float(root.find("./TIL/TILE/ULLAT").text)
        ul_lon = float(root.find("./TIL/TILE/ULLON").text)
        ur_lat = float(root.find("./TIL/TILE/URLAT").text)
        ur_lon = float(root.find("./TIL/TILE/URLON").text)
        lr_lat = float(root.find("./TIL/TILE/LRLAT").text)
        lr_lon = float(root.find("./TIL/TILE/LRLON").text)
        ll_lat = float(root.find("./TIL/TILE/LLLAT").text)
        ll_lon = float(root.find("./TIL/TILE/LLLON").text)
        geometry, bbox, centroid = get_geom_bbox_centroid(ul_lon, ul_lat, ur_lon, ur_lat, lr_lon, lr_lat, ll_lon, ll_lat)

        # Overwrite geometry and centroid if GIS_FILE is present with order shape file
        d = AccessManager.dirname(url)
        if AccessManager.is_dir(os.path.join(d, "GIS_FILE")):
            for file in AccessManager.listdir(os.path.join(d, "GIS_FILES")):
                if file.endswith("_ORDER_SHAPE.shp"):
                    setup_gdal()

                    with AccessManager.make_local(os.path.join(d, "GIS_FILES", file)) as order_shape_file:
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

        date_time_str = root.find("./IMD/MAP_PROJECTED_PRODUCT/EARLIESTACQTIME").text
        date_time = int(datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        gsd = float(root.find("./IMD/IMAGE/MEANCOLLECTEDGSD").text)
        processing__level = root.find("./IMD/PRODUCTLEVEL").text
        eo__cloud_cover = float(root.find("./IMD/IMAGE/CLOUDCOVER").text) * 1000
        constellation = root.find("./IMD/IMAGE/SATID").text
        if root.find("./IMD/IMAGE/SATAZ") is not None:
            view__azimuth = float(root.find("./IMD/IMAGE/SATAZ").text)
        else:
            view__azimuth = float(root.find("./IMD/IMAGE/MEANSATAZ").text)
        if root.find("./IMD/IMAGE/SUNAZ") is not None:
            view__sun_azimuth = float(root.find("./IMD/IMAGE/SUNAZ").text)
        else:
            view__sun_azimuth = float(root.find("./IMD/IMAGE/MEANSUNAZ").text)
        if root.find("./IMD/IMAGE/SUNEL") is not None:
            view__sun_elevation = float(root.find("./IMD/IMAGE/SUNEL").text)
        else:
            view__sun_elevation = float(root.find("./IMD/IMAGE/MEANSUNEL").text)

        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly

        with AccessManager.make_local(self.tif_path) as local_tif_path:
            src_ds = gdal.Open(local_tif_path, GA_ReadOnly)
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
                    instrument=constellation,
                    constellation=constellation,
                    sensor=constellation,
                    view__azimuth=view__azimuth,
                    view__sun_azimuth=view__sun_azimuth,
                    view__sun_elevation=view__sun_elevation,
                    item_type=ResourceType.gridded.value,
                    item_format=ItemFormat.digitalglobe.value,
                    main_asset_format=AssetFormat.geotiff.value,
                    main_asset_name=Role.data.value,
                    observation_type=ObservationType.image.value
                ),
                assets=dict(map(lambda asset: (asset.name, asset), assets))
            )
        if eo__cloud_cover != -999000.0:
            item.properties.eo__cloud_cover = eo__cloud_cover

        return item

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if AccessManager.is_file(os.path.join(path, file)):
                    if file.endswith('-BROWSE.JPG'):
                        self.thumbnail_path = os.path.join(path, file)
                        self.quicklook_path = os.path.join(path, file)
                    if file.endswith('.TIF'):
                        self.tif_path = os.path.join(path, file)
                    if file.endswith('.XML'):
                        self.xml_path = os.path.join(path, file)
                    if file.endswith('.TIL'):
                        self.til_path = os.path.join(path, file)
                    if file.endswith('.IMD'):
                        self.imd_path = os.path.join(path, file)
            if self.tif_path:
                tfw_path = os.path.splitext(self.tif_path)[0] + ".TFW"
                if AccessManager.exists(tfw_path):
                    self.tfw_path = tfw_path
            return self.tif_path is not None and self.xml_path is not None and self.til_path is not None and self.imd_path is not None
        return False
