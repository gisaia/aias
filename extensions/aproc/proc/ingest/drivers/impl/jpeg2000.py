from airs.core.models.model import Asset, AssetFormat, Item, ItemFormat
from aias_common.access.manager import AccessManager
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
            return (url.lower().endswith(".jp2")
                    or url.lower().endswith(".j2k")
                    or url.lower().endswith(".jpf")
                    or url.lower().endswith(".jpm")
                    or url.lower().endswith(".jpg2")
                    or url.lower().endswith(".j2c")
                    or url.lower().endswith(".jpc")
                    or url.lower().endswith(".jpx")
                    or url.lower().endswith(".jpc")) and AccessManager.is_file(url)
        except Exception as e:
            self.LOGGER.warn(e)
            return False

    # Implements drivers method
    def identify_assets(self, url: str) -> list[Asset]:
        return ImageDriverHelper.identify_assets(self, "image/jp2", url)

    # Implements drivers method
    def fetch_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return ImageDriverHelper.fetch_assets(self, url, assets)

    # Implements drivers method
    def get_item_id(self, url: str) -> str:
        return ImageDriverHelper.get_item_id(self, url)

    # Implements drivers method
    def transform_assets(self, url: str, assets: list[Asset]) -> list[Asset]:
        return assets

    # Implements drivers method
    def to_item(self, url: str, assets: list[Asset]) -> Item:
        with AccessManager.make_local(url + ".aux.xml"):
            item = ImageDriverHelper.to_item(self, ItemFormat.jpeg2000, AssetFormat.jpg2000, url, assets)
        return item

    @staticmethod
    def get_main_asset_format(root):
        return AssetFormat.jpg2000.value
