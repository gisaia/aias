from pydantic import BaseModel, Field


RASTERS_DESCRIPTION = "The list of items in this group. " + \
                      "They represent a temporal slice of the datacube."
TIMESTAMP_DESCRIPTION = "The timestamp of this temporal slice of the datacube."


class ItemReference(BaseModel):
    collection: str = Field(description="Name of the collection containing the item")
    id: str = Field(description="Item's identifer")
    alias: str = Field(description="Product alias (e.g. s2_l2)")


class ItemGroup(BaseModel):
    rasters: list[ItemReference] = Field(description=RASTERS_DESCRIPTION)
    timestamp: int = Field(description=TIMESTAMP_DESCRIPTION)
