import io
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from time import time
from urllib.parse import urlparse

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat, MimeType,
                                    ResourceType, Role)
from extensions.aproc.proc.enrich.drivers.driver import Driver as EnrichDriver
from extensions.aproc.proc.enrich.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import get_file_size
from extensions.aproc.proc.s3_configuration import S3Configuration


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower()]

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        Driver.configuration = S3Configuration.model_validate(configuration)

    # Implements drivers method
    @staticmethod
    def supports(item: Item) -> bool:
        return item.properties.item_format and item.properties.item_format.lower() == ItemFormat.safe.value.lower()

    # Implements drivers method
    def create_asset(self, item: Item, asset_type: str) -> tuple[Asset, str]:
        if asset_type:
            if asset_type.lower() in Driver.SUPPORTED_ASSET_TYPES:
                Driver.LOGGER.info("adding {} to item {}".format(asset_type, item.id))
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
                Path(asset_location).touch()
                Driver.__build_asset(item, asset_type, asset_location)
                asset.size = get_file_size(asset_location)
                return asset, asset_location
            else:
                raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
        else:
            raise DriverException("Asset type must be provided.")

    @staticmethod
    def __build_asset(item: Item, asset_type: str, asset_location: str):
        if asset_type.lower() == "cog":
            href = Driver.get_asset_href(item)
            if href:
                Driver.LOGGER.info("Building cog for {}".format(item.id))

                from osgeo import gdal
                start = time()
                tci_file_path = Driver.__download_TCI(href)
                Driver.LOGGER.info("Fetching the data took {} s".format(time() - start))

                start = time()
                kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
                gdal.Warp(asset_location, tci_file_path, **kwargs)
                Driver.LOGGER.info("Creating COG took {} s".format(time() - start))
                os.remove(tci_file_path)
            else:
                raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))
        else:
            raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))

    @staticmethod
    def __download_TCI(href: str):
        storage_type = urlparse(href).scheme
        transport_params = Driver.configuration.get_storage_parameters(href, Driver.LOGGER)

        # With GS, it has been observed that performances for extracting a file directly from the zip remotely
        # Is far more slower than downloading the whole archive and then unzipping
        if storage_type == "gs":
            from google.cloud.storage import Client

            storage_client: Client = transport_params["client"]
            bucket = storage_client.bucket(urlparse(href).netloc)
            blob = bucket.blob(urlparse(href).path[1:])

            # Download archive then extract it
            tmp_file = tempfile.NamedTemporaryFile("w+", suffix=".zip", delete=False).name
            blob.download_to_filename(tmp_file)
            tci_file_path = Driver.__extract(tmp_file)

            # Remove temporary archive
            os.remove(tmp_file)
        elif Driver.configuration.is_download_required(href):
            import requests

            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(href, headers=transport_params["headers"],
                             stream=True, verify=False)

            tmp_asset = os.path.join(tempfile.gettempdir(), urlparse(href).path.strip("/").split("/")[-1])
            if (os.path.splitext(tmp_asset)[1] != ".zip"):
                tmp_asset = os.path.splitext(tmp_asset)[0] + ".zip"

            with open(tmp_asset, "wb") as out_file:
                shutil.copyfileobj(r.raw, out_file)

            tci_file_path = Driver.__extract(tmp_asset)
            os.remove(tmp_asset)
        else:
            import smart_open

            with smart_open.open(href, "rb", transport_params=transport_params) as fb:
                tci_file_path = Driver.__extract(fb)

        return tci_file_path

    @staticmethod
    def __extract(zip_file: str | io.TextIOWrapper):
        with zipfile.ZipFile(zip_file) as raster_zip:
            file_names = raster_zip.namelist()
            raster_files = list(filter(lambda f: re.match(r".*/IMG_DATA/.*" + r"_TCI.jp2", f), file_names))

            if len(raster_files) == 0:
                raise DriverException("No TCI file found in the SAFE archive.")
            if len(raster_files) > 1:
                Driver.LOGGER.warning("More than one TCI file found, using the first one.")

            tci_file_path = os.path.join(tempfile.gettempdir(), raster_files[0])
            raster_zip.extract(raster_files[0], tempfile.gettempdir())

        return tci_file_path
