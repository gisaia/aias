from pydantic import Extra, Field, field_validator

from airs.core.models.model import Band, ChunkingStrategy, ItemGroup
from extensions.aproc.proc.processes.process_model import InputProcess

COMPOSITION_DESCRIPTION = "The composition is an array of item groups " + \
                          "that each represent a temporal slice of " + \
                          "the datacube. The whole composition contains " + \
                          "all the data requested across space and time."
BANDS_DESCRIPTION = "The list of bands to extract. " + \
                    "The bands will be the variables of the datacube."
ROI_DESCRIPTION = "The Region Of Interest to extract. " + \
                  "Accepted formats are BBOX or WKT POLYGON."
RESOLUTION_DESCRIPTION = "The requested spatial resolution in meters. " + \
                         "By default uses the best resolution of the " + \
                         "given products."
PROJECTION_DESCRIPTION = "The targeted projection. Default: 4326."
CHUNKING_DESCRIPTION = "Defines how the datacube must be chunked, " + \
                       "to facilitate further data processing. Three " + \
                       "strategies are available: 'carrot', 'potato' and " + \
                       "'spinach'. 'carrot' creates deep temporal slices, " + \
                       "while 'spinach' chunks data on wide geographical " + \
                       "areas. 'Potato' is a balanced option, creating " + \
                       "an equally sized chunk."
DESCRIPTION_DESCRIPTION = "The datacube's description."
THEMATICS_DESCRIPTION = "Thematics / keywords of the datacube."
OVERVIEW_DESCRIPTION = "Whether to build an overview of the resulting cube."


class InputDC3BuildProcess(InputProcess, extra=Extra.allow):
    target_collection: str = Field(title="Collection name", description="Name of the collection where the item will be registered")
    target_catalog: str = Field(title="Catalog name", description="Name of the catalog, within the collection, where the item will be registered")
    composition: list[ItemGroup] = Field(description=COMPOSITION_DESCRIPTION, min_length=1)
    overview: bool = Field(default=False, description=OVERVIEW_DESCRIPTION)
    bands: list[Band] = Field(description=BANDS_DESCRIPTION, min_length=1)
    roi: str = Field(description=ROI_DESCRIPTION)
    target_resolution: int = Field(default=10,
                                   description=RESOLUTION_DESCRIPTION, gt=0)
    target_projection: int = Field(default=4326,
                                   description=PROJECTION_DESCRIPTION)
    chunking_strategy: ChunkingStrategy = Field(default=ChunkingStrategy.POTATO, description=CHUNKING_DESCRIPTION)
    title: str = Field(default=None, description="The datacube's title")
    description: str = Field(default=None, description=DESCRIPTION_DESCRIPTION)
    keywords: list[str] = Field(default=[], description=THEMATICS_DESCRIPTION)

    @field_validator('bands', mode='after')
    @classmethod
    def check_overview_params(cls, value: list[Band]) -> list[Band]:
        rgb = {}
        for band in value:
            if band.dc3__rgb is not None:
                if band.dc3__rgb in rgb:
                    raise ValueError(f"Band for {band.dc3__rgb.value} has been defined multiple times: {rgb[band.dc3__rgb]} & {band.name}")
                rgb[band.dc3__rgb] = band.name

        if len(rgb) != 3 and len(rgb) != 0:
            raise ValueError("The request should either have no bands with 'dc3__rgb' specified, or each color should be assigned exactly once.")

        return value
