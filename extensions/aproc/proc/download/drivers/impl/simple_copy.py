import os
import shutil

import requests

from airs.core.models.model import Item, Role
from extensions.aproc.proc.download.drivers.driver import \
    Driver as DownloadDriver
from extensions.aproc.proc.download.drivers.impl.utils import get_file_name


class Driver(DownloadDriver):

    # Implements drivers method
    def init(configuration: dict):
        ...

    # Implements drivers method
    def supports(item: Item) -> bool:
        data = item.assets.get(Role.data.value)
        return data is not None and data.href is not None and (data.href.startswith("file://") or data.href.startswith("http://") or data.href.startswith("https://"))

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        data = item.assets.get(Role.data.value)
        file_name = get_file_name(item.id)
        if data is not None:
            if data.href.startswith("file://"):
                shutil.copy(data.href, os.path.join(target_directory, file_name))
            if data.href.startswith("http://") or data.href.startswith("https://"):
                response = requests.get(data.href)
                with open(os.path.join(target_directory, file_name), "wb") as f:
                    f.write(response.content)
