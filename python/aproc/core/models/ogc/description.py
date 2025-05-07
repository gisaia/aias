from typing import Any

from pydantic import BaseModel, Field

from aproc.core.models.ogc.enums import MaxOccur
from aproc.core.models.ogc.schema import Reference, SchemaItem


class Metadata(BaseModel):
    title: str | None = Field(default=None)
    role: str | None = Field(default=None)
    href: str | None = Field(default=None)


class AdditionalParameter(BaseModel):
    name: str
    value: list[str | float | int | list[Any] | dict[str, Any]]


class AdditionalParameters(Metadata):
    parameters: list[AdditionalParameter] | None = Field(default=None)


class DescriptionType(BaseModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    keywords: list[str] | None = Field(default=None)
    metadata: list[Metadata] | None = Field(default=None)
    additionalParameters: AdditionalParameters | None = Field(default=None)


class InputDescription(DescriptionType):
    class Config:
        populate_by_name = True

    minOccurs: int | None = 1
    maxOccurs: int | MaxOccur | None = None
    schema_: Reference | SchemaItem = Field(alias="schema")


class OutputDescription(DescriptionType):
    class Config:
        populate_by_name = True

    schema_: Reference | SchemaItem = Field(alias="schema")
