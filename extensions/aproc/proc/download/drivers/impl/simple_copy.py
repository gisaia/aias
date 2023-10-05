import os
import shutil
import requests
from airs.core.models.model import Item, Role
from aproc.core.settings import Configuration
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver


class Driver(DownloadDriver):

    # Implements drivers method
    def init(configuration: Configuration):
        ...

    # Implements drivers method
    def supports(item: Item) -> bool:
        data = item.assets.get(Role.data.value)
        return data is not None and data.href is not None and (data.href.startswith("file://") or data.href.startswith("http://") or data.href.startswith("https://"))
    
    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, file_name: str, crop_wkt: str, target_projection: str, target_format: str):
        data = item.assets.get(Role.data.value)
        if data is not None:
            if data.href.startswith("file://"):
                shutil.copy(data.href, os.path.join(target_directory, file_name))
            if data.href.startswith("http://") or data.href.startswith("https://"):
                response = requests.get(data.href)
                with open(os.path.join(target_directory, file_name), "wb") as f:
                    f.write(response.content)
