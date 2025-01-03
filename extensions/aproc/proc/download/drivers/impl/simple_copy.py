import os
import shutil

import requests

from airs.core.models.model import Item
from extensions.aproc.proc.download.drivers.download_driver import DownloadDriver
from extensions.aproc.proc.download.drivers.impl.utils import get_file_name


class Driver(DownloadDriver):

    def __init__(self):
        super().__init__()

    # Implements drivers method
    def init(configuration: dict):
        DownloadDriver.init(configuration)

    # Implements drivers method
    def supports(self, item: Item) -> bool:
        href = self.get_asset_href(item)
        return href is not None\
            and (href.startswith("file://")
                 or href.startswith("http://")
                 or href.startswith("https://"))

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        href = self.get_asset_href(item)
        file_name = get_file_name(item.id)
        if href.startswith("file://"):
            shutil.copy(href, os.path.join(target_directory, file_name))
        if href.startswith("http://") or href.startswith("https://"):
            response = requests.get(href)
            with open(os.path.join(target_directory, file_name), "wb") as f:
                f.write(response.content)
