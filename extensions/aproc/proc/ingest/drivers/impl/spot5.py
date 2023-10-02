import os
import xml.etree.ElementTree as ET
from airs.core.models.model import Asset, Item, Properties, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import setup_gdal, get_geom_bbox_centroid
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
        assets = []
        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                                description=Role.thumbnail.value))
        if self.quicklook_path is not None:
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                                description=Role.overview.value))
        assets.append(Asset(href=self.tif_path,
                            roles=[Role.data.value], name=Role.data.value, type="image/tif",
                            description=Role.data.value, airs__managed=False))

        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        from osgeo import gdal
        setup_gdal()
        tree = ET.parse(self.dim_path)
        root = tree.getroot()
        coords = []
        # Get geometry, bbox, centroid
        for vertex in root.iter('Vertex'):
            coord = [float(vertex.find('FRAME_LON').text), float(vertex.find('FRAME_LAT').text)]
            coords.append(coord)
        geometry, bbox, centroid = get_geom_bbox_centroid(coords[0][0], coords[0][1], coords[1][0], coords[1][1],
                                                          coords[2][0], coords[2][1], coords[3][0], coords[3][1])
        gsd = (float(root.find('./Geoposition/Geoposition_Insert/XDIM').text) + float(root.find('./Geoposition/Geoposition_Insert/YDIM').text))/2
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

            return Driver.tif_path is not None and \
                   Driver.dim_path is not None

        else:
            #TODO try to hide this log for file exploration service
            Driver.LOGGER.error("The folder {} does not exist.".format(path))
            return False
