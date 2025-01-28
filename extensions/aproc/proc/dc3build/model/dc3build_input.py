from pydantic import Field

from extensions.aproc.proc.processes.process_model import InputProcess

from .enums import ChunkingStrategy as CStrat
from .band import Band
from .item_group import ItemGroup

COMPOSITION_DESCRIPTION = "The composition is an array of item groups " + \
                          "that each represent a temporal slice of " + \
                          "the datacube. The whole composition contains " + \
                          "all the data requested across space and time."
BANDS_DESCRIPTION = "The list of bands to extract. " + \
                    "The bands will be the variables of the datacube."
ALIASES_DESCRIPTION = "The list of aliases for this datacube. " + \
                      "They will allow to quickly reference the " + \
                      "product bands used to compute the datacube bands."
ROI_DESCRIPTION = "The Region Of Interest to extract. " + \
                  "Accepted formats are BBOX or WKT POLYGON."
RESOLUTION_DESCRIPTION = "The requested spatial resolution in meters. " + \
                         "By default uses the best resolution of the " + \
                         "given products."
PROJECTION_DESCRIPTION = "The targeted projection. Default: 'EPSG:4326'."
CHUNKING_DESCRIPTION = "Defines how the datacube must be chunked, " + \
                       "to facilitate further data processing. Three " + \
                       "strategies are available: 'carrot', 'potato' and " + \
                       "'spinach'. 'carrot' creates deep temporal slices, " + \
                       "while 'spinach' chunks data on wide geographical " + \
                       "areas. 'Potato' is a balanced option, creating " + \
                       "an equally sized chunk."
DESCRIPTION_DESCRIPTION = "The datacube's description."
THEMATICS_DESCRIPTION = "Thematics / keywords of the datacube."
EXTRA_PARAMS_DESCRIPTION = "List of key/value driver specific parameters."
TARGET_COLLECTION = "The name of the collection where the resulting cube should be referenced."
TARGET_CATALOG = "The name of the catalog for the resulting cube."
OVERVIEW_DESCRIPTION = "Build an overview of the resulting cube."


class InputDC3BuildProcess(InputProcess):
    composition: list[ItemGroup] = Field(description=COMPOSITION_DESCRIPTION)
    overview: bool = Field(default=False, description=COMPOSITION_DESCRIPTION)
    bands: list[Band] = Field(description=BANDS_DESCRIPTION)
    extra_params: dict[str, str] = Field(description=EXTRA_PARAMS_DESCRIPTION)
    roi: str = Field(description=ROI_DESCRIPTION)
    target_resolution: int = Field(default=10,
                                   description=RESOLUTION_DESCRIPTION, gt=0)
    target_projection: str = Field(default="EPSG:4326",
                                   description=PROJECTION_DESCRIPTION)
    chunking_strategy: CStrat = Field(default=CStrat.POTATO,
                                      description=CHUNKING_DESCRIPTION)
    description: str | None = Field(description=DESCRIPTION_DESCRIPTION)
    keywords: list[str] | None = Field(description=THEMATICS_DESCRIPTION)
