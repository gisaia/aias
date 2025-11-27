from pydantic import BaseModel, Field
from aproc.core.processes.process import InputProcess as _InputProcess


class InputProcess(_InputProcess):
    include_drivers: list[str] = Field(default=[], title="List of drivers to include. If none, all are included")
    exclude_drivers: list[str] = Field(default=[], title="List of drivers to exclude. If none, none are excluded")
