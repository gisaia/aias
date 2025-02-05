import time
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field

from extensions.aproc.proc.access.storages.abstract import AbstractStorage
from extensions.aproc.proc.access.storages.utils import (requests_exists,
                                                         requests_get,
                                                         requests_head)


class HttpStorage(AbstractStorage):
    type: Literal["http"] = "http"
    is_local: Literal[False] = False
    headers: dict[str, str] = Field(default={})
    domain: str
    force_download: bool = Field(default=False)

    def get_storage_parameters(self):
        return {"headers": self.headers}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc

        return scheme == self.type and netloc == self.domain

    def exists(self, href: str):
        return requests_exists(href, self.headers)

    def get_rasterio_session(self):
        # Might not work
        return {}

    def pull(self, href: str, dst: str):
        super().pull(href, dst)
        requests_get(href, dst, self.headers)

    def is_file(self, href: str):
        return self.exists(href)

    def is_dir(self, href: str):
        return False

    def get_file_size(self, href: str):
        r = requests_head(href, self.headers)
        return r.headers.get("Content-Length")

    def listdir(self, href: str):
        raise NotImplementedError(f"It is not possible to list the content of a directory with {self.type} protocol")

    def get_last_modification_time(self, href: str):
        r = requests_head(href, self.headers)
        return time.mktime(time.strptime(r.headers.get("Last-Modified"), "%a, %d %b %Y %H:%M:%S %Z"))

    def get_creation_time(self, href: str):
        # There is no difference in HTTP(S) between last update and creation date
        return self.get_last_modification_time(href)

    def makedir(self, href: str, strict=False):
        if strict:
            raise NotImplementedError(f"It is not possible to create the folder with {self.type} protocol")

    def clean(self, href: str):
        raise NotImplementedError(f"It is not possible to delete a file with {self.type} protocol")
