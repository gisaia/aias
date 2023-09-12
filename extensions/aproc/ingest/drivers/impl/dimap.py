from aproc.ingest.drivers.driver import Driver as ProcDriver
from aproc.settings import Configuration
from airs.core.models.model import Asset, Item, Role, Properties
from datetime import datetime
import os
from osgeo import gdal
import xml.etree.ElementTree as ET

from extensions.aproc.ingest.drivers.impl.utils import setup_gdal


class Driver(ProcDriver):
    root_directory = None
    quicklook_path = None
    thumbnail_path = None
    dim_path = None
    relative_dim_path = None

    # Implements drivers method
    def init(configuration: Configuration):
        Driver.root_directory = configuration["root_directory"]

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
        return [
            Asset(href=self.thumbnail_path,
                  roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                  description=Role.thumbnail.value),
            Asset(href=self.quicklook_path,
                  roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                  description=Role.overview.value),
            Asset(href=self.dim_path, relative_href=self.relative_dim_path,
                  roles=[Role.metadata.value], name=Role.metadata.value, type="text/xml",
                  description=Role.metadata.value)
        ]

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        setup_gdal()
        tree = ET.parse(self.dim_path)
        root = tree.getroot()
        coordinates = []
        for vertex in root.iter('Vertex'):
            coord = [float(vertex.find('LON').text), float(vertex.find('LAT').text)]
            coordinates.append(coord)
        coordinates.append(coordinates[0])
        geometry = {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
        for cent in root.iter('Center'):
            centroid = [float(cent.find('LON').text), float(cent.find('LAT').text)]
        src_ds = gdal.Open(self.dim_path)
        metadata = src_ds.GetMetadata()
        date = metadata["IMAGING_DATE"]
        time = metadata["IMAGING_TIME"]
        if "Z" in time:
            date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S.%fZ").timestamp())
        else:
            date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S.%f").timestamp())
        if "CLOUDCOVER_CLOUD_NOTATION" in metadata:
            cloud_cover = float(metadata["CLOUDCOVER_CLOUD_NOTATION"])
        else:
            for cloud in root.iter('Dataset_Content'):
                if cloud.find("CLOUD_COVERAGE") is not None:
                    cloud_cover = float(cloud.find("CLOUD_COVERAGE").text)
        item = Item(
            # TODO valid this formula for id
            id=str(url.replace("/", "-")),
            geometry=geometry,
            bbox=[min(map(lambda xy: xy[0], geometry["coordinates"][0])),
                  min(map(lambda xy: xy[1], geometry["coordinates"][0])),
                  max(map(lambda xy: xy[0], geometry["coordinates"][0])),
                  max(map(lambda xy: xy[1], geometry["coordinates"][0]))],
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=metadata["PROCESSING_LEVEL"],
                instrument=metadata["INSTRUMENT"],
                eo__cloud_cover=cloud_cover,
                view__incidence_angle=metadata["INCIDENCE_ANGLE"],
                view__azimuth=metadata["AZIMUTH_ANGLE"],
                view__sun_azimuth=metadata["SUN_AZIMUTH"],
                view__sun_elevation=metadata["SUN_ELEVATION"]
                # TODO check all the metadata available

            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(relative_folder_path: str):
        # relative_folder_path variable must be a folder path beginning and finishing with a /
        all_path = Driver.root_directory + relative_folder_path
        valid_and_exist = os.path.isdir(all_path) and os.path.exists(all_path)
        cat_all_thumb_path = None
        cat_all_quick_path = None
        if valid_and_exist is True:
            for root, dirs, files in os.walk(all_path):
                for file in files:
                    if file.endswith('.XML') and file.startswith('DIM'):
                        Driver.dim_path = all_path + file
                        Driver.relative_dim_path = relative_folder_path + file
                    if file.endswith('.JPG') and file.startswith('PREVIEW'):
                        raw_all_quick_path = all_path + file
                    if file.endswith('.JPG') and file.startswith('ICON'):
                        raw_all_thumb_path = all_path + file
                    if file.endswith('.JPG') and file.startswith('CAT_QL'):
                        cat_all_quick_path = all_path + file
                    if file.endswith('.JPG') and file.startswith('CAT_TB'):
                        cat_all_thumb_path = all_path + file
            if cat_all_thumb_path is not None:
                Driver.thumbnail_path = cat_all_thumb_path
            else:
                Driver.thumbnail_path = raw_all_thumb_path
            if cat_all_quick_path is not None:
                Driver.quicklook_path = cat_all_quick_path
            else:
                Driver.quicklook_path = raw_all_quick_path
            return Driver.thumbnail_path is not None and Driver.quicklook_path is not None and Driver.dim_path is not None
        else:
            Driver.LOGGER.error("The folder {} does not exist.".format(all_path))
            return False
