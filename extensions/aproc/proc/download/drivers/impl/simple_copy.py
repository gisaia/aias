import os
import shutil
import requests
from airs.core.models.model import Item
from aproc.core.settings import Configuration
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver


class Driver(DownloadDriver):

    # Implements drivers method
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    def supports(item: Item, asset_name: str) -> bool:
        return asset_name is not None and item.assets is not None and item.assets.get(asset_name) is not None and item.assets.get(asset_name).href is not None and (item.assets.get(asset_name).href.startswith("file://") or item.assets.get(asset_name).href.startswith("http://") or item.assets.get(asset_name).href.startswith("https://"))
    
    # Implements drivers method
    def fetch_and_transform(self, item: Item, asset_name: str, target_directory: str, file_name: str, crop_wkt: str, target_projection: str, target_format: str):
        if item.assets.get(asset_name).href.startswith("file://"):
            shutil.copy(item.assets.get(asset_name).href, os.path.join(target_directory, file_name))
        if item.assets.get(asset_name).href.startswith("http://") or item.assets.get(asset_name).href.startswith("https://"):
            response = requests.get(item.assets.get(asset_name).href)
            with open(os.path.join(target_directory, file_name), "wb") as f:
                f.write(response.content)
