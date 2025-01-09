import shutil
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from extensions.aproc.proc.access.storages.abstract import AbstractStorage


class FileStorage(AbstractStorage):
    type: Literal["file"] = "file"
    # TODO: add authorised paths

    def get_storage_parameters(self):
        return {}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        return scheme == "" or scheme == "file"

    def exists(self, href: str):
        return Path(href).exists()

    def get_rasterio_session(self):
        return None

    def pull(self, href: str, dst: str):
        super().pull(href, dst)
        shutil.copy(href, dst)

    # @override method of AbstractStorage
    def prepare_for_local_process(self, href: str):
        # Skip pull as file is already present locally
        return href
