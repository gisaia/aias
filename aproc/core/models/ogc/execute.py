
from typing import Any

from pydantic import AnyUrl, BaseModel, Field, RootModel

from aproc.core.models.ogc.enums import Crs, Response, TransmissionMode
from aproc.core.models.ogc.link import Link


class Format(BaseModel):
    mediaType: str | None = Field(default=None)
    encoding: str | None = Field(default=None)
    schema_: str | dict[str, Any] | None = Field(default=None, alias="schema")


class OutputFormat(BaseModel):
    format: Format | None = Field(default=None)
    transmissionMode: TransmissionMode | None = Field(default=None)


class BinaryInputValue(RootModel):
    root: str


class Bbox(BaseModel):
    bbox: list[float]
    crs: Crs | None \
        = Field(default=Crs.http___www_opengis_net_def_crs_OGC_1_3_CRS84)


class InputValueNoObject(RootModel):
    root: str | float | int | bool | list[Any] | BinaryInputValue | Bbox


class InputValue(RootModel):
    root: dict[str, Any] | InputValueNoObject


class QualifiedInputValue(Format):
    value: InputValue


class InlineOrRefData(RootModel):
    root: InputValueNoObject | QualifiedInputValue | Link


class Subscriber(BaseModel):
    successUri: AnyUrl | None = Field(default=None)
    inProgressUri: AnyUrl | None = Field(default=None)
    failedUri: AnyUrl | None = Field(default=None)


class Execute(BaseModel):
    inputs: dict[str, InlineOrRefData | list[InlineOrRefData]] | None \
        = Field(default=None)
    outputs: dict[str, OutputFormat] | None = Field(default=None)
    response: Response | None = Field(default=Response.raw)
    subscriber: Subscriber | None = Field(default=None)
