from airs.core.models.model import Asset, AssetFormat, Item, ItemFormat
from extensions.aproc.proc.access.manager import AccessManager
from extensions.aproc.proc.ingest.drivers.impl.image_driver_helper import \
    ImageDriverHelper
from extensions.aproc.proc.ingest.drivers.ingest_driver import IngestDriver


class Driver(IngestDriver):

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        IngestDriver.init(configuration)

    # Implements drivers method
    def supports(self, url: str) -> bool:
        try:
            return (url.lower().endswith(".tif") or url.lower().endswith(".tiff")) and AccessManager.is_file(url)
        except Exception as e:
            self.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        return ImageDriverHelper.identify_assets(self, "image/tiff", url)

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return ImageDriverHelper.get_item_id(self, url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        return ImageDriverHelper.to_item(self, ItemFormat.geotiff, AssetFormat.geotiff, url, assets)

    @staticmethod
    def get_main_asset_format(root):
        return AssetFormat.geotiff.value
