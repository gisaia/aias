import os
from datetime import datetime

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    ObservationType, Properties, ResourceType,
                                    Role)
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import Driver as ProcDriver
from extensions.aproc.proc.ingest.drivers.impl.utils import \
    get_geom_bbox_centroid


class Driver(ProcDriver):
    quicklook_path = None
    thumbnail_path = None
    tif_path = None
    file_name = None
    met_path = None
    component_id = None

    # Implements drivers method
    def init(configuration: Configuration):
        return

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
                            description=Role.data.value, airs__managed=False, asset_format=AssetFormat.geotiff.value, asset_type=ResourceType.gridded.value))

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
        inside_component_section = False
        inside_product_image_section = False
        inside_coord_1 = False
        inside_coord_2 = False
        inside_coord_3 = False
        inside_coord_4 = False
        with open(self.met_path) as f:
            for line_1 in f:
                if inside_component_section:
                    self.__set_lat_lon(d,line_1,inside_coord_1,1)
                    self.__set_lat_lon(d,line_1,inside_coord_2,2)
                    self.__set_lat_lon(d,line_1,inside_coord_3,3)
                    self.__set_lat_lon(d,line_1,inside_coord_4,4)
                    self.__get_field__(d,line_1,'Product Image ID')
                    self.__get_field__(d,line_1,'Pixel Size X')
                    self.__get_field__(d,line_1,'Pixel Size Y')
                    self.__get_field__(d,line_1,'Percent Component Cloud Cover',True)
                    if line_1.find('Coordinate: 1') >=0:
                        inside_coord_1 = True
                        inside_coord_4 = False
                    if line_1.find('Coordinate: 2') >=0:
                        inside_coord_2 = True
                        inside_coord_1 = False
                    if line_1.find('Coordinate: 3') >=0:
                        inside_coord_3 = True
                        inside_coord_2 = False
                    if line_1.find('Coordinate: 4') >=0:
                        inside_coord_4 = True
                        inside_coord_3 = False
                    if line_1.find('Percent Component Cloud Cover') >=0:
                        break
                if line_1.find('Component ID: '+ self.component_id) >=0:
                    inside_component_section = True


        with open(self.met_path) as f_2:
            for line_2 in f_2:
                self.__get_field__(d,line_2,'Sensor Type')
                self.__get_field__(d,line_2,'Processing Level')
                if inside_product_image_section:
                        self.__get_field__(d,line_2,'Sensor')
                        self.__get_field__(d,line_2,'Scan Azimuth')
                        self.__get_field__(d,line_2,'Sun Angle Azimuth')
                        self.__get_field__(d,line_2,'Sun Angle Elevation')
                        self.__get_date_field__(d,line_2)
                if line_2.find('Product Image ID: '+ d['Product Image ID']) >=0:
                     inside_product_image_section =True
        geometry, bbox, centroid = get_geom_bbox_centroid(d['lon_1'],d['lat_1'],d['lon_2'],d['lat_2'],d['lon_3'], d['lat_3'],d['lon_4'], d['lat_4'])
        x_pixel_size = float(d['Pixel Size X'].split(' ')[0])
        y_pixel_size = float(d['Pixel Size Y'].split(' ')[0])
        gsd = (x_pixel_size+y_pixel_size)/2
        eo__cloud_cover = d['Percent Component Cloud Cover']
        processing__level = d['Processing Level']
        constellation = d['Sensor']
        instrument = d['Sensor']
        sensor = d['Sensor']
        sensor_type = d['Sensor Type']
        date_time =  int(datetime.strptime(d['Acquisition Date/Time'], "%Y-%m-%d %H:%M %Z").timestamp())
        view__azimuth=float(d['Scan Azimuth'].split(' ')[0])
        view__sun_azimuth=float(d['Sun Angle Azimuth'].split(' ')[0])
        view__sun_elevation=float(d['Sun Angle Elevation'].split(' ')[0])

        item = Item(
            id=str(url.replace("/", "-")),
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                processing__level=processing__level,
                eo__cloud_cover=eo__cloud_cover,
                gsd=gsd,
                instrument=instrument,
                constellation=constellation,
                sensor=sensor,
                sensor_type=sensor_type,
                view__azimuth=view__azimuth,
                view__sun_azimuth=view__sun_azimuth,
                view__sun_elevation=view__sun_elevation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.geoeye.value,
                main_asset_format=AssetFormat.jpg2000.value,  # TODO MATTHIEU: voir si c'est du geotiff ou du jpeg ou jpg2000
                observation_type=ObservationType.image.value
            ),
            assets=dict(map(lambda asset: (asset.name, asset), assets))
        )
        return item

    def __check_path__(file_path: str):
        Driver.tif_path = None
        Driver.met_path = None
        Driver.quicklook_path = None
        Driver.thumbnail_path = None
        Driver.component_id = None
        valid_and_exist = os.path.isfile(file_path) and os.path.exists(file_path)
        file_name = os.path.basename(file_path)
        path = os.path.dirname(file_path)
        if valid_and_exist is True and file_name.endswith(".tif"):
            Driver.tif_path = file_path
            Driver.file_name = file_name
            parts_of_file_name = file_name.replace('.tif','').split("_")
            Driver.component_id = parts_of_file_name[3]
            for file in os.listdir(path):
                # check if current file is a file
                if os.path.isfile(os.path.join(path, file)):
                    if file.endswith('.jpg'):
                        if file == parts_of_file_name[0] + '_' + parts_of_file_name[1] + '_rgb_' + parts_of_file_name[3] + '_ovr.jpg':
                            Driver.thumbnail_path = os.path.join(path, file)
                            Driver.quicklook_path = os.path.join(path, file)
                    if file.endswith('_metadata.txt'):
                        Driver.met_path = os.path.join(path, file)
            return Driver.met_path is not None and \
                   Driver.tif_path is not None
        else:
            #TODO try to hide this log for file exploration service
            Driver.LOGGER.error("The folder {} does not exist.".format(file_path))
            return False

    @staticmethod
    def __get_date_field__(data,line):
        field ='Acquisition Date/Time'
        if line.find(field) >=0:
            data[field]=line.split(':')[1].strip() + ':'+line.split(':')[2].strip()

    @staticmethod
    def __get_field__(data,line,field,isFloat=False):
        if line.find(field) >=0:
            if isFloat:
                data[field]=float(line.split(':')[1].strip())
            else:
                data[field]=line.split(':')[1].strip()

    @staticmethod
    def __get_latitude__(data,line, coord_number):
        if line.find('Latitude') >=0:
            data['lat_' + str(coord_number)]= float((line.split(':')[1].strip()).split(' ')[0])

    @staticmethod
    def __get_longitude__(data,line, coord_number):
        if line.find('Longitude') >=0:
            data['lon_' + str(coord_number)]= float((line.split(':')[1].strip()).split(' ')[0])

    @staticmethod
    def __set_lat_lon(data,line,inside_coord,coord_number):
        if inside_coord:
            Driver.__get_latitude__(data,line,coord_number)
            Driver.__get_longitude__(data,line,coord_number)

