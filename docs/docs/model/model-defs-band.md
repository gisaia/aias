# Band Schema

```txt
airs_model#/$defs/Properties/properties/eo__bands/anyOf/0/items
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                      |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :-------------------------------------------------------------- |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json\*](model.schema.json "open original schema") |

## items Type

`object` ([Band](model-defs-band.md))

# items Properties

| Property                                       | Type     | Required | Nullable       | Defined by                                                                                                                                                                                                                       |
| :--------------------------------------------- | :------- | :------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [name](#name)                                  | `string` | Required | cannot be null | [Item](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md "airs_model#/$defs/Band/properties/name")                                                                                                          |
| [common\_name](#common_name)                   | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md "airs_model#/$defs/Band/properties/common_name") |
| [description](#description)                    | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "airs_model#/$defs/Band/properties/description")                                       |
| [center\_wavelength](#center_wavelength)       | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md "airs_model#/$defs/Band/properties/center_wavelength")                                                                                  |
| [full\_width\_half\_max](#full_width_half_max) | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md "airs_model#/$defs/Band/properties/full_width_half_max")               |
| [solar\_illumination](#solar_illumination)     | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md "airs_model#/$defs/Band/properties/solar_illumination")                                   |
| [quality\_indicators](#quality_indicators)     | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md "airs_model#/$defs/Band/properties/quality_indicators")                                                          |
| Additional Properties                          | Any      | Optional | can be null    |                                                                                                                                                                                                                                  |

## name



`name`

* is required

* Type: `string` ([The name of the band (e.g., B01, B8, band2, red).](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md "airs_model#/$defs/Band/properties/name")

### name Type

`string` ([The name of the band (e.g., B01, B8, band2, red).](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md))

### name Constraints

**maximum length**: the maximum number of characters for this string is: `300`

## common\_name



`common_name`

* is optional

* Type: merged type ([The name commonly used to refer to the band to make it easier to search for bands across instruments. See the list of accepted common names.](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md "airs_model#/$defs/Band/properties/common_name")

### common\_name Type

merged type ([The name commonly used to refer to the band to make it easier to search for bands across instruments. See the list of accepted common names.](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md))

any of

* [Untitled string in Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names-anyof-1.md "check type definition")

## description



`description`

* is optional

* Type: merged type ([Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "airs_model#/$defs/Band/properties/description")

### description Type

merged type ([Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

any of

* [Untitled string in Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-1.md "check type definition")

## center\_wavelength



`center_wavelength`

* is optional

* Type: merged type ([The center wavelength of the band, in micrometers (μm).](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md "airs_model#/$defs/Band/properties/center_wavelength")

### center\_wavelength Type

merged type ([The center wavelength of the band, in micrometers (μm).](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md))

any of

* [Untitled number in Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm-anyof-1.md "check type definition")

## full\_width\_half\_max



`full_width_half_max`

* is optional

* Type: merged type ([Full width at half maximum (FWHM). The width of the band, as measured at half the maximum transmission, in micrometers (μm).](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md "airs_model#/$defs/Band/properties/full_width_half_max")

### full\_width\_half\_max Type

merged type ([Full width at half maximum (FWHM). The width of the band, as measured at half the maximum transmission, in micrometers (μm).](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md))

any of

* [Untitled number in Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm-anyof-1.md "check type definition")

## solar\_illumination



`solar_illumination`

* is optional

* Type: merged type ([The solar illumination of the band, as measured at half the maximum transmission, in W/m2/micrometers.](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md "airs_model#/$defs/Band/properties/solar_illumination")

### solar\_illumination Type

merged type ([The solar illumination of the band, as measured at half the maximum transmission, in W/m2/micrometers.](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md))

any of

* [Untitled number in Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers-anyof-1.md "check type definition")

## quality\_indicators



`quality_indicators`

* is optional

* Type: merged type ([Set of indicators for estimating the quality of the datacube variable (band).](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md))

* cannot be null

* defined in: [Item](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md "airs_model#/$defs/Band/properties/quality_indicators")

### quality\_indicators Type

merged type ([Set of indicators for estimating the quality of the datacube variable (band).](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md))

any of

* [Indicators](model-defs-indicators.md "check type definition")

* [Untitled null in Item](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band-anyof-1.md "check type definition")

## Additional Properties

Additional properties are allowed and do not have to follow a specific schema
