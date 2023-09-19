from datetime import datetime

from pydantic import BaseModel, Extra, Field

from aproc.core.models.ogc.enums import JobType, StatusCode
from aproc.core.models.ogc.link import Link


class StatusInfo(BaseModel):
    class Config:
        extra = Extra.allow

    processID: str | None = Field(default=None)
    type: JobType
    jobID: str
    status: StatusCode
    message: str | None = Field(default=None)
    created: datetime | None = Field(default=None)
    started: datetime | None = Field(default=None)
    finished: datetime | None = Field(default=None)
    updated: datetime | None = Field(default=None)
    progress: int | None = Field(default=None, ge=0, le=100)
    links: list[Link] | None = Field(default=None)
