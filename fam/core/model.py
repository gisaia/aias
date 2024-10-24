from datetime import datetime

from pydantic import BaseModel


class PathRequest(BaseModel):
    path: str = ""
    size: int = 10


class File(BaseModel):
    name: str = ""
    path: str = ""
    is_dir: bool = False
    last_modification_date: datetime
    creation_date: datetime


class Archive(File):
    id: str = ""
    driver_name: str = ""
