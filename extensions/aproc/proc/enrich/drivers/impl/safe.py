import io
import os
import re
import tempfile
import zipfile
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower()]

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        EnrichDriver.init(configuration)

    # Implements drivers method
    def supports(self, item: Item) -> bool:
        return item.properties.item_format and item.properties.item_format.lower() == ItemFormat.safe.value.lower()

    # Implements drivers method
    def create_asset(self, item: Item, asset_type: str) -> tuple[Asset, str]:
        if asset_type:
            if asset_type.lower() in Driver.SUPPORTED_ASSET_TYPES:
                self.LOGGER.info("adding {} to item {}".format(asset_type, item.id))
                asset = Asset(
                    name=Role.cog.value,
                    size=0,     # set once asset created
                    href=None,  # set below
                    asset_type=ResourceType.gridded.value,
                    asset_format=AssetFormat.geotiff.value,
                    roles=[Role.cog.value],
                    type=MimeType.TIFF.value,
                    title="{} for {}/{}".format(asset_type, item.collection, item.id),
                    description="{} for {}/{}".format(asset_type, item.collection, item.id),
                    proj__epsg=3857,
                    airs__managed=True
                )
                asset_location = self.get_asset_filepath(item.id, asset)
                asset.href = asset_location
                self.__build_asset(item, asset_type, asset_location)
                asset.size = AccessManager.get_file_size(asset_location)
                return asset, asset_location
            else:
                raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
        else:
            raise DriverException("Asset type must be provided.")

    def __build_asset(self, item: Item, asset_type: str, asset_location: str):
        if asset_type.lower() == "cog":
            href = self.get_asset_href(item)
            if href:
                self.LOGGER.info("Building cog for {}".format(item.id))

                from osgeo import gdal
                start = time()
                tci_file_path = self.__download_TCI(href)
                self.LOGGER.info("Fetching the data took {} s".format(time() - start))

                start = time()
                kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
                gdal.Warp(asset_location, tci_file_path, **kwargs)
                self.LOGGER.info("Creating COG took {} s".format(time() - start))
                os.remove(tci_file_path)
            else:
                raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))
        else:
            raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))

    def __download_TCI(self, href: str):
        storage = AccessManager.resolve_storage(href)

        # With GS, it has been observed that performances for extracting a file directly from the zip remotely
        # Is far more slower than downloading the whole archive and then unzipping
        if storage.type == "gs" or AccessManager.is_download_required(href):
            # Create tmp file where data will be downloaded
            tmp_file = tempfile.NamedTemporaryFile("w+", suffix=".zip", delete=False).name

            # Download archive then extract it
            storage.pull(href, tmp_file)
            tci_file_path = self.__extract(tmp_file)

            # Clean-up
            os.remove(tmp_file)
        else:
            with AccessManager.stream(href) as fb:
                tci_file_path = self.__extract(fb)

        return tci_file_path

    def __extract(self, zip_file: str | io.TextIOWrapper):
        with zipfile.ZipFile(zip_file) as raster_zip:
            file_names = raster_zip.namelist()
            raster_files = list(filter(lambda f: re.match(r".*/IMG_DATA/.*" + r"_TCI.jp2", f), file_names))

            if len(raster_files) == 0:
                raise DriverException("No TCI file found in the SAFE archive.")
            if len(raster_files) > 1:
                self.LOGGER.warning("More than one TCI file found, using the first one.")

            tci_file_path = os.path.join(AccessManager.tmp_dir, raster_files[0])
            raster_zip.extract(raster_files[0], AccessManager.tmp_dir)

        return tci_file_path
