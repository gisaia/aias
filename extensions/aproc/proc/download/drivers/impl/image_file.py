from pathlib import Path

from airs.core.models.model import AssetFormat, Item, ItemFormat, Role
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.download.drivers.download_driver import DownloadDriver


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
            and (item_format == ItemFormat.geotiff.value
                 or item_format == ItemFormat.jpeg2000.value
                 or item_format == ItemFormat.ast_dem.value
                 or item_format == ItemFormat.csk.value
                 or item_format == ItemFormat.digitalglobe.value
                 or item_format == ItemFormat.geoeye.value
                 or item_format == ItemFormat.rapideye.value)

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str,
                            target_format: str, raw_archive: bool):
        href = self.get_asset_href(item)
        if raw_archive:
            if item.properties.item_format and \
                    item.properties.item_format in [ItemFormat.geotiff.value, ItemFormat.jpeg2000.value]:
                self.LOGGER.debug("Copy {} in {}".format(href, target_directory))
                AccessManager.pull(href, target_directory, True)
                if item.assets and item.assets.get(Role.extent.value) and AccessManager.exists(
                        item.assets.get(Role.extent.value).href):
                    self.LOGGER.debug("Geo file {} detected and copied".format(item.assets.get(Role.extent.value).href))
                    AccessManager.pull(item.assets.get(Role.extent.value).href, target_directory, True)
                if item.assets and item.assets.get(Role.metadata.value) and AccessManager.exists(
                        item.assets.get(Role.metadata.value).href):
                    self.LOGGER.debug("Metadata {} detected and copied".format(item.assets.get(Role.metadata.value).href))
                    AccessManager.pull(item.assets.get(Role.metadata.value).href, target_directory, True)
            else:
                AccessManager.zip(href, target_directory)
                return
        # Default driver is GTiff
        driver_target = "GTiff"
        extension = '.tif'
        if (not target_format) or (target_format == 'native'):
            if item.properties.main_asset_format == AssetFormat.jpg2000.value:
                driver_target = "JP2OpenJPEG"
                extension = '.JP2'
        elif target_format in ["Jpeg2000", AssetFormat.jpg2000.value]:
            driver_target = "JP2OpenJPEG"
            extension = '.JP2'

        if ((not target_projection or target_projection == 'native') and (
                not target_format or target_format == 'native')) and (not crop_wkt):
            # If the projetion and the format are natives, just copy the file and the georef file
            if item.assets and item.assets.get(Role.extent.value) is not None and AccessManager.exists(item.assets.get(Role.extent.value).href):
                geo_ext_file = item.assets.get(Role.extent.value).href
                self.LOGGER.info("Copy {} to {}".format(geo_ext_file, target_directory))
                AccessManager.pull(geo_ext_file, target_directory, True)
            self.LOGGER.debug("Copy {} in {}".format(href, target_directory))
            AccessManager.pull(href, target_directory, True)
            return
        if target_projection == 'native':
            target_projection = item.properties.proj__epsg

        # Some transformation to be done ...
        from extensions.aproc.proc.download.drivers.impl.utils import extract
        target_file_name = Path(Path(href).stem).with_suffix(extension)
        self.LOGGER.info("Extract {} to {} in {} with projection {} and crop {}".format(href, target_file_name,
                                                                                        target_directory,
                                                                                        target_projection, crop_wkt))
        extract([], crop_wkt, href, driver_target, target_projection, target_directory, str(target_file_name))
