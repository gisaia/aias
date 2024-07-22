import os
import shutil
from pathlib import Path

from airs.core.models.model import AssetFormat, Item, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver
from extensions.aproc.proc.download.drivers.impl.utils import \
    make_raw_archive_zip


class Driver(DownloadDriver):

    # Implements drivers method
    @staticmethod
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        if item.properties.main_asset_format:
            return item.properties.main_asset_format == AssetFormat.geotiff.value or item.properties.main_asset_format == AssetFormat.jpg2000.value
        if item.assets.get("data") and item.assets.get("data").asset_format:
            return item.assets.get("data").asset_format == AssetFormat.geotiff or item.assets.get("data").asset_format == AssetFormat.jpg2000
        if item.assets.get("data") and item.assets.get("data").type:
            return item.assets.get("data").type.lower().startswith("image/tiff") or item.assets.get("data").type.lower().startswith("image/jp2")
        return False

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        asset = item.assets.get(Role.data.value)
        # Default driver is GTiff
        driver_target = "GTiff"
        if (not target_format) or (target_format == 'native'):
            if item.properties.main_asset_format == AssetFormat.jpg2000.value:
                driver_target = "JP2OpenJPEG"
            else:
                driver_target = "GTiff"
        elif target_format == "Jpeg2000" or target_format == AssetFormat.jpg2000.value:
            driver_target = "JP2OpenJPEG"

        extension = '.tif'
        if driver_target == "JP2OpenJPEG":
            extension = '.JP2'

        if raw_archive:
            make_raw_archive_zip(asset.href, target_directory)
            return
        if (target_projection == target_format == 'native') and (not crop_wkt):
            # If the projetion and the format are natives, just copy the file and the georef file
            georef_file_extensions = ['.tfw', ".TFW", ".J2W", ".j2w", ".aux.xml", ".AUX.XML"]
            for ext in georef_file_extensions:
                candidate = Path(asset.href).parent.joinpath(Path(asset.href).stem).with_suffix(ext)
                if candidate.exists() and candidate.is_file():
                    Driver.LOGGER.info("Copy {} to {}".format(candidate, target_directory))
                    shutil.copy(candidate, target_directory)
            shutil.copy(asset.href, target_directory)
            return
        
        # Some transformation to be done ...
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        target_file_name = Path(Path(asset.href).stem).with_suffix(extension)
        Driver.LOGGER.info("extract {} to {} in {} with projection {} and crop {}".format(asset.href, target_file_name, target_directory, target_projection, crop_wkt))
        extract([], crop_wkt, asset.href, driver_target, target_projection, target_directory, str(target_file_name))
