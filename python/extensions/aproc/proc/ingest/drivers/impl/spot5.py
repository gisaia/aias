import os
import xml.etree.ElementTree as ET
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, geotiff_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_coordinates)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):
    ns = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}  # NOSONAR
    configuration: dict = {}

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
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

        if self.thumbnail_path is not None:
            assets.append(Asset(href=self.thumbnail_path,
                                roles=[Role.thumbnail.value], name=Role.thumbnail.value, type=MimeType.JPG.value,
                                description=Role.thumbnail.value, size=AccessManager.get_size(self.thumbnail_path), asset_format=AssetFormat.jpg.value))
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
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_preview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None and self.tif_path and ((AccessManager.is_local(self.tif_path) and Driver.configuration.get('build_overview_when_local', True)) or (not AccessManager.is_local(self.tif_path) and Driver.configuration.get('build_overview_when_remote', False))):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, output_path=quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
            quicklook.size = AccessManager.get_size(quicklook.href)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        if self.thumbnail_path is None and self.quicklook_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        with AccessManager.make_local(self.dim_path) as local_dim_path:
            tree = ET.parse(local_dim_path)
            root = tree.getroot()

        return root

    def build_core_item(self, url: str, assets: list[Asset], root: ET.Element) -> Item:
        coords = []
        # Get geometry, bbox, centroid
        for vertex in root.find('./Dataset_Frame', Driver.ns).iter('Vertex'):
            coord = [float(vertex.find('FRAME_LON').text), float(vertex.find('FRAME_LAT').text)]
            coords.append(coord)
        coords.append(coords[0])
        geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(coords)

        metadata = AccessManager.get_gdal_md(self.dim_path)
        # We retrieve the time
        date = metadata["IMAGING_DATE"]
        time = metadata["IMAGING_TIME"]
        date_time = int(datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S").timestamp())

        constellation = metadata["MISSION"]
        satellite = constellation
        if "MISSION_INDEX" in metadata:
            satellite = satellite + "-" + metadata["MISSION_INDEX"]

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                satellite=satellite,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.spot5.value,
                sensor_type=SensorType.OPTIC.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        metadata = AccessManager.get_gdal_md(self.dim_path)

        gsd_x = root.find('./Geoposition/Geoposition_Insert/XDIM', Driver.ns)
        gsd_y = root.find('./Geoposition/Geoposition_Insert/YDIM', Driver.ns)
        if gsd_x is not None and gsd_y is not None:
            item.properties.gsd = (float(gsd_x.text) + float(gsd_y.text))/2

        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.dim_path))
        item.properties.processing__level = metadata.get("PROCESSING_LEVEL", None)
        item.properties.secondary_id = root.find('./Dataset_Sources/Source_Information/SOURCE_ID', Driver.ns).text
        return item

    def add_minor_metadata(self, url: str, item: Item, root: ET.Element) -> Item:
        metadata = AccessManager.get_gdal_md(self.dim_path)

        item.properties.instrument = metadata.get("INSTRUMENT", None)
        item.properties.sensor = item.properties.constellation

        item.properties.view__incidence_angle = metadata.get("INCIDENCE_ANGLE", None)
        item.properties.view__sun_azimuth = metadata.get("SUN_AZIMUTH", None)
        item.properties.view__sun_elevation = metadata.get("SUN_ELEVATION", None)

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
