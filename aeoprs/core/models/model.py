from datetime import datetime as Datetime
from enum import Enum
from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar,
                    Union, cast)

from pydantic import BaseModel, Extra, Field
from pydantic.fields import FieldInfo

class ProcessingLevel(Enum):
    RAW="RAW"
    L1="L1"
    L2="L2"
    L3="L3"
    L4="L4"


class Role(Enum):
    arlas_eo_item="arlas_eo_item"
    thumbnail="thumbnail"
    overview="overview"
    data="data"
    metadata="metadata"
    cog="cog"
    zarr="zarr"
    datacube="datacube"
    visual="visual"
    date="date"
    graphic="graphic"
    data_mask="data-mask"
    snow_ice="snow-ice"
    land_water="land-water"
    water_mask="water-mask"
    iso_19115="iso-19115"
    reflectance="reflectance"
    temperature="temperature"
    saturation="saturation"
    cloud="cloud"
    cloud_shadow="cloud-shadow"
    incidence_angle="incidence-angle"
    azimuth="azimuth"
    sun_azimuth="sun-azimuth"
    sun_elevation="sun-elevation"
    terrain_shadow="terrain-shadow"
    terrain_occlusion="terrain-occlusion"
    terrain_illumination="terrain-illumination"
    local_incidence_angle="local-incidence-angle"
    noise_power="noise-power"
    amplitude="amplitude"
    magnitude="magnitude"
    sigma0="sigma0"
    beta0="beta0"
    gamma0="gamma0"
    date_offset="date-offset"
    covmat="covmat"
    prd="prd"

class CommonBandName(Enum):
    coastal="coastal"
    blue="blue"
    green="green"
    red="red"
    yellow="yellow"
    pan="pan"
    rededge="rededge"
    nir="nir"
    nir08="nir08"
    nir09="nir09"
    cirrus="cirrus"
    swir16="swir16"
    swir22="swir22"
    lwir="lwir"
    lwir11="lwir11"
    lwir12="lwir12"
    
class VariableType(Enum):
    data="data"
    auxiliary="auxiliary"

class DimensionType(Enum):
    spatial="spatial"
    temporal="temporal"
    geometry="geometry"
    
class RasterType(BaseModel):
    source:str
    format:str

class Raster(BaseModel):
    type:RasterType
    path:str
    id:str

class Axis(Enum):
    x="x"
    y="y"
    z="z"
    t="t"

class Indicators(BaseModel):
    time_compacity                : float           | None = Field(default=None, title="Indicates whether the temporal extend of the temporal slices (groups) are compact or not compared to the cube temporal extend. Computed as follow: 1-range(group rasters) / range(cube rasters).")
    spatial_coverage              : float           | None = Field(default=None, title="Indicates the proportion of the region of interest that is covered by the input rasters. Computed as follow: area(intersection(union(rasters),roi)) / area(roi))")
    group_lightness               : float           | None = Field(default=None, title="Indicates the proportion of non overlapping regions between the different input rasters. Computed as follow: area(intersection(union(rasters),roi)) / sum(area(intersection(raster, roi)))")
    time_regularity               : float           | None = Field(default=None, title="Indicates the regularity of the extends between the temporal slices (groups). Computed as follow: 1-std(inter group temporal gaps)/avg(inter group temporal gaps)")

class Group(BaseModel):
    timestamp                     : int             | None = Field(default=None, title="The timestamp of this temporal group.")
    rasters                       :List[Raster]     | None = Field(default=None, title="The rasters belonging to this temporal group.")
    quality_indicators            :Indicators       | None = Field(default=None, title="Set of indicators for estimating the quality of the datacube group. The indicators are group based.")

class Band(BaseModel):
    name                          :str                     = Field(title="The name of the band (e.g., B01, B8, band2, red).", max_length=300)
    common_name                   :str              | None = Field(default=None, title="The name commonly used to refer to the band to make it easier to search for bands across instruments. See the list of accepted common names.")
    description                   :str              | None = Field(default=None, title="Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.", max_length=300)
    center_wavelength             :float            | None = Field(default=None, title="The center wavelength of the band, in micrometers (μm).")
    full_width_half_max           :float            | None = Field(default=None, title="Full width at half maximum (FWHM). The width of the band, as measured at half the maximum transmission, in micrometers (μm).")
    solar_illumination            :float            | None = Field(default=None, title="The solar illumination of the band, as measured at half the maximum transmission, in W/m2/micrometers.")
    quality_indicators            :Indicators       | None = Field(default=None, title="Set of indicators for estimating the quality of the datacube variable (band).")

