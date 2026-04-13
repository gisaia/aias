import io
import os
import re
import tempfile
from typing import Any
import zipfile
from time import time

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, ResourceType, Role)
from aias_common.access.manager import AccessManager
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
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        return extra_params.get("asset_type", "") == "cog" and resource.properties is not None and resource.properties.item_format is not None and resource.properties.item_format.lower() == ItemFormat.safe.value.lower()

    # Implements drivers method
    def create_assets(self, item: Item, asset_type: str) -> list[Asset]:
        if asset_type:
            if asset_type.lower() in Driver.SUPPORTED_ASSET_TYPES:
                self.LOGGER.info("adding {} to item {}".format(asset_type, item.id))
                assets = [self.__create_TCI_asset(item, asset_type)]

                # If the data asset is not zipped, create all bands COG
                if item.assets.get(Role.data.value).type != MimeType.ZIP.value:
                    assets.append(self.__create_all_bands_asset(item))
                return assets
            else:
                raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
        else:
            raise DriverException("Asset type must be provided.")

    def __create_TCI_asset(self, item: Item, asset_type: str):
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
        self.__build_TCI_COG(item, asset_location)
        asset.size = AccessManager.get_size(asset_location)
        return asset

    def __build_TCI_COG(self, item: Item, asset_location: str):
        href = self.get_asset_href(item)
        if href:
            self.LOGGER.info("Building cog for {}".format(item.id))

            from osgeo import gdal
            is_asset_zip = item.assets.get(Role.data.value).type == MimeType.ZIP.value
            if is_asset_zip:
                start = time()
                tci_file_path = self.__download_TCI_from_zip(href)
                self.LOGGER.info("Fetching the data took {} s".format(time() - start))
            else:
                start = time()
                tci_file_path = os.path.join(AccessManager.tmp_dir, os.path.basename(href))
                AccessManager.pull(href, tci_file_path)
                self.LOGGER.info("Fetching the data took {} s".format(time() - start))

            start = time()
            kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857', 'COMPRESS': 'DEFLATE', 'ZLEVEL': '9', 'BIGTIFF': 'IF_SAFER'}
            gdal.Warp(asset_location, tci_file_path, **kwargs)
            self.LOGGER.info("Creating COG took {} s".format(time() - start))

            os.remove(tci_file_path)  # !DELETE!
        else:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))

    def __download_TCI_from_zip(self, href: str):
        storage = AccessManager.resolve_storage(href)

        # With GS, it has been observed that performances for extracting a file directly from the zip remotely
        # Is far more slower than downloading the whole archive and then unzipping
        if storage.get_configuration().type == "gs" or AccessManager.is_download_required(href):
            # Create tmp file where data will be downloaded
            tmp_file = tempfile.NamedTemporaryFile("w+", suffix=".zip", delete=False).name

            # Download archive then extract it
            storage.pull(href, tmp_file)
            tci_file_path = self.__extract_TCI(tmp_file)

            # Clean-up
            os.remove(tmp_file)  # !DELETE!
        else:
            with AccessManager.stream(href) as fb:
                tci_file_path = self.__extract_TCI(fb)

        return tci_file_path

    def __extract_TCI(self, zip_file: str | io.TextIOWrapper):
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

    def __create_all_bands_asset(self, item: Item):
        asset = Asset(
            name='all_bands_cog',
            size=0,     # set once asset created
            href=None,  # set below
            asset_type=ResourceType.gridded.value,
            asset_format=AssetFormat.geotiff.value,
            roles=[Role.cog.value],
            type=MimeType.TIFF.value,
            title="all bands COG for {}/{}".format(item.collection, item.id),
            description="all bands COG for {}/{}".format(item.collection, item.id),
            proj__epsg=3857,
            airs__managed=True
        )
        asset_location = self.get_asset_filepath(item.id, asset)
        asset.href = asset_location
        self.__build_all_bands_COG(item, asset_location)
        asset.size = AccessManager.get_size(asset_location)

        return asset

    def __build_all_bands_COG(self, item: Item, asset_location: str):
        secondary_data_assets = list(filter(lambda a: Role.data.value in a.roles and a.name != Role.data.value, item.assets.values()))
        secondary_data_href = [a.href for a in secondary_data_assets]

        if secondary_data_href:
            secondary_data_href.sort()
            self.LOGGER.info("Building all bands cog for {}".format(item.id))
            vrt_file = tempfile.NamedTemporaryFile("w+", suffix=".zip", delete=False).name

            from osgeo import gdal
            with AccessManager.make_local_list(secondary_data_href) as local_assets:
                start = time()

                # Build VRT to facilitate COG built
                kwargs = {"separate": True, "resolution": "highest"}
                gdal.BuildVRT(vrt_file, local_assets, **kwargs)

                # Build COG from VRT
                kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
                gdal.Warp(asset_location, vrt_file, **kwargs)
                self.LOGGER.info("Creating all bands COG took {} s".format(time() - start))

            AccessManager.clean(vrt_file)  # !DELETE!
        else:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))
