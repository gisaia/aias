from typing import Literal

from extensions.aproc.proc.access.storages.http import HttpStorage


class HttpsStorage(HttpStorage):
    type: Literal["https"] = "https"
