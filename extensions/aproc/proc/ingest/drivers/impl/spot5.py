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
        self.dim_path = None
        self.tif_path = None
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
        assets.append(
            Asset(href=self.dim_path, size=AccessManager.get_size(self.dim_path),
                  roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.XML.value,
                  description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.xml.value, asset_type=ResourceType.other.value))
        if self.tfw_path:
            assets.append(Asset(href=self.tfw_path, size=AccessManager.get_size(self.tfw_path),
                                roles=[Role.metadata.value], name="tfw", type=MimeType.TEXT.value,
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

        with AccessManager.make_local(self.dim_path) as local_dim_path:
            tree = ET.parse(local_dim_path)
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
            src_ds = gdal.Open(local_dim_path, GA_ReadOnly)
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

    def __check_path__(self, path: str):
        self.__init__()
        if AccessManager.is_dir(path):
            for file in AccessManager.listdir(path):
                if not file.is_dir:
                    if file.name.lower() == "imagery.tif":
                        self.tif_path = file.path
                        tfw_path = os.path.splitext(self.tif_path)[0] + ".tfw"
                        if AccessManager.exists(tfw_path):
                            self.tfw_path = tfw_path
                    if file.name.lower() == "metadata.dim":
                        self.dim_path = file.path
                    if file.name.lower() == "preview.jpg":
                        self.quicklook_path = file.path
                    if file.name.lower() == "icon.jpg":
                        self.thumbnail_path = file.path

            return self.tif_path is not None and self.dim_path is not None
        return False
