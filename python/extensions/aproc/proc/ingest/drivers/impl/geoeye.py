import os
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_epsg, get_geom_bbox_centroid_from_coordinates)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()
        self.quicklook_path = None
        self.thumbnail_path = None
        self.tif_path = None
        self.tfw_path = None
        self.file_name = None
        self.met_path = None
        self.component_id = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

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
        assets.append(Asset(href=self.met_path, size=AccessManager.get_size(self.met_path),
                            roles=[Role.metadata.value], name=Role.metadata.value, type=MimeType.TEXT.value,
                            description=Role.metadata.value, airs__managed=False, asset_format=AssetFormat.txt.value, asset_type=ResourceType.other.value))
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
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        d = {}

        coordinates = []
        coords_length = 0
        lat = None
        lon = None

        with AccessManager.make_local(self.met_path) as local_met_path:
            with open(local_met_path) as f:
                for line in f:
                    # Get number of coordinates to avoid adding bbox to polygon
                    if line.find("Number of Coordinates") >= 0:
                        coords_length = int(line.split(':')[1].strip())
                    # Get all the degrees coordinates
                    if line.find('degrees') >= 0 and len(coordinates) < coords_length:
                        if line.find('Latitude') >= 0:
                            lat = float((line.split(':')[1].strip()).split(' ')[0])
                        if line.find('Longitude') >= 0:
                            lon = float((line.split(':')[1].strip()).split(' ')[0])
                            if lon is not None and lat is not None:
                                coordinates.append([lon, lat])
                                lon = None
                                lat = None

                    self.__get_field__(d, line, 'Product Image ID')
                    self.__get_field__(d, line, 'Pixel Size X')
                    self.__get_field__(d, line, 'Pixel Size Y')
                    self.__get_field__(d, line, 'Percent Component Cloud Cover', True)
                    self.__get_field__(d, line, 'Sensor Type')
                    self.__get_field__(d, line, 'Processing Level')
                    self.__get_field__(d, line, 'Sensor')
                    self.__get_field__(d, line, 'Scan Azimuth')
                    self.__get_field__(d, line, 'Sun Angle Azimuth')
                    self.__get_field__(d, line, 'Sun Angle Elevation')
                    self.__get_date_field__(d, line)

        if len(coordinates) < 4:
            raise Exception("Couldn't find enough coordinates for a polygon")
        coordinates.append(coordinates[0])

        geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(coordinates)
        x_pixel_size = float(d['Pixel Size X'].split(' ')[0])
        y_pixel_size = float(d['Pixel Size Y'].split(' ')[0])
        gsd = (x_pixel_size + y_pixel_size) / 2
        eo__cloud_cover = d['Percent Component Cloud Cover']
        processing__level = d['Processing Level']
        constellation = d['Sensor']
        instrument = d['Sensor']
        sensor = d['Sensor']
        sensor_type = d['Sensor Type']
        date_time = int(datetime.strptime(d['Acquisition Date/Time'], "%Y-%m-%d %H:%M %Z").timestamp())
        view__azimuth = float(d['Scan Azimuth'].split(' ')[0])
        view__sun_azimuth = float(d['Sun Angle Azimuth'].split(' ')[0])
        view__sun_elevation = float(d['Sun Angle Elevation'].split(' ')[0])

        item = Item(
            id=self.get_item_id(url),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                eo__cloud_cover=eo__cloud_cover,
                gsd=gsd,
                proj__epsg=get_epsg(AccessManager.get_gdal_proj(self.tif_path)),
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                sensor_type=sensor_type,
                view__azimuth=view__azimuth,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.geoeye.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets=dict([(asset.name, asset) for asset in assets])
        )

        return item

    def __check_path__(self, file_path: str):
        self.__init__()
        file_name = os.path.basename(file_path)
        path = AccessManager.dirname(file_path)
        if file_name.endswith(".tif") and AccessManager.is_file(file_path):
            self.tif_path = file_path
            tfw_path = os.path.splitext(self.tif_path)[0] + ".tfw"
            if AccessManager.exists(tfw_path):
                self.tfw_path = tfw_path
            self.file_name = file_name
            parts_of_file_name = file_name.replace('.tif', '').split("_")
            if len(parts_of_file_name) >= 4:
                self.component_id = parts_of_file_name[3]
                for file in AccessManager.listdir(path):
                    # check if current file is a file
                    if not file.is_dir:
                        if file.name.endswith('.jpg'):
                            if file.name == parts_of_file_name[0] + '_' + parts_of_file_name[1] + '_rgb_' + parts_of_file_name[3] + '_ovr.jpg':
                                self.thumbnail_path = file.path
                                self.quicklook_path = file.path
                        if file.name.endswith('_metadata.txt'):
                            self.met_path = file.path
                return self.met_path is not None and self.tif_path is not None
        return False

    def __get_date_field__(self, data, line):
        field = 'Acquisition Date/Time'
        if line.find(field) >= 0:
            data[field] = line.split(':')[1].strip() + ':' + line.split(':')[2].strip()

    def __get_field__(self, data, line, field, is_float=False):
        if line.find(field) >= 0:
            if is_float:
                data[field] = float(line.split(':')[1].strip())
            else:
                data[field] = line.split(':')[1].strip()
