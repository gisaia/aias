import enum
import os
import shutil
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field

from extensions.aproc.proc.access.storages.abstract import AbstractStorage


class AccessType(enum.Enum):
    READ = "read"
    WRITE = "write"


class FileStorage(AbstractStorage):
    type: Literal["file"] = "file"
    writable_paths: list[str] = Field(default=[])
    readable_paths: list[str] = Field(default=[])

    def get_storage_parameters(self):
        return {}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        return (scheme == "" or scheme == "file") and self.is_path_authorized(href, AccessType.READ)

    def exists(self, href: str):
        return Path(href).exists()

    def get_rasterio_session(self):
        return {}

    def is_path_authorized(self, href: str, action: AccessType) -> bool:
        if action == AccessType.WRITE:
            paths = self.writable_paths
        if action == AccessType.READ:
            paths = list([*self.readable_paths, *self.writable_paths])
        return any(list(map(lambda p: os.path.commonpath([p, href]) == p, paths)))

    def pull(self, href: str, dst: str):
        super().pull(href, dst)

        if not self.is_path_authorized(dst, AccessType.WRITE):
            raise ValueError('The desired output path is not authorized')

        shutil.copy(href, dst)

    def is_file(self, href: str):
        return os.path.isfile(href)

    def is_dir(self, href: str):
        return os.path.isdir(href)
