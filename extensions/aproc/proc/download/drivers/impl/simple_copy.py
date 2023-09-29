import os
import shutil

from airs.core.models.model import Item
from aproc.core.settings import Configuration
from extensions.aproc.proc.ingest.drivers.driver import \
    Driver as DownloadDriver


class Driver(DownloadDriver):

    # Implements drivers method
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    def supports(item: Item, asset_name: str) -> bool:
        return asset_name is not None and item.assets.get(asset_name) is not None and item.assets.get(asset_name).href.startswith("file://")
    
    # Implements drivers method
    def fetch_and_transform(self, item: Item, asset_name: str, target_directory: str, file_name: str, crop_wkt: str, target_projection: str, target_format: str):
        shutil.copy(item.assets.get(asset_name).href, os.path.join(target_directory, file_name))