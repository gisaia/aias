
from pydantic import BaseModel, Extra, Field

from aproc.core.models.ogc.enums import JobType, StatusCode
from aproc.core.models.ogc.link import Link


class StatusInfo(BaseModel):
    class Config:
        extra = Extra.allow

    processID: str | None = Field(default=None)
    type: JobType | None = Field(default=None)
    jobID: str | None = Field(default=None)
    status: StatusCode | None = Field(default=None)
    message: str | None = Field(default=None)
    created: int | None = Field(default=None)
    started: int | None = Field(default=None)
    finished: int | None = Field(default=None)
    updated: int | None = Field(default=None)
    progress: int | None = Field(default=None, ge=0, le=100)
    links: list[Link] | None = Field(default=None)

    # This field is specific to airs : it stores the resource id that is the input of a process
    resourceID: str | None = Field(default=None)


class StatusInfoList(BaseModel):
    class Config:
        extra = Extra.allow

    status_list: list[StatusInfo] | None = Field(default=None)
    total: int | None = Field(default=None)
