from pydantic import BaseModel
from datetime import datetime

class File(BaseModel):
    name: str = ""
    path: str = ""
    is_dir: bool = False
    last_modification_date: datetime
    creation_date: datetime