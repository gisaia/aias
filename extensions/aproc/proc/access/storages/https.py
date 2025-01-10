from typing import Literal
from urllib.parse import urlparse

from pydantic import Field

from extensions.aproc.proc.access.storages.abstract import AbstractStorage
from extensions.aproc.proc.access.storages.utils import requests_exists, requests_get


class HttpsStorage(AbstractStorage):
    type: Literal["https"] = "https"
    headers: dict[str, str] = Field(default={})
    domain: str
    force_download: bool = Field(default=False)

    def get_storage_parameters(self):
        return {"headers": self.headers}

    def supports(self, href: str):
        scheme = urlparse(href).scheme
        netloc = urlparse(href).netloc

        return scheme == "https" and netloc == self.domain

    def exists(self, href: str):
        return requests_exists(href, self.headers)

    def get_rasterio_session(self):
        # Might not work
        return None

    def pull(self, href: str, dst: str, is_dst_dir: bool):
        super().pull(href, dst, is_dst_dir)
        requests_get(href, dst, is_dst_dir, self.headers)

    def is_file(self, href: str):
        return self.exists(href)

    def is_dir(self, href: str):
        return False
