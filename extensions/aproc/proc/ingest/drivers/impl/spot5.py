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
    dim_path = None
    tif_path = None

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
        from osgeo import gdal, ogr
        setup_gdal()
        tree = ET.parse(self.dim_path)
        root = tree.getroot()
        coordinates = []
        #Calculate bbox
        for vertex in root.iter('Vertex'):
            coord = [float(vertex.find('FRAME_LON').text), float(vertex.find('FRAME_LAT').text)]
            coordinates.append(coord)
        bbox = [min(map(lambda xy: xy[0], coordinates)),
                min(map(lambda xy: xy[1], coordinates)),
                max(map(lambda xy: xy[0], coordinates)),
                max(map(lambda xy: xy[1], coordinates))]
        #Use bbox as geometry
        coordinates.append(coordinates[0])
        geometry = {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
        geom = ogr.CreateGeometryFromJson(json.dumps(geometry))
        centroid_geom = geom.Centroid()
        centroid_geom_list = str(centroid_geom).replace("(","").replace(")","").split(" ")
        centroid = [float(centroid_geom_list[2]),float(centroid_geom_list[1])]
        gsd = (float(root.find('./Geoposition/Geoposition_Insert/XDIM').text) +  float(root.find('./Geoposition/Geoposition_Insert/YDIM').text))/2
        src_ds = gdal.Open(self.dim_path)
        metadata = src_ds.GetMetadata()
        # We retrieve the time
        date = metadata["IMAGING_DATE"]
        time = metadata["IMAGING_TIME"]
        date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S").timestamp())
        print(date_time)
        item = Item(
            id=str(url.replace("/", "-")),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=metadata["PROCESSING_LEVEL"],
                gsd=gsd,
                instrument= metadata["INSTRUMENT"],
                constellation = metadata["MISSION"],
                sensor = metadata["MISSION"],
                sensor_type = metadata["MISSION_INDEX"],
                view__incidence_angle=metadata["INCIDENCE_ANGLE"],
                view__sun_azimuth= metadata["SUN_AZIMUTH"],
                view__sun_elevation= metadata["SUN_ELEVATION"]
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(path: str):
        Driver.thumbnail_path = None
        Driver.quicklook_path = None
        Driver.tif_path = None
        Driver.dim_path = None
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        if valid_and_exist is True:
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    if file == "imagery.tif":
                        Driver.tif_path = os.path.join(path, file)
                    if file == "metadata.dim":
                        Driver.dim_path = os.path.join(path, file)
                    if file == "preview.jpg":
                        Driver.quicklook_path = os.path.join(path, file)
                    if file == "icon.jpg":
                        Driver.thumbnail_path = os.path.join(path, file)

            return Driver.thumbnail_path is not None and \
                   Driver.quicklook_path is not None and \
                   Driver.tif_path is not None and \
                   Driver.dim_path is not None

        else:
            Driver.LOGGER.error("The folder {} does not exist.".format(path))
            return False
