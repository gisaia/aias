from pydantic import BaseModel

from aias_common.access.file import File


class PathRequest(BaseModel):
    path: str = ""
    size: int = 10


class Archive(File):
    id: str = ""
    driver_name: str = ""