class Asset(BaseModel):
    name                          :str              | None = Field(default=None, title="Asset's name. But be the same as the key in the `assets` dictionary.", max_length=300)
    href                          :str                     = Field(default=None, title="Absolute link to the asset object.")
    storage__requester_pays       :bool             | None = Field(default=None, title="Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets", alias="storage:requester_pays")
    storage__tier                 :str              | None = Field(default=None, title="Cloud Provider Storage Tiers (Standard, Glacier, etc.)", alias="storage:tier")
    storage__platform             :str              | None = Field(default=None, title="PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)", alias="storage:platform")
    storage__region               :str              | None = Field(default=None, title="The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)", alias="storage:region")
    aeo__managed                  :bool              = Field(default=True, title="Whether the asset is managed by AEOPRS or not.", alias="aeo:managed")
    aeo__object_store_bucket      :str              | None = Field(default=None, title="Object store bucket for the asset object.", alias="aeo:object_store_bucket")
    aeo__object_store_key         :str              | None = Field(default=None, title="Object store key of the asset object.", alias="aeo:object_store_key")
    title                         :str              | None = Field(default=None, title="Optional displayed title for clients and users.", max_length=300)
    description                   :str              | None = Field(default=None, title="A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29 syntax MAY be used for rich text representation.", max_length=300)
    type                          :str              | None = Field(default=None, title="Optional description of the media type. Registered Media Types are preferred. See MediaType for common media types.", max_length=300)
    roles                         :List[str]        | None = Field(default=None, title="Optional, Semantic roles (i.e. thumbnail, overview, data, metadata) of the asset.", max_length=300)
    extra_fields                  :Dict[str, Any]   | None = Field(default=None, title="Optional, additional fields for this asset. This is used by extensions as a way to serialize and deserialize properties on asset object JSON.")
    gsd                           :float            | None = Field(default=None, title="Ground Sampling Distance (resolution) of the asset")
    eo__bands                     :List[Band]       | None = Field(default=None, title="An array of available bands where each object is a Band Object. If given, requires at least one band.", alias="eo:bands")
    sar__instrument_mode          :str              | None = Field(default=None, title="The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for \"Wave mode\" of Sentinel-1 and Envisat ASAR satellites.", alias="sar:instrument_mode")
    sar__frequency_band           :str              | None = Field(default=None, title="The common name for the frequency band to make it easier to search for bands across instruments. See section \"Common Frequency Band Names\" for a list of accepted names.", alias="sar:frequency_band")
    sar__center_frequency         :float            | None = Field(default=None, title="The center frequency of the instrument, in gigahertz (GHz).", alias="sar:center_frequency")
    sar__polarizations            :str              | None = Field(default=None, title="Any combination of polarizations.", alias="sar:polarizations")
    sar__product_type             :str              | None = Field(default=None, title="The product type, for example SSC, MGD, or SGC", alias="sar:product_type")
    sar__resolution_range         :float            | None = Field(default=None, title="The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).", alias="sar:resolution_range")
    sar__resolution_azimuth       :float            | None = Field(default=None, title="The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).", alias="sar:resolution_azimuth")
    sar__pixel_spacing_range      :float            | None = Field(default=None, title="The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.", alias="sar:pixel_spacing_range")
    sar__pixel_spacing_azimuth    :float            | None = Field(default=None, title="The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.", alias="sar:pixel_spacing_azimuth")
    sar__looks_range              :float            | None = Field(default=None, title="Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.", alias="sar:looks_range")
    sar__looks_azimuth            :float            | None = Field(default=None, title="Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.", alias="sar:looks_azimuth")
    sar__looks_equivalent_number  :float            | None = Field(default=None, title="The equivalent number of looks (ENL).", alias="sar:looks_equivalent_number")
    sar__observation_direction    :str              | None = Field(default=None, title="Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.", alias="sar:observation_direction")
    proj__epsg                    :int              | None = Field(default=None, title="EPSG code of the datasource.", alias="proj:epsg")
    proj__wkt2                    :str              | None = Field(default=None, title="PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.", alias="proj:wkt2")
    proj__geometry                :Any              | None = Field(default=None, title="Defines the footprint of this Item.", alias="proj:geometry")
    proj__bbox                    :List[float]      | None = Field(default=None, title="Bounding box of the Item in the asset CRS in 2 or 3 dimensions.", alias="proj:bbox")
    proj__centroid                :Any              | None = Field(default=None, title="Coordinates representing the centroid of the Item (in lat/long).", alias="proj:centroid")
    proj__shape                   :List[float]      | None = Field(default=None, title="Number of pixels in Y and X directions for the default grid.", alias="proj:shape")
    proj__transform               :List[float]      | None = Field(default=None, title="The affine transformation coefficients for the default grid.", alias="proj:transform")

