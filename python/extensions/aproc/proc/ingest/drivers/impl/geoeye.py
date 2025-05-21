import os
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role)
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    get_epsg, get_geom_bbox_centroid, get_hash_url)
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
    def supports(self, url: str) -> bool:
        # url variable must be a folder path begining with a /
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
    def get_item_id(self, url: str) -> str:
        return get_hash_url(url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        d = {}
        inside_component_section = False
        inside_product_image_section = False
        inside_coord_1 = False
        inside_coord_2 = False
        inside_coord_3 = False
        inside_coord_4 = False

        with AccessManager.make_local(self.met_path) as local_met_path:
            with open(local_met_path) as f:
                for line_1 in f:
                    if inside_component_section:
                        self.__set_lat_lon(d, line_1, inside_coord_1, 1)
                        self.__set_lat_lon(d, line_1, inside_coord_2, 2)
                        self.__set_lat_lon(d, line_1, inside_coord_3, 3)
                        self.__set_lat_lon(d, line_1, inside_coord_4, 4)
                        self.__get_field__(d, line_1, 'Product Image ID')
                        self.__get_field__(d, line_1, 'Pixel Size X')
                        self.__get_field__(d, line_1, 'Pixel Size Y')
                        self.__get_field__(d, line_1, 'Percent Component Cloud Cover', True)
                        if line_1.find('Coordinate: 1') >= 0:
                            inside_coord_1 = True
                            inside_coord_4 = False
                        if line_1.find('Coordinate: 2') >= 0:
                            inside_coord_2 = True
                            inside_coord_1 = False
                        if line_1.find('Coordinate: 3') >= 0:
                            inside_coord_3 = True
                            inside_coord_2 = False
                        if line_1.find('Coordinate: 4') >= 0:
                            inside_coord_4 = True
                            inside_coord_3 = False
                        if line_1.find('Percent Component Cloud Cover') >= 0:
                            break
                    if line_1.find('Component ID: ' + self.component_id) >= 0:
                        inside_component_section = True

            with open(local_met_path) as f_2:
                for line_2 in f_2:
                    self.__get_field__(d, line_2, 'Sensor Type')
                    self.__get_field__(d, line_2, 'Processing Level')
                    if inside_product_image_section:
                        self.__get_field__(d, line_2, 'Sensor')
                        self.__get_field__(d, line_2, 'Scan Azimuth')
                        self.__get_field__(d, line_2, 'Sun Angle Azimuth')
                        self.__get_field__(d, line_2, 'Sun Angle Elevation')
                        self.__get_date_field__(d, line_2)
                    if line_2.find('Product Image ID: ' + d['Product Image ID']) >= 0:
                        inside_product_image_section = True

        geometry, bbox, centroid = get_geom_bbox_centroid(d['lon_1'], d['lat_1'], d['lon_2'], d['lat_2'], d['lon_3'], d['lat_3'], d['lon_4'], d['lat_4'])
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
                observation_type=ObservationType.image.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
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

    def __get_latitude__(self, data, line, coord_number):
        if line.find('Latitude') >= 0:
            data['lat_' + str(coord_number)] = float((line.split(':')[1].strip()).split(' ')[0])

    def __get_longitude__(self, data, line, coord_number):
        if line.find('Longitude') >= 0:
            data['lon_' + str(coord_number)] = float((line.split(':')[1].strip()).split(' ')[0])

    def __set_lat_lon(self, data, line, inside_coord, coord_number):
        if inside_coord:
            self.__get_latitude__(data, line, coord_number)
            self.__get_longitude__(data, line, coord_number)
