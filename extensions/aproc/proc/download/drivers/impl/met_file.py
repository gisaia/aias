import os
from airs.core.models.model import Item, Role, ItemFormat
from aproc.core.settings import Configuration
from extensions.aproc.proc.download.drivers.driver import Driver as DownloadDriver
from datetime import datetime

from extensions.aproc.proc.download.drivers.impl.utils import make_raw_archive_zip
import shutil
import xml.etree.ElementTree as ET
from zipfile import ZipFile

class Driver(DownloadDriver):

    # Implements drivers method
    @staticmethod
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        if item.assets.get(Role.metadata.value) is not None:
            asset = item.assets.get(Role.metadata.value)
            file_name = os.path.basename(asset.href)
            return file_name.lower().endswith(".xml")
        else:
            return False
    
    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, file_name: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        asset = item.assets.get(Role.metadata.value)
        met_file = asset.href
        if raw_archive:
            make_raw_archive_zip(met_file, target_directory)
            return
        # If the projetion and the format are natives, just copy the file
        if target_projection == target_format == 'native':
            if item.properties.item_format == ItemFormat.dimap.value:
                self.copy_from_dimap(met_file,target_directory)
            elif item.properties.item_format == ItemFormat.terrasar.value:
                self.copy_from_terrasarx(met_file,target_directory)
            return
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        import pyproj
        met_file_name = os.path.basename(met_file)
        epsg_target = pyproj.Proj(target_projection)
        # Default driver is GTiff
        driver_target = "GTiff"
        if not target_format:
            raise Exception("target_format must be either Geotiff or Jpeg2000")
        if target_format == "Geotiff":
            driver_target = "GTiff"
            target_file_name = os.path.splitext(met_file_name)[0]  + datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+'.tif'
        elif target_format == "Jpeg2000":
            driver_target = "JP2OpenJPEG"
            target_file_name = os.path.splitext(met_file_name)[0]  + datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+'.JP2'
        extract(crop_wkt, met_file, driver_target, epsg_target, target_directory, target_file_name,
                      target_projection)


    def copy_from_dimap(self,href: str, target_directory: str):
        dir_name = os.path.dirname(href)
        file_name = os.path.basename(href)
        tree = ET.parse(href)
        root = tree.getroot()
        files_elements = root.findall('./Raster_Data/Data_Access/Data_Files/Data_File/DATA_FILE_PATH')
        files = list(map(lambda f: [os.path.join(dir_name, f.attrib["href"]),f.attrib["href"]], files_elements))
        self.copy_from_met(files,target_directory,file_name)

    def copy_from_terrasarx(self,href: str, target_directory: str):
        dir_name = os.path.dirname(href)
        file_name = os.path.basename(href)
        tree = ET.parse(href)
        root = tree.getroot()
        files_elements = root.findall('.productComponents/imageData/file/location')
        print(files_elements)
        files = []
        for file in files_elements:
            f = [str(file.find('path').text), str(file.find('filename').text)]
            files.append([os.path.join(dir_name,f[0],f[1]),f[1]])
        self.copy_from_met(files,target_directory,file_name)


    def copy_from_met(self,files,target_directory,file_name):
        # If the met_file reference only one file we copy it
        if len(files) == 1:
            shutil.copyfile(files[0][0], os.path.join(target_directory,files[0][1]))
            return
        # If the met_file reference several files we zip it in one zip file
        elif len(files) > 1:
            tif_zip_file = ZipFile(os.path.join(target_directory,file_name+".zip"), mode='a')
            for f in files:
                valid_and_exist = os.path.isfile(f[0]) and os.path.exists(f[0])
                if valid_and_exist:
                    tif_zip_file.write(f[0],f[1])
            tif_zip_file.close()
        return
