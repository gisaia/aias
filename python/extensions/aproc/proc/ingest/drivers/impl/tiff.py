from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Role)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver
import os


class Driver(IngestDriver):

    configuration: dict = {}

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)
        Driver.configuration = configuration or {}

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = ImageDriverHelper.identify_assets(self, MimeType.TIFF, AssetFormat.geotiff, url)
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if IngestDriver.must_build_preview(Driver.configuration, url, local_remote_both="both"):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(url, Driver.OVERVIEW_FROM_TIFF_PCT, Driver.OVERVIEW_FROM_TIFF_PCT, quicklook.href, stretch=Driver.configuration.get('overview_stretch', True))
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, Driver.THUMBNAIL_DOWNSAMPLE_FACTOR)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    def load_metadata(self, url: str) -> object:
        return ImageDriverHelper.load_metadata(self, url)

    def build_core_item(self, url: str, assets: list[Asset], metadata: object) -> Item:
        return ImageDriverHelper.build_core_item(self, url, ItemFormat.geotiff, AssetFormat.geotiff, assets, metadata)

    def add_major_metadata(self, url: str, item: Item, metadata: object) -> Item:
        item.properties.secondary_id = os.path.basename(url)
        return item

    def add_minor_metadata(self, url: str, item: Item, metadata: object) -> Item:
        return item

    def __check_path__(self, path: str):
        return path.lower().endswith((".tif", ".tiff")) and AccessManager.is_file(path)
