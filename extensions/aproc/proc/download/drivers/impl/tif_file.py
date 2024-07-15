import os
import shutil

from airs.core.models.model import Item, Role, AssetFormat
from aproc.core.settings import Configuration
from extensions.aproc.proc.download.drivers.driver import Driver as DownloadDriver

from extensions.aproc.proc.download.drivers.impl.utils import make_raw_archive_zip


class Driver(DownloadDriver):

    # Implements drivers method
    @staticmethod
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        if item.assets.get(Role.data.value) is not None:
            asset = item.assets.get(Role.data.value)
            file_name = os.path.basename(asset.href)
            return file_name.lower().endswith(".tif")
        else:
            return False
    
    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        asset = item.assets.get(Role.data.value)
        tif_file = asset.href
        tif_file_name = os.path.basename(tif_file)
        if raw_archive:
            make_raw_archive_zip(tif_file, target_directory)
            return
        if (target_projection == target_format == 'native') and (not crop_wkt):
            # If the projetion and the format are natives, just copy the file and the georef file
            georef_file_extension = '.TFW'
            if item.properties.main_asset_format == AssetFormat.jpg2000.value:
                georef_file_extension = '.J2W'
            shutil.copyfile(tif_file, os.path.join(target_directory, tif_file_name))
            georef_file_name = os.path.splitext(tif_file_name)[0]+georef_file_extension
            dir_name = os.path.dirname(tif_file)
            georef_file = os.path.join(dir_name,georef_file_name)
            valid_and_exist = os.path.isfile(georef_file) and os.path.exists(georef_file)
            if valid_and_exist:
                shutil.copyfile(georef_file, os.path.join(target_directory, georef_file_name))
            return
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        # Default driver is GTiff
        driver_target = "GTiff"
        extension='.tif'
        if (not target_format) or (target_format == 'native'):
            if item.properties.main_asset_format == AssetFormat.jpg2000.value:
                driver_target = "JP2OpenJPEG"
            else:
                driver_target = "GTiff"
        elif target_format == "Jpeg2000":
            driver_target = "JP2OpenJPEG"
        if driver_target == "JP2OpenJPEG":
            extension='.JP2'
        target_file_name = os.path.splitext(tif_file_name)[0] + extension
        extract([],crop_wkt, tif_file, driver_target, target_projection, target_directory, target_file_name)




