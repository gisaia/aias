import enum
import os
import shutil
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from extensions.aproc.proc.access.storages.abstract import AbstractStorage


class AccessType(enum.Enum):
    READ = "read"
    WRITE = "write"


class FileStorage(AbstractStorage):
    type: Literal["file"] = "file"
    authorized_paths: list[str]
    writable: bool

    def get_storage_parameters(self):
        return {}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        return scheme == "" or scheme == "file"

    def exists(self, href: str):
        return Path(href).exists()

    def get_rasterio_session(self):
        return {}

    def is_path_authorized(self, href: str, action: AccessType) -> bool:
        if action == AccessType.WRITE and not self.writable:
            return False
        return any(list(map(lambda p: os.path.commonpath([p, href]) == p, self.authorized_paths)))

    def pull(self, href: str, dst: str):
        super().pull(href, dst)

        if not self.is_path_authorized(dst, AccessType.WRITE):
            raise ValueError('The desired output path is not authorized')

        shutil.copy(href, dst)

    def is_file(self, href: str):
        return os.path.isfile(href)

    def is_dir(self, href: str):
        return os.path.isdir(href)
