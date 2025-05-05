from pydantic import BaseModel, Field


class InputProcess(BaseModel):
    include_drivers: list[str] = Field(default=[], title="List of drivers to include. If none, all are included")
    exclude_drivers: list[str] = Field(default=[], title="List of drivers to exclude. If none, none are excluded")
