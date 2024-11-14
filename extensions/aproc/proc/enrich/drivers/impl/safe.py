import os
import re
import tempfile
import zipfile
from pathlib import Path

from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    ResourceType, Role)
from extensions.aproc.proc.enrich.drivers.driver import Driver as EnrichDriver
from extensions.aproc.proc.enrich.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.drivers.impl.utils import get_file_size
from extensions.aproc.proc.s3_configuration import \
    S3Configuration as Configuration


class Driver(EnrichDriver):

    SUPPORTED_ASSET_TYPES = [AssetFormat.cog.value.lower()]

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        Driver.configuration = Configuration.model_validate(configuration)

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
                    type="image/tiff",
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

    def __build_asset(item: Item, asset_type: str, asset_location: str):
        if asset_type.lower() == "cog":
            data_asset = item.assets.get(Role.data.value)
            if data_asset:
                Driver.LOGGER.info("Building cog for {}".format(item.id))

                import smart_open
                from osgeo import gdal

                with smart_open.open(data_asset.href, "rb",
                                     transport_params=Driver.configuration.get_storage_parameters(data_asset.href, Driver.LOGGER)) as fb:
                    with zipfile.ZipFile(fb) as raster_zip:
                        file_names = raster_zip.namelist()
                        raster_files = list(filter(lambda f: re.match(r".*/IMG_DATA/.*" + r"_TCI.jp2", f), file_names))

                        if len(raster_files) == 0:
                            raise DriverException("No TCI file found in the SAFE archive.")
                        if len(raster_files) > 1:
                            Driver.LOGGER.warning("More than one TCI file found, using the first one.")

                        tci_file_path = os.path.join(tempfile.gettempdir(), raster_files[0])
                        raster_zip.extract(raster_files[0], tempfile.gettempdir())

                        kwargs = {'format': 'COG', 'dstSRS': 'EPSG:3857'}
                        gdal.Warp(asset_location, tci_file_path, **kwargs)
                        os.remove(tci_file_path)
            else:
                raise DriverException("Data asset not found for {}/{}".format(item.collection, item.id))
        else:
            raise DriverException("Unsupported asset type {}. Supported types are : {}".format(asset_type, ", ".join(Driver.SUPPORTED_ASSET_TYPES)))
