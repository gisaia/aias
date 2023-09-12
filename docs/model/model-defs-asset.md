# Asset Schema

```txt
airs_model#/properties/assets/anyOf/0/additionalProperties
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## additionalProperties Type

`object` ([Asset](model-defs-asset.md))

# additionalProperties Properties

| Property                                                          | Type   | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                            |
| :---------------------------------------------------------------- | :----- | :------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [name](#name)                                                     | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md "airs_model#/$defs/Asset/properties/name")                                                                                                                                      |
| [href](#href)                                                     | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-absolute-link-to-the-asset-object.md "airs_model#/$defs/Asset/properties/href")                                                                                                                                                                    |
| [storage\_\_requester\_pays](#storage__requester_pays)            | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "airs_model#/$defs/Asset/properties/storage__requester_pays")                                             |
| [storage\_\_tier](#storage__tier)                                 | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "airs_model#/$defs/Asset/properties/storage__tier")                                                                                                                                           |
| [storage\_\_platform](#storage__platform)                         | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "airs_model#/$defs/Asset/properties/storage__platform")                                                                                                                                   |
| [storage\_\_region](#storage__region)                             | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "airs_model#/$defs/Asset/properties/storage__region")                                                                 |
| [airs\_\_managed](#airs__managed)                                 | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-whether-the-asset-is-managed-by-airs-or-not.md "airs_model#/$defs/Asset/properties/airs__managed")                                                                                                                                                 |
| [airs\_\_object\_store\_bucket](#airs__object_store_bucket)       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md "airs_model#/$defs/Asset/properties/airs__object_store_bucket")                                                                                                                                        |
| [airs\_\_object\_store\_key](#airs__object_store_key)             | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-object-store-key-of-the-asset-object.md "airs_model#/$defs/Asset/properties/airs__object_store_key")                                                                                                                                               |
| [title](#title)                                                   | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md "airs_model#/$defs/Asset/properties/title")                                                                                                                                                      |
| [description](#description)                                       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "airs_model#/$defs/Asset/properties/description")                                |
| [type](#type)                                                     | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md "airs_model#/$defs/Asset/properties/type")                                                                                     |
| [roles](#roles)                                                   | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md "airs_model#/$defs/Asset/properties/roles")                                                                                                                            |
| [extra\_fields](#extra_fields)                                    | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md "airs_model#/$defs/Asset/properties/extra_fields")                                                   |
| [gsd](#gsd)                                                       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md "airs_model#/$defs/Asset/properties/gsd")                                                                                                                                                      |
| [eo\_\_bands](#eo__bands)                                         | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "airs_model#/$defs/Asset/properties/eo__bands")                                                                                              |
| [sar\_\_instrument\_mode](#sar__instrument_mode)                  | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "airs_model#/$defs/Asset/properties/sar__instrument_mode")      |
| [sar\_\_frequency\_band](#sar__frequency_band)                    | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "airs_model#/$defs/Asset/properties/sar__frequency_band")                  |
| [sar\_\_center\_frequency](#sar__center_frequency)                | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "airs_model#/$defs/Asset/properties/sar__center_frequency")                                                                                                                             |
| [sar\_\_polarizations](#sar__polarizations)                       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-any-combination-of-polarizations.md "airs_model#/$defs/Asset/properties/sar__polarizations")                                                                                                                                                       |
| [sar\_\_product\_type](#sar__product_type)                        | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "airs_model#/$defs/Asset/properties/sar__product_type")                                                                                                                                             |
| [sar\_\_resolution\_range](#sar__resolution_range)                | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Asset/properties/sar__resolution_range")                                                  |
| [sar\_\_resolution\_azimuth](#sar__resolution_azimuth)            | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Asset/properties/sar__resolution_azimuth")                                                   |
| [sar\_\_pixel\_spacing\_range](#sar__pixel_spacing_range)         | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Asset/properties/sar__pixel_spacing_range") |
| [sar\_\_pixel\_spacing\_azimuth](#sar__pixel_spacing_azimuth)     | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Asset/properties/sar__pixel_spacing_azimuth")  |
| [sar\_\_looks\_range](#sar__looks_range)                          | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "airs_model#/$defs/Asset/properties/sar__looks_range")                                                                             |
| [sar\_\_looks\_azimuth](#sar__looks_azimuth)                      | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "airs_model#/$defs/Asset/properties/sar__looks_azimuth")                                                                              |
| [sar\_\_looks\_equivalent\_number](#sar__looks_equivalent_number) | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md "airs_model#/$defs/Asset/properties/sar__looks_equivalent_number")                                                                                                                                           |
| [sar\_\_observation\_direction](#sar__observation_direction)      | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "airs_model#/$defs/Asset/properties/sar__observation_direction")                                                                             |
| [proj\_\_epsg](#proj__epsg)                                       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-epsg-code-of-the-datasource.md "airs_model#/$defs/Asset/properties/proj__epsg")                                                                                                                                                                    |
| [proj\_\_wkt2](#proj__wkt2)                                       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "airs_model#/$defs/Asset/properties/proj__wkt2")                                                                           |
| [proj\_\_geometry](#proj__geometry)                               | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-defines-the-footprint-of-this-item.md "airs_model#/$defs/Asset/properties/proj__geometry")                                                                                                                                                         |
| [proj\_\_bbox](#proj__bbox)                                       | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "airs_model#/$defs/Asset/properties/proj__bbox")                                                                                                                                 |
| [proj\_\_centroid](#proj__centroid)                               | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "airs_model#/$defs/Asset/properties/proj__centroid")                                                                                                                               |
| [proj\_\_shape](#proj__shape)                                     | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "airs_model#/$defs/Asset/properties/proj__shape")                                                                                                                                   |
| [proj\_\_transform](#proj__transform)                             | Merged | Optional | cannot be null | [Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md "airs_model#/$defs/Asset/properties/proj__transform")                                                                                                                               |
| Additional Properties                                             | Any    | Optional | can be null    |                                                                                                                                                                                                                                                                                       |

## name



`name`

*   is optional

*   Type: merged type ([Asset's name. But be the same as the key in the \`assets\` dictionary.](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md "airs_model#/$defs/Asset/properties/name")

### name Type

merged type ([Asset's name. But be the same as the key in the \`assets\` dictionary.](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary-anyof-1.md "check type definition")

## href



`href`

*   is optional

*   Type: merged type ([Absolute link to the asset object.](model-defs-asset-properties-absolute-link-to-the-asset-object.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-absolute-link-to-the-asset-object.md "airs_model#/$defs/Asset/properties/href")

### href Type

merged type ([Absolute link to the asset object.](model-defs-asset-properties-absolute-link-to-the-asset-object.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-absolute-link-to-the-asset-object-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-absolute-link-to-the-asset-object-anyof-1.md "check type definition")

## storage\_\_requester\_pays



`storage__requester_pays`

*   is optional

*   Type: merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "airs_model#/$defs/Asset/properties/storage__requester_pays")

### storage\_\_requester\_pays Type

merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

any of

*   [Untitled boolean in Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-1.md "check type definition")

## storage\_\_tier



`storage__tier`

*   is optional

*   Type: merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "airs_model#/$defs/Asset/properties/storage__tier")

### storage\_\_tier Type

merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-1.md "check type definition")

## storage\_\_platform



`storage__platform`

*   is optional

*   Type: merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "airs_model#/$defs/Asset/properties/storage__platform")

### storage\_\_platform Type

merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-1.md "check type definition")

## storage\_\_region



`storage__region`

*   is optional

*   Type: merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "airs_model#/$defs/Asset/properties/storage__region")

### storage\_\_region Type

merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-1.md "check type definition")

## airs\_\_managed



`airs__managed`

*   is optional

*   Type: merged type ([Whether the asset is managed by AIRS or not.](model-defs-asset-properties-whether-the-asset-is-managed-by-airs-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-whether-the-asset-is-managed-by-airs-or-not.md "airs_model#/$defs/Asset/properties/airs__managed")

### airs\_\_managed Type

merged type ([Whether the asset is managed by AIRS or not.](model-defs-asset-properties-whether-the-asset-is-managed-by-airs-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-asset-properties-whether-the-asset-is-managed-by-airs-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-whether-the-asset-is-managed-by-airs-or-not-anyof-1.md "check type definition")

### airs\_\_managed Default Value

The default value is:

```json
true
```

## airs\_\_object\_store\_bucket



`airs__object_store_bucket`

*   is optional

*   Type: merged type ([Object store bucket for the asset object.](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md "airs_model#/$defs/Asset/properties/airs__object_store_bucket")

### airs\_\_object\_store\_bucket Type

merged type ([Object store bucket for the asset object.](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object-anyof-1.md "check type definition")

## airs\_\_object\_store\_key



`airs__object_store_key`

*   is optional

*   Type: merged type ([Object store key of the asset object.](model-defs-asset-properties-object-store-key-of-the-asset-object.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-object-store-key-of-the-asset-object.md "airs_model#/$defs/Asset/properties/airs__object_store_key")

### airs\_\_object\_store\_key Type

merged type ([Object store key of the asset object.](model-defs-asset-properties-object-store-key-of-the-asset-object.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-object-store-key-of-the-asset-object-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-object-store-key-of-the-asset-object-anyof-1.md "check type definition")

## title



`title`

*   is optional

*   Type: merged type ([Optional displayed title for clients and users.](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md "airs_model#/$defs/Asset/properties/title")

### title Type

merged type ([Optional displayed title for clients and users.](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users-anyof-1.md "check type definition")

## description



`description`

*   is optional

*   Type: merged type ([A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "airs_model#/$defs/Asset/properties/description")

### description Type

merged type ([A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-1.md "check type definition")

## type



`type`

*   is optional

*   Type: merged type ([Optional description of the media type. Registered Media Types are preferred. See MediaType for common media types.](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md "airs_model#/$defs/Asset/properties/type")

### type Type

merged type ([Optional description of the media type. Registered Media Types are preferred. See MediaType for common media types.](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types-anyof-1.md "check type definition")

## roles



`roles`

*   is optional

*   Type: merged type ([Optional, Semantic roles (i.e. thumbnail, overview, data, metadata) of the asset.](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md "airs_model#/$defs/Asset/properties/roles")

### roles Type

merged type ([Optional, Semantic roles (i.e. thumbnail, overview, data, metadata) of the asset.](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset-anyof-1.md "check type definition")

## extra\_fields



`extra_fields`

*   is optional

*   Type: merged type ([Optional, additional fields for this asset. This is used by extensions as a way to serialize and deserialize properties on asset object JSON.](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md "airs_model#/$defs/Asset/properties/extra_fields")

### extra\_fields Type

merged type ([Optional, additional fields for this asset. This is used by extensions as a way to serialize and deserialize properties on asset object JSON.](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md))

any of

*   [Untitled object in Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json-anyof-1.md "check type definition")

## gsd



`gsd`

*   is optional

*   Type: merged type ([Ground Sampling Distance (resolution) of the asset](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md "airs_model#/$defs/Asset/properties/gsd")

### gsd Type

merged type ([Ground Sampling Distance (resolution) of the asset](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset-anyof-1.md "check type definition")

## eo\_\_bands



`eo__bands`

*   is optional

*   Type: merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "airs_model#/$defs/Asset/properties/eo__bands")

### eo\_\_bands Type

merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-1.md "check type definition")

## sar\_\_instrument\_mode



`sar__instrument_mode`

*   is optional

*   Type: merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "airs_model#/$defs/Asset/properties/sar__instrument_mode")

### sar\_\_instrument\_mode Type

merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-1.md "check type definition")

## sar\_\_frequency\_band



`sar__frequency_band`

*   is optional

*   Type: merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "airs_model#/$defs/Asset/properties/sar__frequency_band")

### sar\_\_frequency\_band Type

merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-1.md "check type definition")

## sar\_\_center\_frequency



`sar__center_frequency`

*   is optional

*   Type: merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "airs_model#/$defs/Asset/properties/sar__center_frequency")

### sar\_\_center\_frequency Type

merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-1.md "check type definition")

## sar\_\_polarizations



`sar__polarizations`

*   is optional

*   Type: merged type ([Any combination of polarizations.](model-defs-asset-properties-any-combination-of-polarizations.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-any-combination-of-polarizations.md "airs_model#/$defs/Asset/properties/sar__polarizations")

### sar\_\_polarizations Type

merged type ([Any combination of polarizations.](model-defs-asset-properties-any-combination-of-polarizations.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-any-combination-of-polarizations-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-any-combination-of-polarizations-anyof-1.md "check type definition")

## sar\_\_product\_type



`sar__product_type`

*   is optional

*   Type: merged type ([The product type, for example SSC, MGD, or SGC](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "airs_model#/$defs/Asset/properties/sar__product_type")

### sar\_\_product\_type Type

merged type ([The product type, for example SSC, MGD, or SGC](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-1.md "check type definition")

## sar\_\_resolution\_range



`sar__resolution_range`

*   is optional

*   Type: merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Asset/properties/sar__resolution_range")

### sar\_\_resolution\_range Type

merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

## sar\_\_resolution\_azimuth



`sar__resolution_azimuth`

*   is optional

*   Type: merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Asset/properties/sar__resolution_azimuth")

### sar\_\_resolution\_azimuth Type

merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

## sar\_\_pixel\_spacing\_range



`sar__pixel_spacing_range`

*   is optional

*   Type: merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Asset/properties/sar__pixel_spacing_range")

### sar\_\_pixel\_spacing\_range Type

merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

## sar\_\_pixel\_spacing\_azimuth



`sar__pixel_spacing_azimuth`

*   is optional

*   Type: merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Asset/properties/sar__pixel_spacing_azimuth")

### sar\_\_pixel\_spacing\_azimuth Type

merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

## sar\_\_looks\_range



`sar__looks_range`

*   is optional

*   Type: merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "airs_model#/$defs/Asset/properties/sar__looks_range")

### sar\_\_looks\_range Type

merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-1.md "check type definition")

## sar\_\_looks\_azimuth



`sar__looks_azimuth`

*   is optional

*   Type: merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "airs_model#/$defs/Asset/properties/sar__looks_azimuth")

### sar\_\_looks\_azimuth Type

merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-1.md "check type definition")

## sar\_\_looks\_equivalent\_number



`sar__looks_equivalent_number`

*   is optional

*   Type: merged type ([The equivalent number of looks (ENL).](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md "airs_model#/$defs/Asset/properties/sar__looks_equivalent_number")

### sar\_\_looks\_equivalent\_number Type

merged type ([The equivalent number of looks (ENL).](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl-anyof-1.md "check type definition")

## sar\_\_observation\_direction



`sar__observation_direction`

*   is optional

*   Type: merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "airs_model#/$defs/Asset/properties/sar__observation_direction")

### sar\_\_observation\_direction Type

merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-1.md "check type definition")

## proj\_\_epsg



`proj__epsg`

*   is optional

*   Type: merged type ([EPSG code of the datasource.](model-defs-asset-properties-epsg-code-of-the-datasource.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-epsg-code-of-the-datasource.md "airs_model#/$defs/Asset/properties/proj__epsg")

### proj\_\_epsg Type

merged type ([EPSG code of the datasource.](model-defs-asset-properties-epsg-code-of-the-datasource.md))

any of

*   [Untitled integer in Item](model-defs-asset-properties-epsg-code-of-the-datasource-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-epsg-code-of-the-datasource-anyof-1.md "check type definition")

## proj\_\_wkt2



`proj__wkt2`

*   is optional

*   Type: merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "airs_model#/$defs/Asset/properties/proj__wkt2")

### proj\_\_wkt2 Type

merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-1.md "check type definition")

## proj\_\_geometry



`proj__geometry`

*   is optional

*   Type: merged type ([Defines the footprint of this Item.](model-defs-asset-properties-defines-the-footprint-of-this-item.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-defines-the-footprint-of-this-item.md "airs_model#/$defs/Asset/properties/proj__geometry")

### proj\_\_geometry Type

merged type ([Defines the footprint of this Item.](model-defs-asset-properties-defines-the-footprint-of-this-item.md))

any of

*   [Untitled undefined type in Item](model-defs-asset-properties-defines-the-footprint-of-this-item-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-defines-the-footprint-of-this-item-anyof-1.md "check type definition")

## proj\_\_bbox



`proj__bbox`

*   is optional

*   Type: merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "airs_model#/$defs/Asset/properties/proj__bbox")

### proj\_\_bbox Type

merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-1.md "check type definition")

## proj\_\_centroid



`proj__centroid`

*   is optional

*   Type: merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "airs_model#/$defs/Asset/properties/proj__centroid")

### proj\_\_centroid Type

merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

any of

*   [Untitled undefined type in Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-1.md "check type definition")

## proj\_\_shape



`proj__shape`

*   is optional

*   Type: merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "airs_model#/$defs/Asset/properties/proj__shape")

### proj\_\_shape Type

merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-1.md "check type definition")

## proj\_\_transform



`proj__transform`

*   is optional

*   Type: merged type ([The affine transformation coefficients for the default grid.](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md "airs_model#/$defs/Asset/properties/proj__transform")

### proj\_\_transform Type

merged type ([The affine transformation coefficients for the default grid.](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-1.md "check type definition")

## Additional Properties

Additional properties are allowed and do not have to follow a specific schema
