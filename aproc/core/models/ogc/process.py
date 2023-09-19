from pydantic import BaseModel, Field

from aproc.core.models.ogc.description import (DescriptionType,
                                               InputDescription,
                                               OutputDescription)
from aproc.core.models.ogc.enums import JobControlOptions, TransmissionMode
from aproc.core.models.ogc.link import Link


class ProcessSummary(DescriptionType):
    id: str
    version: str
    jobControlOptions: list[JobControlOptions] | None = Field(default=None)
    outputTransmission: list[TransmissionMode] | None = Field(default=None)
    links: list[Link] | None = Field(default=None)


class ProcessList(BaseModel):
    processes: list[ProcessSummary]
    links: list[Link] | None = Field(default=None)


class ProcessDescription(ProcessSummary):
    inputs: dict[str, InputDescription] | None = Field(default=None)
    outputs: dict[str, OutputDescription] | None = Field(default=None)