class Properties(BaseModel, extra=Extra.allow):
    datetime                      :Datetime         | None = Field(default=None, title="datetime associated with this item. If None, a start_datetime and end_datetime must be supplied.")
    start_datetime                :Datetime         | None = Field(default=None, title="Optional start datetime, part of common metadata. This value will override any start_datetime key in properties.")
    end_datetime                  :Datetime         | None = Field(default=None, title="Optional end datetime, part of common metadata. This value will override any end_datetime key in properties.")
    programme                     :str              | None = Field(default=None, title="Name of the programme")
    constellation                 :str              | None = Field(default=None, title="Name of the constellation")
    instrument                    :str              | None = Field(default=None, title="Name of the instrument")
    sensor                        :str              | None = Field(default=None, title="Name of the sensor")
    sensor_type                   :str              | None = Field(default=None, title="Type of sensor")
    gsd                           :float            | None = Field(default=None, title="Ground Sampling Distance (resolution)")
    data_type                     :str              | None = Field(default=None, title="Type of data")
    data_coverage                 :float            | None = Field(default=None, title="Estimate of data cover")
    water_coverage                :float            | None = Field(default=None, title="Estimate of water cover")
    locations                     :List[str]        | None = Field(default=None, title="List of locations covered by the item")
    create_datetime               :int              | None = Field(default=None, title="Date of item creation in the catalog, managed by the ARLAS EO Registration Service")
    update_datetime               :int              | None = Field(default=None, title="Update date of the item in the catalog, managed by the ARLAS EO Registration Service")
    view__off_nadir               :float            | None = Field(default=None, title="The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).", alias="view:off_nadir")
    view__incidence_angle         :float            | None = Field(default=None, title="The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight back to the satellite at the scene center. Measured in degrees (0-90).", alias="view:incidence_angle")
    view__azimuth                 :float            | None = Field(default=None, title="Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform) between the scene center and true north. Measured clockwise from north in degrees (0-360).", alias="view:azimuth")
    view__sun_azimuth             :float            | None = Field(default=None, title="Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun. Measured clockwise in degrees (0-360).", alias="sview:un_azimuth")
    view__sun_elevation           :float            | None = Field(default=None, title="Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° means the data was captured during nautical twilight.", alias="view:sun_elevation")
    storage__requester_pays       :bool             | None = Field(default=None, title="Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets", alias="storage:requester_pays")
    storage__tier                 :str              | None = Field(default=None, title="Cloud Provider Storage Tiers (Standard, Glacier, etc.)", alias="storage:tier")
    storage__platform             :str              | None = Field(default=None, title="PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)", alias="storage:platform")
    storage__region               :str              | None = Field(default=None, title="The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)", alias="storage:region")
    eo__cloud_cover               :float            | None = Field(default=None, title="Estimate of cloud cover.", alias="eo:cloud_cover")
    eo__snow_cover                :float            | None = Field(default=None, title="Estimate of snow and ice cover.", alias="eo:snow_cover")
    eo__bands                     :List[Band]       | None = Field(default=None, title="An array of available bands where each object is a Band Object. If given, requires at least one band.", alias="eo:bands")
    processing__expression        :str              | None = Field(default=None, title="An expression or processing chain that describes how the data has been processed. Alternatively, you can also link to a processing chain with the relation type processing-expression (see below).", alias="processing:expression")
    processing__lineage           :str              | None = Field(default=None, title="Lineage Information provided as free text information about the how observations were processed or models that were used to create the resource being described NASA ISO.", alias="processing:lineage")
    processing__level             :str              | None = Field(default=None, title="The name commonly used to refer to the processing level to make it easier to search for product level across collections or items. The short name must be used (only L, not Level).", alias="processing:level")
    processing__facility          :str              | None = Field(default=None, title="The name of the facility that produced the data. For example, Copernicus S1 Core Ground Segment - DPA for product of Sentinel-1 satellites.", alias="processing:facility")
    processing__software          :Dict[str,str]    | None = Field(default=None, title="A dictionary with name/version for key/value describing one or more softwares that produced the data.", alias="processing:software")
    dc3__quality_indicators       :Indicators       | None = Field(default=None, title="Set of indicators for estimating the quality of the datacube based on the composition. The indicators are group based. A cube indicator is the product of its corresponding group indicator.", alias="dc3:quality_indicators")
    dc3__composition              :List[Group]      | None = Field(default=None, title="List of raster groups used for elaborating the cube temporal slices.", alias="dc3:composition")
    dc3__number_of_chunks         :int              | None = Field(default=None, title="Number of chunks (if zarr or similar partitioned format) within the cube.", alias="dc3:number_of_chunks")
    dc3__chunk_weight             :int              | None = Field(default=None, title="Weight of a chunk (number of bytes).", alias="dc3:chunk_weight")
    dc3__fill_ratio               :float            | None = Field(default=None, title="1: the cube is full, 0 the cube is empty, in between the cube is partially filled.", alias="dc3:fill_ratio")
    cube__dimensions              :Dict[str, DimensionType] | None = Field(default=None, title="Uniquely named dimensions of the datacube.", alias="cube:dimensions")
    cube__variables               :Dict[str, VariableType] | None = Field(default=None, title="Uniquely named variables of the datacube.", alias="cube:variables")
    sar__instrument_mode          :str              | None = Field(default=None,title="The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for \"Wave mode\" of Sentinel-1 and Envisat ASAR satellites.", alias="sar:instrument_mode")
    sar__frequency_band           :str              | None = Field(default=None,title="The common name for the frequency band to make it easier to search for bands across instruments. See section \"Common Frequency Band Names\" for a list of accepted names.", alias="sar:frequency_band")
    sar__center_frequency         :float            | None = Field(default=None, title="The center frequency of the instrument, in gigahertz (GHz).", alias="sar:center_frequency")
    sar__polarizations            :str              | None = Field(default=None,title="Any combination of polarizations.", alias="sar:polarizations")
    sar__product_type             :str              | None = Field(default=None,title="The product type, for example SSC, MGD, or SGC", alias="sar:product_type")
    sar__resolution_range         :float            | None = Field(default=None, title="The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).", alias="sar:resolution_range")
    sar__resolution_azimuth       :float            | None = Field(default=None, title="The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).", alias="sar:resolution_azimuth")
    sar__pixel_spacing_range      :float            | None = Field(default=None, title="The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.", alias="sar:pixel_spacing_range")
    sar__pixel_spacing_azimuth    :float            | None = Field(default=None, title="The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.", alias="sar:pixel_spacing_azimuth")
    sar__looks_range              :float            | None = Field(default=None, title="Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.", alias="sar:looks_range")
    sar__looks_azimuth            :float            | None = Field(default=None, title="Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.", alias="sar:looks_azimuth")
    sar__looks_equivalent_number  :float            | None = Field(default=None, title="The equivalent number of looks (ENL).", alias="sar:looks_equivalent_number")
    sar__observation_direction    :str              | None = Field(default=None, title="Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.", alias="sar:observation_direction")
    proj__epsg                    :int              | None = Field(default=None, title="EPSG code of the datasource.", alias="proj:epsg")
    proj__wkt2                    :str              | None = Field(default=None, title="PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.", alias="proj:wkt2")
    proj__geometry                :Any              | None = Field(default=None, title="Defines the footprint of this Item.", alias="proj:geometry")
    proj__bbox                    :List[float]      | None = Field(default=None, title="Bounding box of the Item in the asset CRS in 2 or 3 dimensions.", alias="proj:bbox")
    proj__centroid                :Any              | None = Field(default=None, title="Coordinates representing the centroid of the Item (in lat/long).", alias="proj:centroid")
    proj__shape                   :List[float]      | None = Field(default=None, title="Number of pixels in Y and X directions for the default grid.", alias="proj:shape")
    proj__transform               :List[float]      | None = Field(default=None, title="The affine transformation coefficients for the default grid.", alias="proj:transform")
    generated__has_overview       :bool             | None = Field(default=False, title="Whether the item has an overview or not.", alias="generated:has_overview")
    generated__has_thumbnail      :bool             | None = Field(default=False, title="Whether the item has a thumbnail or not.", alias="generated:has_thumbnail")
    generated__has_metadata       :bool             | None = Field(default=False, title="Whether the item has a metadata file or not.", alias="generated:has_metadata")
    generated__has_data           :bool             | None = Field(default=False, title="Whether the item has a data file or not.", alias="generated:has_data")
    generated__has_cog            :bool             | None = Field(default=False, title="Whether the item has a cog or not.", alias="generated:has_cog")
    generated__has_zarr           :bool             | None = Field(default=False, title="Whether the item has a zarr or not.", alias="generated:has_zarr")
    generated__date_keywords      :List[str]        | None = Field(default=None, title="A list of keywords indicating clues on the date", alias="generated:date_keywords")
    generated__day_of_week        :int              | None = Field(default=None, title="Day of week.", alias="generated:day_of_week")
    generated__day_of_year        :int              | None = Field(default=None, title="Day of year.", alias="generated:day_of_year")
    generated__hour_of_day        :int              | None = Field(default=None, title="Hour of day.", alias="generated:hour_of_day")
    generated__minute_of_day      :int              | None = Field(default=None, title="Minute of day.", alias="generated:minute_of_day")
    generated__month              :int              | None = Field(default=None, title="Month", alias="generated:month")
    generated__year               :int              | None = Field(default=None, title="Year", alias="generated:year")
    generated__season             :str              | None = Field(default=None, title="Season", alias="generated:season")
    generated__tltrbrbl           :List[List[float]]| None = Field(default=None, title="The coordinates of the top left, top right, bottom right, bottom left corners of the item.", alias="generated:tltrbrbl")
    generated__band_common_names  :List[str]        | None = Field(default=None, title="List of the band common names.", alias="generated:band_common_names")
    generated__band_names         :List[str]        | None = Field(default=None, title="List of the band names.", alias="generated:band_names")
    generated__geohash2           :str              | None = Field(default=None, title="Geohash on the first two characters.", alias="generated:geohash2")
    generated__geohash3           :str              | None = Field(default=None, title="Geohash on the first three characters.", alias="generated:geohash3")
    generated__geohash4           :str              | None = Field(default=None, title="Geohash on the first four characters.", alias="generated:geohash4")
    generated__geohash5           :str              | None = Field(default=None, title="Geohash on the first five characters.", alias="generated:geohash5")

class Item(BaseModel):
    collection                    :str              | None = Field(default=None, title="Name of the collection the item belongs to.", max_length=300)
    catalog                       :str              | None = Field(default=None, title="Name of the catalog the item belongs to.", max_length=300)
    id                            :str              | None  = Field(default=None, title="Provider identifier. Must be unique within the STAC.", max_length=300)
    geometry                      :Dict[str, Any]   | None = Field(default=None, title="Defines the full footprint of the asset represented by this item, formatted according to `RFC 7946, section 3.1 (GeoJSON) <https://tools.ietf.org/html/rfc7946>`_")
    bbox                          :List[float]      | None = Field(default=None, title="Bounding Box of the asset represented by this item using either 2D or 3D geometries. The length of the array must be 2*n where n is the number of dimensions. Could also be None in the case of a null geometry.")
    centroid                      :List[float]      | None = Field(default=None, title="Coordinates (lat/lon) of the geometry's centroid.")
    assets                        :Dict[str, Asset] | None = Field(default=None, title="A dictionary mapping string keys to Asset objects. All Asset values in the dictionary will have their owner attribute set to the created Item.")
    properties                    :Properties       | None = Field(default=None, title="Item properties")
