from aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from aproc.core.settings import Configuration
from airs.core.models.model import Asset, Item, Role, Properties
from datetime import datetime
import os

from extensions.aproc.proc.ingest.drivers.impl.utils import setup_gdal

# TODO this driver must be tested with real data
class Driver(ProcDriver):
    root_directory = None
    tif_file_path = None
    image_shp_file_path = None
    component_shp_file_path = None
    preview_file_path = None
    tif_file = None

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
            Asset(href=self.preview_file_path,
                  roles=[Role.thumbnail.value], name=Role.thumbnail.value, type="image/jpg",
                  description=Role.thumbnail.value),
            Asset(href=self.preview_file_path,
                  roles=[Role.overview.value], name=Role.overview.value, type="image/jpg",
                  description=Role.overview.value),
            Asset(href=self.tif_file_path, relative_href=self.relative_dim_path,
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
        #Retrieve resolution from tiff file
        src_ds = gdal.Open(self.tif_file_path)
        _, xres, _, _, _, yres  = src_ds.GetGeoTransform()
        resolution = xres
        #Open component shape file to retrieve feature corresponding to tiff fle name
        driver = ogr.GetDriverByName("ESRI Shapefile")
        component_source = driver.Open(self.component_shp_file_path, 0) # read-only
        layer = component_source.GetLayer()
        layer.SetAttributeFilter("Filename_1 = " + self.tif_file)
        component_feature = layer.GetNextFeature()

        #Retrieve geometry and centroid
        component_geometry = component_feature.geometry()
        geometry = component_feature.ExportToJson(as_object=True)["geometry"]
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(component_geometry)
        centroid = str(component_geometry.Centroid())

        #Retrieve image ID corresponding to the component with a geographical query
        image_source = driver.Open(self.image_shp_file_path, 0)
        image_layer = image_source.GetLayer()
        image_layer.SetSpatialFilter(ogr.CreateGeometryFromWkt(str(component_geometry)))
        image_feature = image_layer.GetNextFeature()
        metadata = image_feature.items()
        azimuth_angle = float(metadata["Collect_Az"])
        sun_azimuth = float(metadata["Sun_Az"])
        sun_elevation = float(metadata["Sun_El"])
        cloud_cover = float(metadata["CloudCover"])
        date = metadata["Acq_Date"].split(" ")[0]
        time = metadata["Acq_Date"].split(" ")[1] + ":00"
        date_time = int(datetime.datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S").timestamp())
        image_feature.Destroy()
        component_feature.Destroy()

        item = Item(
            # TODO valid this formula for id
            id=str(url.replace("/", "-")),
            gsd=resolution,
            geometry=geometry,
            bbox=[min(map(lambda xy: xy[0], geometry["coordinates"][0])),
                  min(map(lambda xy: xy[1], geometry["coordinates"][0])),
                  max(map(lambda xy: xy[0], geometry["coordinates"][0])),
                  max(map(lambda xy: xy[1], geometry["coordinates"][0]))],
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                eo__cloud_cover=cloud_cover,
                view__azimuth=azimuth_angle,
                view__sun_azimuth=sun_azimuth,
                view__sun_elevation=sun_elevation
                # TODO check all the metadata available

            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(relative_folder_path: str):
        # relative_folder_path variable must be a folder path beginning and finishing with a /
        all_path = Driver.root_directory + relative_folder_path
        valid_and_exist = os.path.isdir(all_path) and os.path.exists(all_path)
        if valid_and_exist is True:
            for root, dirs, files in os.walk(all_path):
                for file in files:
                    if file.endswith('.tif'):
                        Driver.tif_file = file
                        Driver.tif_file_path = all_path + file
                    if file.endswith('_image.shp'):
                        Driver.image_shp_file_path = all_path + file
                    if file.endswith('_component.shp'):
                        Driver.component_shp_file_path = all_path + file
                    if file.endswith('.jpg'):
                        Driver.preview_file_path = all_path + file
            return Driver.tif_file_path is not None and Driver.image_shp_file_path is not None \
                   and Driver.component_shp_file_path is not None and Driver.preview_file_path is not None
        else:
            Driver.LOGGER.error("The folder {} does not exist.".format(all_path))
            return False
