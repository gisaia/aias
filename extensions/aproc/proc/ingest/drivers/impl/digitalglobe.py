import os
import xml.etree.ElementTree as ET
import json
from airs.core.models.model import Asset, Item, Properties, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import setup_gdal
from datetime import datetime

class Driver(ProcDriver):
    quicklook_path = None
    thumbnail_path = None
    xml_path = None
    til_path = None
    tif_path = None
    imd_path = None

    # Implements drivers method

    def init(configuration: Configuration):
        return

    # Implements drivers method
    def supports(url: str) -> bool:
        try:
            result = Driver.__check_path__(url)
            return result
        except Exception as e:
            Driver.LOGGER.debug(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        return [
            Asset(href=self.thumbnail_path,
                  roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                  description=Role.thumbnail.value),
            Asset(href=self.quicklook_path,
                  roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                  description=Role.overview.value),
            Asset(href=self.tif_path,
                  roles=[Role.data.value], name=Role.data.value, type="image/tif",
                  description=Role.data.value)
        ]

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import ogr
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        #Calculate bbox
        coordinates = [[float(root.find("./TIL/TILE/ULLON").text), float(root.find("./TIL/TILE/ULLAT").text)],
                       [float(root.find("./TIL/TILE/URLON").text), float(root.find("./TIL/TILE/URLAT").text)],
                       [float(root.find("./TIL/TILE/LRLON").text), float(root.find("./TIL/TILE/LRLAT").text)],
                       [float(root.find("./TIL/TILE/LLLON").text), float(root.find("./TIL/TILE/LLLAT").text)]]
        bbox = [min(map(lambda xy: xy[0], coordinates)),
                min(map(lambda xy: xy[1], coordinates)),
                max(map(lambda xy: xy[0], coordinates)),
                max(map(lambda xy: xy[1], coordinates))]
        #Calculate geometry
        from os.path import dirname, abspath
        d = (dirname(abspath(url)))
        if os.path.isdir(os.path.join(d,"GIS_FILE")):
            for file in os.listdir(os.path.join(d,"GIS_FILES")):
                if file.endswith("_ORDER_SHAPE.shp"):
                    setup_gdal()
                    order_shape_file = os.path.join(d,"GIS_FILES",file)
                    driver = ogr.GetDriverByName("ESRI Shapefile")
                    component_source = driver.Open(order_shape_file, 0) # read-only
                    layer = component_source.GetLayer()
                    component_feature = layer.GetNextFeature()
                    component_geometry = component_feature.geometry()
                    geometry = component_feature.ExportToJson(as_object=True)["geometry"]
                    centroid_geom = component_geometry.Centroid()
                    centroid_geom_list = str(centroid_geom).replace("(","").replace(")","").split(" ")
                    centroid = [float(centroid_geom_list[2]),float(centroid_geom_list[1])]
                    break
        else:
            #Use bbox as geometry
            coordinates.append([float(root.find("./TIL/TILE/ULLON").text), float(root.find("./TIL/TILE/ULLAT").text)])
            geometry = {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
            geom = ogr.CreateGeometryFromJson(json.dumps(geometry))
            centroid_geom = geom.Centroid()
            centroid_geom_list = str(centroid_geom).replace("(","").replace(")","").split(" ")
            centroid = [float(centroid_geom_list[1]),float(centroid_geom_list[2])]

        date_time_str = root.find("./IMD/MAP_PROJECTED_PRODUCT/EARLIESTACQTIME").text
        date_time = int(datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        gsd = float(root.find("./IMD/IMAGE/MEANCOLLECTEDGSD").text)
        processing__level=root.find("./IMD/PRODUCTLEVEL").text
        eo__cloud_cover=float(root.find("./IMD/IMAGE/CLOUDCOVER").text) * 1000
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
        item = Item(
            id=str(url.replace("/", "-")),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                gsd=gsd,
                instrument=constellation,
                constellation = constellation,
                sensor = constellation,
                view__azimuth=view__azimuth,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        if eo__cloud_cover != -999000.0:
            item.properties.eo__cloud_cover = eo__cloud_cover
        return item

    def __check_path__(path: str):
        Driver.thumbnail_path = None
        Driver.quicklook_path = None
        Driver.tif_path = None
        Driver.xml_path = None
        Driver.til_path = None
        Driver.imd_path = None
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        if valid_and_exist is True:
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    if file.endswith('-BROWSE.JPG'):
                        Driver.thumbnail_path = os.path.join(path, file)
                        Driver.quicklook_path = os.path.join(path, file)
                    if file.endswith('.TIF'):
                        Driver.tif_path = os.path.join(path, file)
                    if file.endswith('.XML'):
                        Driver.xml_path = os.path.join(path, file)
                    if file.endswith('.TIL'):
                        Driver.til_path = os.path.join(path, file)
                    if file.endswith('.IMD'):
                        Driver.imd_path = os.path.join(path, file)
            return Driver.thumbnail_path is not None and \
                   Driver.quicklook_path is not None and \
                   Driver.tif_path is not None and \
                   Driver.xml_path is not None and \
                   Driver.til_path is not None and \
                   Driver.imd_path is not None
        else:
            Driver.LOGGER.error("The folder {} does not exist.".format(path))
            return False