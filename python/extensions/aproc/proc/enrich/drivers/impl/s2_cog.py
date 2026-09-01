import io
import os
import re
import tempfile
import zipfile
from time import time
from typing import Any

from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Role)
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.enrich.drivers.enrich_driver import EnrichDriver
from extensions.aproc.proc.enrich.drivers.impl.cog_builder_helper import \
    CogBuilderHelper


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower(), AssetFormat.overview_cog.value.lower(), AssetFormat.all_bands_cog.value.lower()]

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        CogBuilderHelper.init(Driver, configuration)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        # Is it able to build the requested enrichment type?
        if self.supports_format(resource, extra_params, Driver.SUPPORTED_ASSET_TYPES):
            # Is it a SAFE archive?
            if resource.properties and resource.properties.item_format and resource.properties.item_format.lower() == ItemFormat.safe.value.lower():
                # Does it have a data asset?
                if resource.assets.get(Role.data.value) and resource.assets.get(Role.data.value).href:
                    # If a all band cog is requested, check that the data asset is not a zip (SAFE archive)
                    if self.supports_format(resource, extra_params, [AssetFormat.all_bands_cog.value.lower()]):
                        if resource.assets.get(Role.data.value).type != MimeType.ZIP.value:
                            return True
                        else:
                            return False
                    else:
                        # no all band cog requested, so we can build the TCI COG from the SAFE archive
                        return True
        return False

    # Implements drivers method
    def create_enrichment(self, item: Item, enrichment: str) -> list[Asset]:
        if enrichment.lower() == AssetFormat.cog.value.lower() or enrichment.lower() == AssetFormat.overview_cog.value.lower():
            return [self.__create_TCI_asset(item, enrichment)]
        elif enrichment.lower() == AssetFormat.all_bands_cog.value.lower():
            # If the data asset is not zipped, create all bands COG
            if item.assets.get(Role.data.value).type != MimeType.ZIP.value:
                return [self.__create_all_bands_asset(item)]
            else:
                raise DriverException("Cannot create all bands COG from a zipped SAFE archive. Please provide a SAFE archive with unzipped data assets.")
        else:
            raise DriverException("Unsupported asset type {}. Supported types are : {}".format(enrichment, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))

    def __create_TCI_asset(self, item: Item, enrichment: str):
        cog_max_width_or_height = Driver.configuration['cog_max_width_or_height']
        if enrichment == AssetFormat.overview_cog.value.lower():
            cog_max_width_or_height = Driver.configuration['cog_overview_max_width_or_height']

        target_asset_location = self.get_target_asset_filepath(item.id, enrichment)
        self.__build_TCI_COG(item, target_asset_location, cog_max_width_or_height)
        return CogBuilderHelper.create_asset(item, enrichment, target_asset_location)

    def __build_TCI_COG(self, item: Item, target_asset_location: str, cog_max_width_or_height: int):
        href = self.get_asset_href(item)
        if href:
            self.LOGGER.info("Building cog for {}".format(item.id))

            from osgeo import gdal
            gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())

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

            CogBuilderHelper.build(tci_file_path, target_asset_location, max_px_width_or_height=cog_max_width_or_height)
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
        target_asset_location = self.get_target_asset_filepath(item.id, AssetFormat.all_bands_cog.value)
        self.__build_all_bands_COG(item, target_asset_location)

        return CogBuilderHelper.create_asset(item, AssetFormat.all_bands_cog.value.lower(), target_asset_location)

    def __build_all_bands_COG(self, item: Item, target_asset_location: str):
        band_assets = list(filter(lambda a: Role.data.value in a.roles and a.name != Role.data.value, item.assets.values()))
        band_files = [a.href for a in band_assets]

        if band_files:
            band_files.sort()
            self.LOGGER.info("Building all bands cog for {} made of {}".format(item.id, ", ".join(band_files)))
            source_files_vrt = tempfile.NamedTemporaryFile("w+", suffix=".files", delete=False).name

            from osgeo import gdal
            gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())
            with AccessManager.make_local_list(band_files) as local_assets:

                # Build VRT to facilitate COG built
                kwargs = {"separate": True, "resolution": "highest"}
                gdal.BuildVRT(source_files_vrt, local_assets, **kwargs)
                all_bands_cog_max_width_or_height = Driver.configuration['all_bands_cog_max_width_or_height']
                CogBuilderHelper.build(source_files_vrt, target_asset_location, max_px_width_or_height=all_bands_cog_max_width_or_height)

            AccessManager.clean(source_files_vrt)  # !DELETE!
        else:
            raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))
