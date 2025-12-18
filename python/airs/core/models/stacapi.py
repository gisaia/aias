from datetime import datetime as Datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Link(BaseModel):
    href: str
    rel: str | None = Field(default=None)
    type: str | None = Field(default=None)
    hreflang: str | None = Field(default=None)
    title: str | None = Field(default=None)


class BBOX(BaseModel):
    bbox: List[List[float]] = Field([[-180, -90, 180, 90]], description="Bounding boxes as [minX, minY, maxX, maxY]")


class Extent(BaseModel):
    spatial: BBOX | None = Field(default=None, description="Spatial extent of the collection")
    temporal: list[list[Datetime]] = Field(default=[], description="Temporal extent of the collection")


class CollectionDescription(BaseModel):
    id: str
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    extent: Dict[str, Any] | None = Field(default=None)
    crs: List[str] | None = Field(default=None)
    links: list[Link] = Field([], description="Links related to the collections")


class CollectionDescriptionListResponse(BaseModel):
    collections: list[CollectionDescription] = Field(default_factory=list)
    links: list[Link] = Field([], description="Links related to the collections")
    numberMatched: int = Field(default=0)
    numberReturned: int = Field(default=0)
