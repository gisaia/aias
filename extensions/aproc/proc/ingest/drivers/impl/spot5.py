import os
from pathlib import Path
import xml.etree.ElementTree as ET
from airs.core.models.model import Asset, AssetFormat, Item, ItemFormat, MimeType, ObservationType, Properties, ResourceType, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import get_file_size, setup_gdal, get_geom_bbox_centroid, \
    get_hash_url, get_epsg
from datetime import datetime


class Driver(ProcDriver):
    quicklook_path = None
    thumbnail_path = None
    dim_path = None
    tif_path = None
    tfw_path = None

    # Implements drivers method
    @staticmethod
    def init(configuration: Configuration):
        return

    # Implements drivers method
    @staticmethod
    def supports(url: str) -> bool:
        try:
            result = Driver.__check_path__(url)
            return result
        except Exception as e:
            Driver.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG,
                                description=Role.thumbnail.value, size=get_file_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
        if self.quicklook_path is not None:
            assets.append(Asset(href=self.quicklook_path,
                                roles=[Role.overview.value], name=Role.overview.value, type=MimeType.JPG,
                                description=Role.overview.value, size=get_file_size(self.quicklook_path), asset_format=AssetFormat.jpg.value))
        assets.append(Asset(href=self.tif_path, size=get_file_size(self.tif_path),
                            roles=[Role.data.value], name=Role.data.value, type=MimeType.TIFF,
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))
        assets.append(
            Asset(href=self.dim_path, size=get_file_size(self.dim_path),
                  roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML,
                  description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        if Driver.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=get_file_size(self.tfw_path),
                                roles=[Role.metadata.value], name="tfw", type=MimeType.TEXT,
                                description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
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
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly
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
        if root.find('./Geoposition/Geoposition_Insert/XDIM') and root.find('./Geoposition/Geoposition_Insert/YDIM'):
            gsd = (float(root.find('./Geoposition/Geoposition_Insert/XDIM').text) + float(root.find('./Geoposition/Geoposition_Insert/YDIM').text))/2
        else:
            gsd = None
        src_ds = gdal.Open(self.dim_path, GA_ReadOnly)
        metadata = src_ds.GetMetadata()
        # We retrieve the time
        date = metadata["IMAGING_DATE"]
        time = metadata["IMAGING_TIME"]
        date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S").timestamp())
        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=metadata.get("PROCESSING_LEVEL"),
                gsd=gsd,
                proj__epsg=get_epsg(src_ds),
                instrument=metadata.get("INSTRUMENT"),
                constellation=metadata.get("MISSION"),
                sensor=metadata.get("MISSION"),
                sensor_type=metadata.get("MISSION_INDEX"),
                view__incidence_angle=metadata.get("INCIDENCE_ANGLE"),
                view__sun_azimuth=metadata.get("SUN_AZIMUTH"),
                view__sun_elevation=metadata.get("SUN_ELEVATION"),
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.spot5.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.image.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    @staticmethod
    def __check_path__(path: str):
        Driver.thumbnail_path = None
        Driver.quicklook_path = None
        Driver.tif_path = None
        Driver.dim_path = None
        valid_and_exist = os.path.isdir(path) and os.path.exists(path)
        if valid_and_exist is True:
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    if file.lower() == "imagery.tif":
                        Driver.tif_path = os.path.join(path, file)
                        tfw_path = Path(Driver.tif_path).with_suffix(".tfw")
                        if tfw_path.exists():
                            Driver.tfw_path = str(tfw_path)
                    if file.lower() == "metadata.dim":
                        Driver.dim_path = os.path.join(path, file)
                    if file.lower() == "preview.jpg":
                        Driver.quicklook_path = os.path.join(path, file)
                    if file.lower() == "icon.jpg":
                        Driver.thumbnail_path = os.path.join(path, file)

            return Driver.tif_path is not None and \
                   Driver.dim_path is not None
        return False
