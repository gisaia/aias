from aias_common.access.manager import AccessManager
from airs.core.models.model import (Asset, AssetFormat, Item, ItemFormat,
                                    MimeType, Role)
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.impl.utils import (downsample_image,
                                                             geotiff_to_jpg)
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        assets = ImageDriverHelper.identify_assets(self, MimeType.JPEG2000, url)
        assets.append(
            Asset(
                href=url,
                roles=[Role.archive.value],
                name=Role.archive.value,
                type=MimeType.JPEG2000.value,
                description=Role.archive.value,
                airs__managed=False,
                asset_format=AssetFormat.jpg2000.value
            )
        )
        return assets

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        if AccessManager.is_local(url):
            quicklook = ImageDriverHelper.prepare_preview_asset(self, url, Role.overview, MimeType.JPG, AssetFormat.jpg)
            geotiff_to_jpg(url, 25, 25, quicklook.href)
            quicklook.size = AccessManager.get_size(quicklook.href)
            assets.append(quicklook)

            thumbnail = ImageDriverHelper.prepare_preview_asset(self, url, Role.thumbnail, MimeType.JPG, AssetFormat.jpg)
            downsample_image(quicklook.href, thumbnail.href, 4)
            thumbnail.size = AccessManager.get_size(thumbnail.href)
            assets.append(thumbnail)
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        item = ImageDriverHelper.to_item(self, ItemFormat.jpeg2000, AssetFormat.jpg2000, url, assets)
        return item

    @staticmethod
    def get_main_asset_format(root):
        return AssetFormat.jpg2000.value

    def __check_path__(self, path: str):
        return path.lower().endswith((".jp2", ".j2k", ".jpf", ".jpm", ".jpg2", ".j2c", ".jpc", ".jpx")) \
            and AccessManager.is_file(path)
