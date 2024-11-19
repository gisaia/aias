import shutil
from pathlib import Path

from airs.core.models.model import AssetFormat, Item, ItemFormat, Role
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver
from extensions.aproc.proc.download.drivers.impl.utils import \
    make_raw_archive_zip


class Driver(DownloadDriver):

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        ...

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        item_format = item.properties.item_format
        return item_format == ItemFormat.geotiff.value or \
               item_format == ItemFormat.jpeg2000.value or \
               item_format == ItemFormat.ast_dem.value or \
               item_format == ItemFormat.csk.value or \
               item_format == ItemFormat.digitalglobe.value or \
               item_format == ItemFormat.geoeye.value or \
               item_format == ItemFormat.rapideye.value

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str,
                            target_format: str, raw_archive: bool):
        asset = item.assets.get(Role.data.value)
        if raw_archive:
            if item.properties.item_format and (
                    item.properties.item_format == ItemFormat.geotiff.value or item.properties.item_format == ItemFormat.jpeg2000.value):
                Driver.LOGGER.debug("copy {} in {}".format(asset.href, target_directory))
                shutil.copy(asset.href, target_directory)
                if item.assets and item.assets.get(Role.extent.value) and Path(
                        item.assets.get(Role.extent.value).href).exists():
                    Driver.LOGGER.debug("geo file {} detected and copied".format(item.assets.get(Role.extent.value).href))
                    shutil.copy(item.assets.get(Role.extent.value).href, target_directory)
                if item.assets and item.assets.get(Role.metadata.value) and Path(
                        item.assets.get(Role.metadata.value).href).exists():
                    Driver.LOGGER.debug("metadata {} detected and copied".format(item.assets.get(Role.metadata.value).href))
                    shutil.copy(item.assets.get(Role.metadata.value).href, target_directory)
            else:
                make_raw_archive_zip(asset.href, target_directory)
                return
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

        if ((not target_projection or target_projection == 'native') and (
                not target_format or target_format == 'native')) and (not crop_wkt):
            # If the projetion and the format are natives, just copy the file and the georef file
            if item.assets and item.assets.get(Role.extent.value) is not None and Path(item.assets.get(Role.extent.value).href).exists():
                geo_ext_file = item.assets.get(Role.extent.value).href
                Driver.LOGGER.info("Copy {} to {}".format(geo_ext_file, target_directory))
                shutil.copy(geo_ext_file, target_directory)
            Driver.LOGGER.debug("copy {} in {}".format(asset.href, target_directory))
            shutil.copy(asset.href, target_directory)
            return
        if target_projection == 'native':
            target_projection = item.properties.proj__epsg
        # Some transformation to be done ...
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        target_file_name = Path(Path(asset.href).stem).with_suffix(extension)
        Driver.LOGGER.info("extract {} to {} in {} with projection {} and crop {}".format(asset.href, target_file_name,
                                                                                          target_directory,
                                                                                          target_projection, crop_wkt))
        extract([], crop_wkt, asset.href, driver_target, target_projection, target_directory, str(target_file_name))
