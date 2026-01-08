import os
from typing import Any

from airs.core.models.model import Item
from aias_common.access.manager import AccessManager
from extensions.aproc.proc.download.drivers.download_driver import DownloadDriver
from extensions.aproc.proc.download.drivers.impl.utils import get_file_name


class Driver(DownloadDriver):

    def __init__(self):
        super().__init__()

    # Implements drivers method
    @staticmethod
    def init(configuration: dict):
        DownloadDriver.init(configuration)

    # Implements drivers method
    def supports(self, resource: Item, extra_params: dict[str, Any] = {}) -> bool:
        # simple copy does not support any transformation
        if extra_params.get("crop_wkt", "") or extra_params.get("target_projection", "") or extra_params.get("target_format", ""):
            return False
        href = self.get_asset_href(resource)
        return href is not None

    # Implements drivers method
    def fetch_and_transform(self, item: Item, target_directory: str, crop_wkt: str, target_projection: str, target_format: str, raw_archive: bool):
        href = self.get_asset_href(item)
        file_name = get_file_name(item, "archive" if raw_archive else target_format)
        self.LOGGER.debug("Copy {} in {}".format(href, target_directory))
        AccessManager.pull(href, os.path.join(target_directory, file_name))
