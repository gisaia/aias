import os
from datetime import datetime

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ObservationType, Properties,
                                    ResourceType, Role, SensorType)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (
    downsample_image, raster_to_jpg, get_epsg,
    get_geom_bbox_centroid_from_coordinates)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()
        self.quicklook_path = None
        self.tif_path = None
        self.tfw_path = None
        self.file_name = None
        self.met_path = None
        self.component_id = None

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = []
        ImageDriverHelper.add_archive(assets, url)

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
        if self.quicklook_path:
            quicklook = ImageDriverHelper.make_local_preview_asset(self, url, self.quicklook_path, MimeType.PNG, AssetFormat.png)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if self.quicklook_path is None and IngestDriver.must_build_preview(Driver.configuration, self.tif_path, local_remote_both="both"):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            raster_to_jpg(self.tif_path, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href, stretch=Driver.configuration.get('overview_stretch', False))
            quicklook.size = AccessManager.get_size(quicklook.href)
            self.quicklook_path = quicklook.href
            assets.append(quicklook)

        if self.quicklook_path is not None:
            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(self.quicklook_path, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> dict:
        # The metadata file is a txt, so we build a dictionary that will be easy to read
        metadata = {}

        # One metadata file can refer to multiple geoeye products
        # We need to check that the correct metadata are taken for the item
        inside_component_section = False
        inside_product_image_section = False

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
                    if inside_component_section:
                        self.__get_field__(metadata, line, 'Product Image ID')
                        self.__get_field__(metadata, line, 'Pixel Size X')
                        self.__get_field__(metadata, line, 'Pixel Size Y')
                        self.__get_field__(metadata, line, 'Percent Component Cloud Cover', True)

                        if line.find('degrees') >= 0 and len(coordinates) < coords_length:
                            if line.find('Latitude') >= 0:
                                lat = float((line.split(':')[1].strip()).split(' ')[0])
                            if line.find('Longitude') >= 0:
                                lon = float((line.split(':')[1].strip()).split(' ')[0])
                            if lat is not None and lon is not None:
                                coordinates.append([lon, lat])
                                lon = None
                                lat = None
                        # Stop reading the file if the last line of the product description is reached
                        if line.find('Percent Component Cloud Cover:') >= 0:
                            break
                    if line.find('Component ID: ' + self.component_id) >= 0:
                        inside_component_section = True

            # Loop on the metadata file to ensure taht we got the Product Image ID
            with open(local_met_path) as f:
                for line in f:
                    self.__get_field__(metadata, line, 'Sensor Type')
                    self.__get_field__(metadata, line, 'Processing Level')
                    if inside_product_image_section:
                        self.__get_field__(metadata, line, 'Sensor')
                        self.__get_field__(metadata, line, 'Scan Azimuth')
                        self.__get_field__(metadata, line, 'Sun Angle Azimuth')
                        self.__get_field__(metadata, line, 'Sun Angle Elevation')
                        self.__get_date_field__(metadata, line)

                        if line.find('Percent Cloud Cover:') >= 0:
                            break
                    if line.find('Product Image ID: ' + metadata['Product Image ID']) >= 0:
                        inside_product_image_section = True

        if len(coordinates) < 4:
            raise DriverException("Couldn't find enough coordinates for a polygon")
        coordinates.append(coordinates[0])

        metadata['coordinates'] = coordinates

        return metadata

    def build_core_item(self, url: str, assets: list[Asset], metadata: dict) -> Item:
        geometry, bbox, centroid = get_geom_bbox_centroid_from_coordinates(metadata['coordinates'])
        date_time = int(datetime.strptime(metadata['Acquisition Date/Time'], "%Y-%m-%d %H:%M %Z").timestamp())
        constellation = metadata['Sensor']

        item = Item(
            geometry=geometry,
            bbox=bbox,
            centroid=centroid,
            properties=Properties(
                datetime=date_time,
                constellation=constellation,
                satellite=constellation,
                item_type=ResourceType.gridded.value,
                item_format=ItemFormat.geoeye.value,
                sensor_type=SensorType.OPTIC.value,
                main_asset_format=AssetFormat.geotiff.value,
                main_asset_name=Role.data.value,
                observation_type=ObservationType.optic.value
            ),
            assets={asset.name: asset for asset in assets}
        )

        return item

    def add_major_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        if 'Pixel Size X' in metadata and 'Pixel Size Y' in metadata:
            x_pixel_size = float(metadata['Pixel Size X'].split(' ')[0])
            y_pixel_size = float(metadata['Pixel Size Y'].split(' ')[0])
            item.properties.gsd = (x_pixel_size + y_pixel_size) / 2

        item.properties.secondary_id = self.tif_path.removesuffix(".tif")   # If merging files in one product: metadata.get("Product Order Number", None)
        item.properties.processing__level = metadata.get("Processing Level", None)
        item.properties.proj__epsg = get_epsg(AccessManager.get_gdal_proj(self.tif_path))

        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: dict) -> Item:
        item.properties.eo__cloud_cover = metadata.get("Percent Component Cloud Cover", None)

        item.properties.instrument = item.properties.constellation
        item.properties.sensor = item.properties.constellation

        if 'Scan Azimuth' in metadata:
            item.properties.view__azimuth = float(metadata['Scan Azimuth'].split(' ')[0])
        if 'Sun Angle Azimuth' in metadata:
            item.properties.view__sun_azimuth = float(metadata['Sun Angle Azimuth'].split(' ')[0])
        if 'Sun Angle Elevation' in metadata:
            item.properties.view__sun_elevation = float(metadata['Sun Angle Elevation'].split(' ')[0])

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
                                self.quicklook_path = file.path
                        if file.name.endswith('_metadata.txt'):
                            self.met_path = file.path
                return self.met_path is not None and self.tif_path is not None
        return False

    def __get_date_field__(self, data: dict, line: str):
        field = 'Acquisition Date/Time'
        if line.find(field) >= 0:
            data[field] = line.split(':')[1].strip() + ':' + line.split(':')[2].strip()

    def __get_field__(self, data: dict, line: str, field: str, is_float=False):
        if line.find(field) >= 0:
            if is_float:
                data[field] = float(line.split(':')[1].strip())
            else:
                data[field] = line.split(':')[1].strip()
