import os
import xml.etree.ElementTree as ET

from airs.core.models.model import AssetFormat, Item, ItemFormat
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.download.drivers.download_driver import \
    DownloadDriver


class Driver(DownloadDriver):

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        DownloadDriver.init(configuration)

    # Implements drivers method
    def supports(self, item: Item) -> bool:
        item_format = item.properties.item_format
        href = self.get_asset_href(item)
        return href is not None \
            and (item_format == ItemFormat.dimap.value
                 or item_format == ItemFormat.terrasar.value
                 or item_format == ItemFormat.spot5.value)

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        met_file = self.get_asset_href(item)
        if raw_archive:
            AccessManager.zip(met_file, target_directory)
            return
        met_file_name = os.path.basename(met_file)
        # Default driver is GTiff
        driver_target = "GTiff"
        extension = '.tif'
        if (not target_format) or (target_format == 'native'):
            if item.properties.main_asset_format == AssetFormat.jpg2000.value:
                driver_target = "JP2OpenJPEG"
                extension = '.JP2'
            else:
                driver_target = "GTiff"
        elif target_format == "Jpeg2000":
            driver_target = "JP2OpenJPEG"
            extension = '.JP2'

        # If the projetion and the format are natives, just copy the file
        if (target_projection == target_format == 'native') and (not crop_wkt):
            if item.properties.item_format in [ItemFormat.dimap.value, ItemFormat.spot5.value]:
                self.copy_from_dimap(met_file, target_directory, extension)
            elif item.properties.item_format == ItemFormat.terrasar.value:
                self.copy_from_terrasarx(met_file, target_directory, extension)
            return
        if target_projection == 'native':
            target_projection = item.properties.proj__epsg
        target_file_name = os.path.splitext(met_file_name)[0] + extension
        images = []
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        if item.properties.item_format in [ItemFormat.dimap.value, ItemFormat.spot5.value]:
            images = list(map(lambda f: [f[0], os.path.splitext(f[1])[0] + extension], self.get_dimap_images(met_file, extension)))
        elif item.properties.item_format == ItemFormat.terrasar.value:
            images = list(map(lambda f: [f[0], os.path.splitext(f[1])[0] + extension], self.get_terrasarx_images(met_file, extension)))
        extract(images, crop_wkt, met_file, driver_target, target_projection, target_directory, target_file_name)

    def get_dimap_images(self, href: str, extension: str) -> list[tuple[str, str, str, str]]:
        href = AccessManager.prepare(href)

        dir_name = os.path.dirname(href)
        tree = ET.parse(href)
        root = tree.getroot()
        files_elements = root.findall('./Raster_Data/Data_Access/Data_Files/Data_File/DATA_FILE_PATH')

        georef_file_extension = '.TFW'
        if extension == '.JP2':
            georef_file_extension = '.J2W'

        files = list(map(lambda f: [os.path.join(dir_name, f.attrib["href"]),
                                    f.attrib["href"],
                                    os.path.join(dir_name, os.path.splitext(f.attrib["href"])[0] + georef_file_extension),
                                    os.path.splitext(f.attrib["href"])[0] + georef_file_extension], files_elements))
        return files

    def get_terrasarx_images(self, href: str, extension: str) -> list[tuple[str, str, str, str]]:
        href = AccessManager.prepare(href)

        dir_name = os.path.dirname(href)
        tree = ET.parse(href)
        root = tree.getroot()
        files_elements = root.findall('.productComponents/imageData/file/location')

        georef_file_extension = '.TFW'
        if extension == '.JP2':
            georef_file_extension = '.J2W'
        files = []
        for file in files_elements:
            f = [str(file.find('path').text), str(file.find('filename').text)]
            files.append([os.path.join(dir_name, f[0], f[1]), f[1],
                          os.path.join(dir_name, f[0], os.path.splitext(f[1])[0] + georef_file_extension),
                          os.path.splitext(f[1])[0] + georef_file_extension])
        return files

    def copy_from_dimap(self, href: str, target_directory: str, extension: str):
        files = self.get_dimap_images(href, extension)
        self.copy_from_met(files, target_directory)

    def copy_from_terrasarx(self, href: str, target_directory: str, extension: str):
        files = self.get_terrasarx_images(href, extension)
        self.copy_from_met(files, target_directory)

    def copy_from_met(self, files: list[tuple[str, str, str, str]], target_directory: str):
        for f in files:
            storage = AccessManager.resolve_storage(f[0])
            if AccessManager.exists(f[0]) and (os.path.isfile(f[0]) if storage.type == "file" else True):
                AccessManager.pull(f[0], target_directory + "/" + f[1])
            if AccessManager.exists(f[2]) and (os.path.isfile(f[2]) if storage.type == "file" else True):
                AccessManager.pull(f[2], target_directory + "/" + f[3])
