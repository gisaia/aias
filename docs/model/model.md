# Item Schema

```txt
aeopres_model
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                              |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :---------------------------------------------------------------------- |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json](../../out/model.schema.json "open original schema") |

## Item Type

`object` ([Item](model.md))

# Item Properties

| Property                  | Type   | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                |
| :------------------------ | :----- | :------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [collection](#collection) | Merged | Optional | cannot be null | [Item](model-properties-name-of-the-collection-the-item-belongs-to.md "aeopres_model#/properties/collection")                                                                                                                                                             |
| [catalog](#catalog)       | Merged | Optional | cannot be null | [Item](model-properties-name-of-the-catalog-the-item-belongs-to.md "aeopres_model#/properties/catalog")                                                                                                                                                                   |
| [id](#id)                 | Merged | Optional | cannot be null | [Item](model-properties-provider-identifier-must-be-unique-within-the-stac.md "aeopres_model#/properties/id")                                                                                                                                                             |
| [geometry](#geometry)     | Merged | Optional | cannot be null | [Item](model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_.md "aeopres_model#/properties/geometry")                                                        |
| [bbox](#bbox)             | Merged | Optional | cannot be null | [Item](model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry.md "aeopres_model#/properties/bbox") |
| [centroid](#centroid)     | Merged | Optional | cannot be null | [Item](model-properties-coordinates-latlon-of-the-geometrys-centroid.md "aeopres_model#/properties/centroid")                                                                                                                                                             |
| [assets](#assets)         | Merged | Optional | cannot be null | [Item](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item.md "aeopres_model#/properties/assets")                                                               |
| [properties](#properties) | Merged | Optional | cannot be null | [Item](model-properties-item-properties.md "aeopres_model#/properties/properties")                                                                                                                                                                                        |

## collection



`collection`

*   is optional

*   Type: merged type ([Name of the collection the item belongs to.](model-properties-name-of-the-collection-the-item-belongs-to.md))

*   cannot be null

*   defined in: [Item](model-properties-name-of-the-collection-the-item-belongs-to.md "aeopres_model#/properties/collection")

### collection Type

merged type ([Name of the collection the item belongs to.](model-properties-name-of-the-collection-the-item-belongs-to.md))

any of

*   [Untitled string in Item](model-properties-name-of-the-collection-the-item-belongs-to-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-name-of-the-collection-the-item-belongs-to-anyof-1.md "check type definition")

## catalog



`catalog`

*   is optional

*   Type: merged type ([Name of the catalog the item belongs to.](model-properties-name-of-the-catalog-the-item-belongs-to.md))

*   cannot be null

*   defined in: [Item](model-properties-name-of-the-catalog-the-item-belongs-to.md "aeopres_model#/properties/catalog")

### catalog Type

merged type ([Name of the catalog the item belongs to.](model-properties-name-of-the-catalog-the-item-belongs-to.md))

any of

*   [Untitled string in Item](model-properties-name-of-the-catalog-the-item-belongs-to-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-name-of-the-catalog-the-item-belongs-to-anyof-1.md "check type definition")

## id



`id`

*   is optional

*   Type: merged type ([Provider identifier. Must be unique within the STAC.](model-properties-provider-identifier-must-be-unique-within-the-stac.md))

*   cannot be null

*   defined in: [Item](model-properties-provider-identifier-must-be-unique-within-the-stac.md "aeopres_model#/properties/id")

### id Type

merged type ([Provider identifier. Must be unique within the STAC.](model-properties-provider-identifier-must-be-unique-within-the-stac.md))

any of

*   [Untitled string in Item](model-properties-provider-identifier-must-be-unique-within-the-stac-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-provider-identifier-must-be-unique-within-the-stac-anyof-1.md "check type definition")

## geometry



`geometry`

*   is optional

*   Type: merged type ([Defines the full footprint of the asset represented by this item, formatted according to \`RFC 7946, section 3.1 (GeoJSON) \<https://tools.ietf.org/html/rfc7946>\`\_](model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_.md))

*   cannot be null

*   defined in: [Item](model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_.md "aeopres_model#/properties/geometry")

### geometry Type

merged type ([Defines the full footprint of the asset represented by this item, formatted according to \`RFC 7946, section 3.1 (GeoJSON) \<https://tools.ietf.org/html/rfc7946>\`\_](model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_.md))

any of

*   [Untitled object in Item](model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_-anyof-1.md "check type definition")

## bbox



`bbox`

*   is optional

*   Type: merged type ([Bounding Box of the asset represented by this item using either 2D or 3D geometries. The length of the array must be 2\*n where n is the number of dimensions. Could also be None in the case of a null geometry.](model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry.md))

*   cannot be null

*   defined in: [Item](model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry.md "aeopres_model#/properties/bbox")

### bbox Type

merged type ([Bounding Box of the asset represented by this item using either 2D or 3D geometries. The length of the array must be 2\*n where n is the number of dimensions. Could also be None in the case of a null geometry.](model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry.md))

any of

*   [Untitled array in Item](model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry-anyof-1.md "check type definition")

## centroid



`centroid`

*   is optional

*   Type: merged type ([Coordinates (lat/lon) of the geometry's centroid.](model-properties-coordinates-latlon-of-the-geometrys-centroid.md))

*   cannot be null

*   defined in: [Item](model-properties-coordinates-latlon-of-the-geometrys-centroid.md "aeopres_model#/properties/centroid")

### centroid Type

merged type ([Coordinates (lat/lon) of the geometry's centroid.](model-properties-coordinates-latlon-of-the-geometrys-centroid.md))

any of

*   [Untitled array in Item](model-properties-coordinates-latlon-of-the-geometrys-centroid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-coordinates-latlon-of-the-geometrys-centroid-anyof-1.md "check type definition")

## assets



`assets`

*   is optional

*   Type: merged type ([A dictionary mapping string keys to Asset objects. All Asset values in the dictionary will have their owner attribute set to the created Item.](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item.md))

*   cannot be null

*   defined in: [Item](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item.md "aeopres_model#/properties/assets")

### assets Type

merged type ([A dictionary mapping string keys to Asset objects. All Asset values in the dictionary will have their owner attribute set to the created Item.](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item.md))

any of

*   [Untitled object in Item](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item-anyof-0.md "check type definition")

*   [Untitled null in Item](model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item-anyof-1.md "check type definition")

## properties



`properties`

*   is optional

*   Type: merged type ([Item properties](model-properties-item-properties.md))

*   cannot be null

*   defined in: [Item](model-properties-item-properties.md "aeopres_model#/properties/properties")

### properties Type

merged type ([Item properties](model-properties-item-properties.md))

any of

*   [Properties](model-defs-properties.md "check type definition")

*   [Untitled null in Item](model-properties-item-properties-anyof-1.md "check type definition")

# Item Definitions

## Definitions group Asset

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/Asset"}
```

| Property                                                     | Type      | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                              |
| :----------------------------------------------------------- | :-------- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [name](#name)                                                | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md "aeopres_model#/$defs/Asset/properties/name")                                                                                                                                     |
| [href](#href)                                                | `string`  | Optional | cannot be null | [Item](model-defs-asset-properties-absolute-link-to-the-asset-object.md "aeopres_model#/$defs/Asset/properties/href")                                                                                                                                                                   |
| [storage:requester\_pays](#storagerequester_pays)            | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "aeopres_model#/$defs/Asset/properties/storage:requester_pays")                                             |
| [storage:tier](#storagetier)                                 | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "aeopres_model#/$defs/Asset/properties/storage:tier")                                                                                                                                           |
| [storage:platform](#storageplatform)                         | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "aeopres_model#/$defs/Asset/properties/storage:platform")                                                                                                                                   |
| [storage:region](#storageregion)                             | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "aeopres_model#/$defs/Asset/properties/storage:region")                                                                 |
| [aeo:managed](#aeomanaged)                                   | `boolean` | Optional | cannot be null | [Item](model-defs-asset-properties-whether-the-asset-is-managed-by-aeoprs-or-not.md "aeopres_model#/$defs/Asset/properties/aeo:managed")                                                                                                                                                |
| [aeo:object\_store\_bucket](#aeoobject_store_bucket)         | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md "aeopres_model#/$defs/Asset/properties/aeo:object_store_bucket")                                                                                                                                         |
| [aeo:object\_store\_key](#aeoobject_store_key)               | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-object-store-key-of-the-asset-object.md "aeopres_model#/$defs/Asset/properties/aeo:object_store_key")                                                                                                                                                |
| [title](#title)                                              | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md "aeopres_model#/$defs/Asset/properties/title")                                                                                                                                                     |
| [description](#description)                                  | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "aeopres_model#/$defs/Asset/properties/description")                               |
| [type](#type)                                                | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md "aeopres_model#/$defs/Asset/properties/type")                                                                                    |
| [roles](#roles)                                              | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md "aeopres_model#/$defs/Asset/properties/roles")                                                                                                                           |
| [extra\_fields](#extra_fields)                               | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md "aeopres_model#/$defs/Asset/properties/extra_fields")                                                  |
| [gsd](#gsd)                                                  | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md "aeopres_model#/$defs/Asset/properties/gsd")                                                                                                                                                     |
| [eo:bands](#eobands)                                         | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "aeopres_model#/$defs/Asset/properties/eo:bands")                                                                                              |
| [sar:instrument\_mode](#sarinstrument_mode)                  | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "aeopres_model#/$defs/Asset/properties/sar:instrument_mode")      |
| [sar:frequency\_band](#sarfrequency_band)                    | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "aeopres_model#/$defs/Asset/properties/sar:frequency_band")                  |
| [sar:center\_frequency](#sarcenter_frequency)                | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "aeopres_model#/$defs/Asset/properties/sar:center_frequency")                                                                                                                             |
| [sar:polarizations](#sarpolarizations)                       | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-any-combination-of-polarizations.md "aeopres_model#/$defs/Asset/properties/sar:polarizations")                                                                                                                                                       |
| [sar:product\_type](#sarproduct_type)                        | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "aeopres_model#/$defs/Asset/properties/sar:product_type")                                                                                                                                             |
| [sar:resolution\_range](#sarresolution_range)                | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Asset/properties/sar:resolution_range")                                                  |
| [sar:resolution\_azimuth](#sarresolution_azimuth)            | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Asset/properties/sar:resolution_azimuth")                                                   |
| [sar:pixel\_spacing\_range](#sarpixel_spacing_range)         | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Asset/properties/sar:pixel_spacing_range") |
| [sar:pixel\_spacing\_azimuth](#sarpixel_spacing_azimuth)     | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Asset/properties/sar:pixel_spacing_azimuth")  |
| [sar:looks\_range](#sarlooks_range)                          | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "aeopres_model#/$defs/Asset/properties/sar:looks_range")                                                                             |
| [sar:looks\_azimuth](#sarlooks_azimuth)                      | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "aeopres_model#/$defs/Asset/properties/sar:looks_azimuth")                                                                              |
| [sar:looks\_equivalent\_number](#sarlooks_equivalent_number) | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md "aeopres_model#/$defs/Asset/properties/sar:looks_equivalent_number")                                                                                                                                           |
| [sar:observation\_direction](#sarobservation_direction)      | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "aeopres_model#/$defs/Asset/properties/sar:observation_direction")                                                                             |
| [proj:epsg](#projepsg)                                       | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-epsg-code-of-the-datasource.md "aeopres_model#/$defs/Asset/properties/proj:epsg")                                                                                                                                                                    |
| [proj:wkt2](#projwkt2)                                       | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "aeopres_model#/$defs/Asset/properties/proj:wkt2")                                                                           |
| [proj:geometry](#projgeometry)                               | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-defines-the-footprint-of-this-item.md "aeopres_model#/$defs/Asset/properties/proj:geometry")                                                                                                                                                         |
| [proj:bbox](#projbbox)                                       | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "aeopres_model#/$defs/Asset/properties/proj:bbox")                                                                                                                                 |
| [proj:centroid](#projcentroid)                               | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "aeopres_model#/$defs/Asset/properties/proj:centroid")                                                                                                                               |
| [proj:shape](#projshape)                                     | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "aeopres_model#/$defs/Asset/properties/proj:shape")                                                                                                                                   |
| [proj:transform](#projtransform)                             | Merged    | Optional | cannot be null | [Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md "aeopres_model#/$defs/Asset/properties/proj:transform")                                                                                                                               |

### name



`name`

*   is optional

*   Type: merged type ([Asset's name. But be the same as the key in the \`assets\` dictionary.](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md "aeopres_model#/$defs/Asset/properties/name")

#### name Type

merged type ([Asset's name. But be the same as the key in the \`assets\` dictionary.](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-assets-name-but-be-the-same-as-the-key-in-the-assets-dictionary-anyof-1.md "check type definition")

### href



`href`

*   is optional

*   Type: `string` ([Absolute link to the asset object.](model-defs-asset-properties-absolute-link-to-the-asset-object.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-absolute-link-to-the-asset-object.md "aeopres_model#/$defs/Asset/properties/href")

#### href Type

`string` ([Absolute link to the asset object.](model-defs-asset-properties-absolute-link-to-the-asset-object.md))

### storage:requester\_pays



`storage:requester_pays`

*   is optional

*   Type: merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "aeopres_model#/$defs/Asset/properties/storage:requester_pays")

#### storage:requester\_pays Type

merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

any of

*   [Untitled boolean in Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-1.md "check type definition")

### storage:tier



`storage:tier`

*   is optional

*   Type: merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "aeopres_model#/$defs/Asset/properties/storage:tier")

#### storage:tier Type

merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-1.md "check type definition")

### storage:platform



`storage:platform`

*   is optional

*   Type: merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "aeopres_model#/$defs/Asset/properties/storage:platform")

#### storage:platform Type

merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-1.md "check type definition")

### storage:region



`storage:region`

*   is optional

*   Type: merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "aeopres_model#/$defs/Asset/properties/storage:region")

#### storage:region Type

merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-1.md "check type definition")

### aeo:managed



`aeo:managed`

*   is optional

*   Type: `boolean` ([Whether the asset is managed by AEOPRS or not.](model-defs-asset-properties-whether-the-asset-is-managed-by-aeoprs-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-whether-the-asset-is-managed-by-aeoprs-or-not.md "aeopres_model#/$defs/Asset/properties/aeo:managed")

#### aeo:managed Type

`boolean` ([Whether the asset is managed by AEOPRS or not.](model-defs-asset-properties-whether-the-asset-is-managed-by-aeoprs-or-not.md))

#### aeo:managed Default Value

The default value is:

```json
true
```

### aeo:object\_store\_bucket



`aeo:object_store_bucket`

*   is optional

*   Type: merged type ([Object store bucket for the asset object.](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md "aeopres_model#/$defs/Asset/properties/aeo:object_store_bucket")

#### aeo:object\_store\_bucket Type

merged type ([Object store bucket for the asset object.](model-defs-asset-properties-object-store-bucket-for-the-asset-object.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-object-store-bucket-for-the-asset-object-anyof-1.md "check type definition")

### aeo:object\_store\_key



`aeo:object_store_key`

*   is optional

*   Type: merged type ([Object store key of the asset object.](model-defs-asset-properties-object-store-key-of-the-asset-object.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-object-store-key-of-the-asset-object.md "aeopres_model#/$defs/Asset/properties/aeo:object_store_key")

#### aeo:object\_store\_key Type

merged type ([Object store key of the asset object.](model-defs-asset-properties-object-store-key-of-the-asset-object.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-object-store-key-of-the-asset-object-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-object-store-key-of-the-asset-object-anyof-1.md "check type definition")

### title



`title`

*   is optional

*   Type: merged type ([Optional displayed title for clients and users.](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md "aeopres_model#/$defs/Asset/properties/title")

#### title Type

merged type ([Optional displayed title for clients and users.](model-defs-asset-properties-optional-displayed-title-for-clients-and-users.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-displayed-title-for-clients-and-users-anyof-1.md "check type definition")

### description



`description`

*   is optional

*   Type: merged type ([A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "aeopres_model#/$defs/Asset/properties/description")

#### description Type

merged type ([A description of the Asset providing additional details, such as how it was processed or created. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-a-description-of-the-asset-providing-additional-details-such-as-how-it-was-processed-or-created-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-1.md "check type definition")

### type



`type`

*   is optional

*   Type: merged type ([Optional description of the media type. Registered Media Types are preferred. See MediaType for common media types.](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md "aeopres_model#/$defs/Asset/properties/type")

#### type Type

merged type ([Optional description of the media type. Registered Media Types are preferred. See MediaType for common media types.](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-description-of-the-media-type-registered-media-types-are-preferred-see-mediatype-for-common-media-types-anyof-1.md "check type definition")

### roles



`roles`

*   is optional

*   Type: merged type ([Optional, Semantic roles (i.e. thumbnail, overview, data, metadata) of the asset.](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md "aeopres_model#/$defs/Asset/properties/roles")

#### roles Type

merged type ([Optional, Semantic roles (i.e. thumbnail, overview, data, metadata) of the asset.](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset-anyof-1.md "check type definition")

### extra\_fields



`extra_fields`

*   is optional

*   Type: merged type ([Optional, additional fields for this asset. This is used by extensions as a way to serialize and deserialize properties on asset object JSON.](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md "aeopres_model#/$defs/Asset/properties/extra_fields")

#### extra\_fields Type

merged type ([Optional, additional fields for this asset. This is used by extensions as a way to serialize and deserialize properties on asset object JSON.](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json.md))

any of

*   [Untitled object in Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json-anyof-1.md "check type definition")

### gsd



`gsd`

*   is optional

*   Type: merged type ([Ground Sampling Distance (resolution) of the asset](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md "aeopres_model#/$defs/Asset/properties/gsd")

#### gsd Type

merged type ([Ground Sampling Distance (resolution) of the asset](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-ground-sampling-distance-resolution-of-the-asset-anyof-1.md "check type definition")

### eo:bands



`eo:bands`

*   is optional

*   Type: merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "aeopres_model#/$defs/Asset/properties/eo:bands")

#### eo:bands Type

merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-1.md "check type definition")

### sar:instrument\_mode



`sar:instrument_mode`

*   is optional

*   Type: merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "aeopres_model#/$defs/Asset/properties/sar:instrument_mode")

#### sar:instrument\_mode Type

merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-1.md "check type definition")

### sar:frequency\_band



`sar:frequency_band`

*   is optional

*   Type: merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "aeopres_model#/$defs/Asset/properties/sar:frequency_band")

#### sar:frequency\_band Type

merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-1.md "check type definition")

### sar:center\_frequency



`sar:center_frequency`

*   is optional

*   Type: merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "aeopres_model#/$defs/Asset/properties/sar:center_frequency")

#### sar:center\_frequency Type

merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-1.md "check type definition")

### sar:polarizations



`sar:polarizations`

*   is optional

*   Type: merged type ([Any combination of polarizations.](model-defs-asset-properties-any-combination-of-polarizations.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-any-combination-of-polarizations.md "aeopres_model#/$defs/Asset/properties/sar:polarizations")

#### sar:polarizations Type

merged type ([Any combination of polarizations.](model-defs-asset-properties-any-combination-of-polarizations.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-any-combination-of-polarizations-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-any-combination-of-polarizations-anyof-1.md "check type definition")

### sar:product\_type



`sar:product_type`

*   is optional

*   Type: merged type ([The product type, for example SSC, MGD, or SGC](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "aeopres_model#/$defs/Asset/properties/sar:product_type")

#### sar:product\_type Type

merged type ([The product type, for example SSC, MGD, or SGC](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-1.md "check type definition")

### sar:resolution\_range



`sar:resolution_range`

*   is optional

*   Type: merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Asset/properties/sar:resolution_range")

#### sar:resolution\_range Type

merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

### sar:resolution\_azimuth



`sar:resolution_azimuth`

*   is optional

*   Type: merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Asset/properties/sar:resolution_azimuth")

#### sar:resolution\_azimuth Type

merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

### sar:pixel\_spacing\_range



`sar:pixel_spacing_range`

*   is optional

*   Type: merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Asset/properties/sar:pixel_spacing_range")

#### sar:pixel\_spacing\_range Type

merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

### sar:pixel\_spacing\_azimuth



`sar:pixel_spacing_azimuth`

*   is optional

*   Type: merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Asset/properties/sar:pixel_spacing_azimuth")

#### sar:pixel\_spacing\_azimuth Type

merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

### sar:looks\_range



`sar:looks_range`

*   is optional

*   Type: merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "aeopres_model#/$defs/Asset/properties/sar:looks_range")

#### sar:looks\_range Type

merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-1.md "check type definition")

### sar:looks\_azimuth



`sar:looks_azimuth`

*   is optional

*   Type: merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "aeopres_model#/$defs/Asset/properties/sar:looks_azimuth")

#### sar:looks\_azimuth Type

merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-1.md "check type definition")

### sar:looks\_equivalent\_number



`sar:looks_equivalent_number`

*   is optional

*   Type: merged type ([The equivalent number of looks (ENL).](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md "aeopres_model#/$defs/Asset/properties/sar:looks_equivalent_number")

#### sar:looks\_equivalent\_number Type

merged type ([The equivalent number of looks (ENL).](model-defs-asset-properties-the-equivalent-number-of-looks-enl.md))

any of

*   [Untitled number in Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-equivalent-number-of-looks-enl-anyof-1.md "check type definition")

### sar:observation\_direction



`sar:observation_direction`

*   is optional

*   Type: merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "aeopres_model#/$defs/Asset/properties/sar:observation_direction")

#### sar:observation\_direction Type

merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-1.md "check type definition")

### proj:epsg



`proj:epsg`

*   is optional

*   Type: merged type ([EPSG code of the datasource.](model-defs-asset-properties-epsg-code-of-the-datasource.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-epsg-code-of-the-datasource.md "aeopres_model#/$defs/Asset/properties/proj:epsg")

#### proj:epsg Type

merged type ([EPSG code of the datasource.](model-defs-asset-properties-epsg-code-of-the-datasource.md))

any of

*   [Untitled integer in Item](model-defs-asset-properties-epsg-code-of-the-datasource-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-epsg-code-of-the-datasource-anyof-1.md "check type definition")

### proj:wkt2



`proj:wkt2`

*   is optional

*   Type: merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "aeopres_model#/$defs/Asset/properties/proj:wkt2")

#### proj:wkt2 Type

merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

any of

*   [Untitled string in Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-1.md "check type definition")

### proj:geometry



`proj:geometry`

*   is optional

*   Type: merged type ([Defines the footprint of this Item.](model-defs-asset-properties-defines-the-footprint-of-this-item.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-defines-the-footprint-of-this-item.md "aeopres_model#/$defs/Asset/properties/proj:geometry")

#### proj:geometry Type

merged type ([Defines the footprint of this Item.](model-defs-asset-properties-defines-the-footprint-of-this-item.md))

any of

*   [Untitled undefined type in Item](model-defs-asset-properties-defines-the-footprint-of-this-item-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-defines-the-footprint-of-this-item-anyof-1.md "check type definition")

### proj:bbox



`proj:bbox`

*   is optional

*   Type: merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "aeopres_model#/$defs/Asset/properties/proj:bbox")

#### proj:bbox Type

merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-1.md "check type definition")

### proj:centroid



`proj:centroid`

*   is optional

*   Type: merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "aeopres_model#/$defs/Asset/properties/proj:centroid")

#### proj:centroid Type

merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

any of

*   [Untitled undefined type in Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-1.md "check type definition")

### proj:shape



`proj:shape`

*   is optional

*   Type: merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "aeopres_model#/$defs/Asset/properties/proj:shape")

#### proj:shape Type

merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-1.md "check type definition")

### proj:transform



`proj:transform`

*   is optional

*   Type: merged type ([The affine transformation coefficients for the default grid.](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

*   cannot be null

*   defined in: [Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md "aeopres_model#/$defs/Asset/properties/proj:transform")

#### proj:transform Type

merged type ([The affine transformation coefficients for the default grid.](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

any of

*   [Untitled array in Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-1.md "check type definition")

## Definitions group Band

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/Band"}
```

| Property                                       | Type     | Required | Nullable       | Defined by                                                                                                                                                                                                                          |
| :--------------------------------------------- | :------- | :------- | :------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [name](#name-1)                                | `string` | Required | cannot be null | [Item](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md "aeopres_model#/$defs/Band/properties/name")                                                                                                          |
| [common\_name](#common_name)                   | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md "aeopres_model#/$defs/Band/properties/common_name") |
| [description](#description-1)                  | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "aeopres_model#/$defs/Band/properties/description")                                       |
| [center\_wavelength](#center_wavelength)       | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md "aeopres_model#/$defs/Band/properties/center_wavelength")                                                                                  |
| [full\_width\_half\_max](#full_width_half_max) | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md "aeopres_model#/$defs/Band/properties/full_width_half_max")               |
| [solar\_illumination](#solar_illumination)     | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md "aeopres_model#/$defs/Band/properties/solar_illumination")                                   |
| [quality\_indicators](#quality_indicators)     | Merged   | Optional | cannot be null | [Item](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md "aeopres_model#/$defs/Band/properties/quality_indicators")                                                          |

### name



`name`

*   is required

*   Type: `string` ([The name of the band (e.g., B01, B8, band2, red).](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md "aeopres_model#/$defs/Band/properties/name")

#### name Type

`string` ([The name of the band (e.g., B01, B8, band2, red).](model-defs-band-properties-the-name-of-the-band-eg-b01-b8-band2-red.md))

#### name Constraints

**maximum length**: the maximum number of characters for this string is: `300`

### common\_name



`common_name`

*   is optional

*   Type: merged type ([The name commonly used to refer to the band to make it easier to search for bands across instruments. See the list of accepted common names.](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md "aeopres_model#/$defs/Band/properties/common_name")

#### common\_name Type

merged type ([The name commonly used to refer to the band to make it easier to search for bands across instruments. See the list of accepted common names.](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names.md))

any of

*   [Untitled string in Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-band-properties-the-name-commonly-used-to-refer-to-the-band-to-make-it-easier-to-search-for-bands-across-instruments-see-the-list-of-accepted-common-names-anyof-1.md "check type definition")

### description



`description`

*   is optional

*   Type: merged type ([Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md "aeopres_model#/$defs/Band/properties/description")

#### description Type

merged type ([Description to fully explain the band. CommonMark 0.29 syntax MAY be used for rich text representation.](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation.md))

any of

*   [Untitled string in Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-band-properties-description-to-fully-explain-the-band-commonmark-029-syntax-may-be-used-for-rich-text-representation-anyof-1.md "check type definition")

### center\_wavelength



`center_wavelength`

*   is optional

*   Type: merged type ([The center wavelength of the band, in micrometers (μm).](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md "aeopres_model#/$defs/Band/properties/center_wavelength")

#### center\_wavelength Type

merged type ([The center wavelength of the band, in micrometers (μm).](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm.md))

any of

*   [Untitled number in Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-band-properties-the-center-wavelength-of-the-band-in-micrometers-μm-anyof-1.md "check type definition")

### full\_width\_half\_max



`full_width_half_max`

*   is optional

*   Type: merged type ([Full width at half maximum (FWHM). The width of the band, as measured at half the maximum transmission, in micrometers (μm).](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md "aeopres_model#/$defs/Band/properties/full_width_half_max")

#### full\_width\_half\_max Type

merged type ([Full width at half maximum (FWHM). The width of the band, as measured at half the maximum transmission, in micrometers (μm).](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm.md))

any of

*   [Untitled number in Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-band-properties-full-width-at-half-maximum-fwhm-the-width-of-the-band-as-measured-at-half-the-maximum-transmission-in-micrometers-μm-anyof-1.md "check type definition")

### solar\_illumination



`solar_illumination`

*   is optional

*   Type: merged type ([The solar illumination of the band, as measured at half the maximum transmission, in W/m2/micrometers.](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md "aeopres_model#/$defs/Band/properties/solar_illumination")

#### solar\_illumination Type

merged type ([The solar illumination of the band, as measured at half the maximum transmission, in W/m2/micrometers.](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers.md))

any of

*   [Untitled number in Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-band-properties-the-solar-illumination-of-the-band-as-measured-at-half-the-maximum-transmission-in-wm2micrometers-anyof-1.md "check type definition")

### quality\_indicators



`quality_indicators`

*   is optional

*   Type: merged type ([Set of indicators for estimating the quality of the datacube variable (band).](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md))

*   cannot be null

*   defined in: [Item](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md "aeopres_model#/$defs/Band/properties/quality_indicators")

#### quality\_indicators Type

merged type ([Set of indicators for estimating the quality of the datacube variable (band).](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band.md))

any of

*   [Indicators](model-defs-indicators.md "check type definition")

*   [Untitled null in Item](model-defs-band-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-variable-band-anyof-1.md "check type definition")

## Definitions group DimensionType

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/DimensionType"}
```

| Property | Type | Required | Nullable | Defined by |
| :------- | :--- | :------- | :------- | :--------- |

## Definitions group Group

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/Group"}
```

| Property                                     | Type   | Required | Nullable       | Defined by                                                                                                                                                                                          |
| :------------------------------------------- | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [timestamp](#timestamp)                      | Merged | Optional | cannot be null | [Item](model-defs-group-properties-the-timestamp-of-this-temporal-group.md "aeopres_model#/$defs/Group/properties/timestamp")                                                                       |
| [rasters](#rasters)                          | Merged | Optional | cannot be null | [Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md "aeopres_model#/$defs/Group/properties/rasters")                                                                 |
| [quality\_indicators](#quality_indicators-1) | Merged | Optional | cannot be null | [Item](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md "aeopres_model#/$defs/Group/properties/quality_indicators") |

### timestamp



`timestamp`

*   is optional

*   Type: merged type ([The timestamp of this temporal group.](model-defs-group-properties-the-timestamp-of-this-temporal-group.md))

*   cannot be null

*   defined in: [Item](model-defs-group-properties-the-timestamp-of-this-temporal-group.md "aeopres_model#/$defs/Group/properties/timestamp")

#### timestamp Type

merged type ([The timestamp of this temporal group.](model-defs-group-properties-the-timestamp-of-this-temporal-group.md))

any of

*   [Untitled integer in Item](model-defs-group-properties-the-timestamp-of-this-temporal-group-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-group-properties-the-timestamp-of-this-temporal-group-anyof-1.md "check type definition")

### rasters



`rasters`

*   is optional

*   Type: merged type ([The rasters belonging to this temporal group.](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md))

*   cannot be null

*   defined in: [Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md "aeopres_model#/$defs/Group/properties/rasters")

#### rasters Type

merged type ([The rasters belonging to this temporal group.](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md))

any of

*   [Untitled array in Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group-anyof-1.md "check type definition")

### quality\_indicators



`quality_indicators`

*   is optional

*   Type: merged type ([Set of indicators for estimating the quality of the datacube group. The indicators are group based.](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md))

*   cannot be null

*   defined in: [Item](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md "aeopres_model#/$defs/Group/properties/quality_indicators")

#### quality\_indicators Type

merged type ([Set of indicators for estimating the quality of the datacube group. The indicators are group based.](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md))

any of

*   [Indicators](model-defs-indicators.md "check type definition")

*   [Untitled null in Item](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based-anyof-1.md "check type definition")

## Definitions group Indicators

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/Indicators"}
```

| Property                               | Type   | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                                     |
| :------------------------------------- | :----- | :------- | :------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [time\_compacity](#time_compacity)     | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md "aeopres_model#/$defs/Indicators/properties/time_compacity") |
| [spatial\_coverage](#spatial_coverage) | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md "aeopres_model#/$defs/Indicators/properties/spatial_coverage")                                  |
| [group\_lightness](#group_lightness)   | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md "aeopres_model#/$defs/Indicators/properties/group_lightness")             |
| [time\_regularity](#time_regularity)   | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md "aeopres_model#/$defs/Indicators/properties/time_regularity")                              |

### time\_compacity



`time_compacity`

*   is optional

*   Type: merged type ([Indicates whether the temporal extend of the temporal slices (groups) are compact or not compared to the cube temporal extend. Computed as follow: 1-range(group rasters) / range(cube rasters).](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md "aeopres_model#/$defs/Indicators/properties/time_compacity")

#### time\_compacity Type

merged type ([Indicates whether the temporal extend of the temporal slices (groups) are compact or not compared to the cube temporal extend. Computed as follow: 1-range(group rasters) / range(cube rasters).](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters-anyof-1.md "check type definition")

### spatial\_coverage



`spatial_coverage`

*   is optional

*   Type: merged type ([Indicates the proportion of the region of interest that is covered by the input rasters. Computed as follow: area(intersection(union(rasters),roi)) / area(roi))](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md "aeopres_model#/$defs/Indicators/properties/spatial_coverage")

#### spatial\_coverage Type

merged type ([Indicates the proportion of the region of interest that is covered by the input rasters. Computed as follow: area(intersection(union(rasters),roi)) / area(roi))](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi-anyof-1.md "check type definition")

### group\_lightness



`group_lightness`

*   is optional

*   Type: merged type ([Indicates the proportion of non overlapping regions between the different input rasters. Computed as follow: area(intersection(union(rasters),roi)) / sum(area(intersection(raster, roi)))](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md "aeopres_model#/$defs/Indicators/properties/group_lightness")

#### group\_lightness Type

merged type ([Indicates the proportion of non overlapping regions between the different input rasters. Computed as follow: area(intersection(union(rasters),roi)) / sum(area(intersection(raster, roi)))](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi-anyof-1.md "check type definition")

### time\_regularity



`time_regularity`

*   is optional

*   Type: merged type ([Indicates the regularity of the extends between the temporal slices (groups). Computed as follow: 1-std(inter group temporal gaps)/avg(inter group temporal gaps)](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md "aeopres_model#/$defs/Indicators/properties/time_regularity")

#### time\_regularity Type

merged type ([Indicates the regularity of the extends between the temporal slices (groups). Computed as follow: 1-std(inter group temporal gaps)/avg(inter group temporal gaps)](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps-anyof-1.md "check type definition")

## Definitions group Properties

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/Properties"}
```

| Property                                                       | Type   | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                                                                 |
| :------------------------------------------------------------- | :----- | :------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [datetime](#datetime)                                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md "aeopres_model#/$defs/Properties/properties/datetime")                                                                                                                            |
| [start\_datetime](#start_datetime)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md "aeopres_model#/$defs/Properties/properties/start_datetime")                                                                                                      |
| [end\_datetime](#end_datetime)                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md "aeopres_model#/$defs/Properties/properties/end_datetime")                                                                                                            |
| [programme](#programme)                                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-programme.md "aeopres_model#/$defs/Properties/properties/programme")                                                                                                                                                                                                   |
| [constellation](#constellation)                                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-constellation.md "aeopres_model#/$defs/Properties/properties/constellation")                                                                                                                                                                                           |
| [instrument](#instrument)                                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-instrument.md "aeopres_model#/$defs/Properties/properties/instrument")                                                                                                                                                                                                 |
| [sensor](#sensor)                                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-sensor.md "aeopres_model#/$defs/Properties/properties/sensor")                                                                                                                                                                                                         |
| [sensor\_type](#sensor_type)                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-type-of-sensor.md "aeopres_model#/$defs/Properties/properties/sensor_type")                                                                                                                                                                                                        |
| [gsd](#gsd-1)                                                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-ground-sampling-distance-resolution.md "aeopres_model#/$defs/Properties/properties/gsd")                                                                                                                                                                                           |
| [data\_type](#data_type)                                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-type-of-data.md "aeopres_model#/$defs/Properties/properties/data_type")                                                                                                                                                                                                            |
| [data\_coverage](#data_coverage)                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-data-cover.md "aeopres_model#/$defs/Properties/properties/data_coverage")                                                                                                                                                                                              |
| [water\_coverage](#water_coverage)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-water-cover.md "aeopres_model#/$defs/Properties/properties/water_coverage")                                                                                                                                                                                            |
| [locations](#locations)                                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md "aeopres_model#/$defs/Properties/properties/locations")                                                                                                                                                                                   |
| [create\_datetime](#create_datetime)                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-eo-registration-service.md "aeopres_model#/$defs/Properties/properties/create_datetime")                                                                                                                                 |
| [update\_datetime](#update_datetime)                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-eo-registration-service.md "aeopres_model#/$defs/Properties/properties/update_datetime")                                                                                                                               |
| [view:off\_nadir](#viewoff_nadir)                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md "aeopres_model#/$defs/Properties/properties/view:off_nadir")                                                                                                                |
| [view:incidence\_angle](#viewincidence_angle)                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md "aeopres_model#/$defs/Properties/properties/view:incidence_angle")                            |
| [view:azimuth](#viewazimuth)                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md "aeopres_model#/$defs/Properties/properties/view:azimuth")                  |
| [sview:un\_azimuth](#sviewun_azimuth)                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md "aeopres_model#/$defs/Properties/properties/sview:un_azimuth")                                                                |
| [view:sun\_elevation](#viewsun_elevation)                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md "aeopres_model#/$defs/Properties/properties/view:sun_elevation") |
| [storage:requester\_pays](#storagerequester_pays-1)            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "aeopres_model#/$defs/Properties/properties/storage:requester_pays")                                                                      |
| [storage:tier](#storagetier-1)                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "aeopres_model#/$defs/Properties/properties/storage:tier")                                                                                                                                                                    |
| [storage:platform](#storageplatform-1)                         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "aeopres_model#/$defs/Properties/properties/storage:platform")                                                                                                                                                            |
| [storage:region](#storageregion-1)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "aeopres_model#/$defs/Properties/properties/storage:region")                                                                                          |
| [eo:cloud\_cover](#eocloud_cover)                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-cloud-cover.md "aeopres_model#/$defs/Properties/properties/eo:cloud_cover")                                                                                                                                                                                            |
| [eo:snow\_cover](#eosnow_cover)                                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md "aeopres_model#/$defs/Properties/properties/eo:snow_cover")                                                                                                                                                                                      |
| [eo:bands](#eobands-1)                                         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "aeopres_model#/$defs/Properties/properties/eo:bands")                                                                                                                       |
| [processing:expression](#processingexpression)                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md "aeopres_model#/$defs/Properties/properties/processing:expression")               |
| [processing:lineage](#processinglineage)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md "aeopres_model#/$defs/Properties/properties/processing:lineage")                                       |
| [processing:level](#processinglevel)                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md "aeopres_model#/$defs/Properties/properties/processing:level")                                   |
| [processing:facility](#processingfacility)                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md "aeopres_model#/$defs/Properties/properties/processing:facility")                                                                      |
| [processing:software](#processingsoftware)                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md "aeopres_model#/$defs/Properties/properties/processing:software")                                                                                                            |
| [dc3:quality\_indicators](#dc3quality_indicators)              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md "aeopres_model#/$defs/Properties/properties/dc3:quality_indicators")                  |
| [dc3:composition](#dc3composition)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md "aeopres_model#/$defs/Properties/properties/dc3:composition")                                                                                                                                               |
| [dc3:number\_of\_chunks](#dc3number_of_chunks)                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md "aeopres_model#/$defs/Properties/properties/dc3:number_of_chunks")                                                                                                                                       |
| [dc3:chunk\_weight](#dc3chunk_weight)                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md "aeopres_model#/$defs/Properties/properties/dc3:chunk_weight")                                                                                                                                                                                |
| [dc3:fill\_ratio](#dc3fill_ratio)                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md "aeopres_model#/$defs/Properties/properties/dc3:fill_ratio")                                                                                                                                     |
| [cube:dimensions](#cubedimensions)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md "aeopres_model#/$defs/Properties/properties/cube:dimensions")                                                                                                                                                                         |
| [cube:variables](#cubevariables)                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md "aeopres_model#/$defs/Properties/properties/cube:variables")                                                                                                                                                                           |
| [sar:instrument\_mode](#sarinstrument_mode-1)                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "aeopres_model#/$defs/Properties/properties/sar:instrument_mode")                               |
| [sar:frequency\_band](#sarfrequency_band-1)                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "aeopres_model#/$defs/Properties/properties/sar:frequency_band")                                           |
| [sar:center\_frequency](#sarcenter_frequency-1)                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "aeopres_model#/$defs/Properties/properties/sar:center_frequency")                                                                                                                                                      |
| [sar:polarizations](#sarpolarizations-1)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-any-combination-of-polarizations.md "aeopres_model#/$defs/Properties/properties/sar:polarizations")                                                                                                                                                                                |
| [sar:product\_type](#sarproduct_type-1)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "aeopres_model#/$defs/Properties/properties/sar:product_type")                                                                                                                                                                      |
| [sar:resolution\_range](#sarresolution_range-1)                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Properties/properties/sar:resolution_range")                                                                           |
| [sar:resolution\_azimuth](#sarresolution_azimuth-1)            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Properties/properties/sar:resolution_azimuth")                                                                            |
| [sar:pixel\_spacing\_range](#sarpixel_spacing_range-1)         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Properties/properties/sar:pixel_spacing_range")                          |
| [sar:pixel\_spacing\_azimuth](#sarpixel_spacing_azimuth-1)     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Properties/properties/sar:pixel_spacing_azimuth")                           |
| [sar:looks\_range](#sarlooks_range-1)                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "aeopres_model#/$defs/Properties/properties/sar:looks_range")                                                                                                      |
| [sar:looks\_azimuth](#sarlooks_azimuth-1)                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "aeopres_model#/$defs/Properties/properties/sar:looks_azimuth")                                                                                                       |
| [sar:looks\_equivalent\_number](#sarlooks_equivalent_number-1) | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md "aeopres_model#/$defs/Properties/properties/sar:looks_equivalent_number")                                                                                                                                                                    |
| [sar:observation\_direction](#sarobservation_direction-1)      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "aeopres_model#/$defs/Properties/properties/sar:observation_direction")                                                                                                      |
| [proj:epsg](#projepsg-1)                                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-epsg-code-of-the-datasource.md "aeopres_model#/$defs/Properties/properties/proj:epsg")                                                                                                                                                                                             |
| [proj:wkt2](#projwkt2-1)                                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "aeopres_model#/$defs/Properties/properties/proj:wkt2")                                                                                                    |
| [proj:geometry](#projgeometry-1)                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-defines-the-footprint-of-this-item.md "aeopres_model#/$defs/Properties/properties/proj:geometry")                                                                                                                                                                                  |
| [proj:bbox](#projbbox-1)                                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "aeopres_model#/$defs/Properties/properties/proj:bbox")                                                                                                                                                          |
| [proj:centroid](#projcentroid-1)                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "aeopres_model#/$defs/Properties/properties/proj:centroid")                                                                                                                                                        |
| [proj:shape](#projshape-1)                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "aeopres_model#/$defs/Properties/properties/proj:shape")                                                                                                                                                            |
| [proj:transform](#projtransform-1)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md "aeopres_model#/$defs/Properties/properties/proj:transform")                                                                                                                                                        |
| [generated:has\_overview](#generatedhas_overview)              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_overview")                                                                                                                                                                    |
| [generated:has\_thumbnail](#generatedhas_thumbnail)            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_thumbnail")                                                                                                                                                                   |
| [generated:has\_metadata](#generatedhas_metadata)              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_metadata")                                                                                                                                                                |
| [generated:has\_data](#generatedhas_data)                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_data")                                                                                                                                                                        |
| [generated:has\_cog](#generatedhas_cog)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_cog")                                                                                                                                                                               |
| [generated:has\_zarr](#generatedhas_zarr)                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_zarr")                                                                                                                                                                             |
| [generated:date\_keywords](#generateddate_keywords)            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md "aeopres_model#/$defs/Properties/properties/generated:date_keywords")                                                                                                                                                           |
| [generated:day\_of\_week](#generatedday_of_week)               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-day-of-week.md "aeopres_model#/$defs/Properties/properties/generated:day_of_week")                                                                                                                                                                                                 |
| [generated:day\_of\_year](#generatedday_of_year)               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-day-of-year.md "aeopres_model#/$defs/Properties/properties/generated:day_of_year")                                                                                                                                                                                                 |
| [generated:hour\_of\_day](#generatedhour_of_day)               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-hour-of-day.md "aeopres_model#/$defs/Properties/properties/generated:hour_of_day")                                                                                                                                                                                                 |
| [generated:minute\_of\_day](#generatedminute_of_day)           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-minute-of-day.md "aeopres_model#/$defs/Properties/properties/generated:minute_of_day")                                                                                                                                                                                             |
| [generated:month](#generatedmonth)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-month.md "aeopres_model#/$defs/Properties/properties/generated:month")                                                                                                                                                                                                             |
| [generated:year](#generatedyear)                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-year.md "aeopres_model#/$defs/Properties/properties/generated:year")                                                                                                                                                                                                               |
| [generated:season](#generatedseason)                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-season.md "aeopres_model#/$defs/Properties/properties/generated:season")                                                                                                                                                                                                           |
| [generated:tltrbrbl](#generatedtltrbrbl)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md "aeopres_model#/$defs/Properties/properties/generated:tltrbrbl")                                                                                                                         |
| [generated:band\_common\_names](#generatedband_common_names)   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-the-band-common-names.md "aeopres_model#/$defs/Properties/properties/generated:band_common_names")                                                                                                                                                                         |
| [generated:band\_names](#generatedband_names)                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-the-band-names.md "aeopres_model#/$defs/Properties/properties/generated:band_names")                                                                                                                                                                                       |
| [generated:geohash2](#generatedgeohash2)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-two-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash2")                                                                                                                                                                            |
| [generated:geohash3](#generatedgeohash3)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-three-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash3")                                                                                                                                                                          |
| [generated:geohash4](#generatedgeohash4)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-four-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash4")                                                                                                                                                                           |
| [generated:geohash5](#generatedgeohash5)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-five-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash5")                                                                                                                                                                           |
| Additional Properties                                          | Any    | Optional | can be null    |                                                                                                                                                                                                                                                                                                                            |

### datetime



`datetime`

*   is optional

*   Type: merged type ([datetime associated with this item. If None, a start\_datetime and end\_datetime must be supplied.](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md "aeopres_model#/$defs/Properties/properties/datetime")

#### datetime Type

merged type ([datetime associated with this item. If None, a start\_datetime and end\_datetime must be supplied.](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied-anyof-1.md "check type definition")

### start\_datetime



`start_datetime`

*   is optional

*   Type: merged type ([Optional start datetime, part of common metadata. This value will override any start\_datetime key in properties.](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md "aeopres_model#/$defs/Properties/properties/start_datetime")

#### start\_datetime Type

merged type ([Optional start datetime, part of common metadata. This value will override any start\_datetime key in properties.](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties-anyof-1.md "check type definition")

### end\_datetime



`end_datetime`

*   is optional

*   Type: merged type ([Optional end datetime, part of common metadata. This value will override any end\_datetime key in properties.](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md "aeopres_model#/$defs/Properties/properties/end_datetime")

#### end\_datetime Type

merged type ([Optional end datetime, part of common metadata. This value will override any end\_datetime key in properties.](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties-anyof-1.md "check type definition")

### programme



`programme`

*   is optional

*   Type: merged type ([Name of the programme](model-defs-properties-properties-name-of-the-programme.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-name-of-the-programme.md "aeopres_model#/$defs/Properties/properties/programme")

#### programme Type

merged type ([Name of the programme](model-defs-properties-properties-name-of-the-programme.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-name-of-the-programme-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-name-of-the-programme-anyof-1.md "check type definition")

### constellation



`constellation`

*   is optional

*   Type: merged type ([Name of the constellation](model-defs-properties-properties-name-of-the-constellation.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-name-of-the-constellation.md "aeopres_model#/$defs/Properties/properties/constellation")

#### constellation Type

merged type ([Name of the constellation](model-defs-properties-properties-name-of-the-constellation.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-name-of-the-constellation-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-name-of-the-constellation-anyof-1.md "check type definition")

### instrument



`instrument`

*   is optional

*   Type: merged type ([Name of the instrument](model-defs-properties-properties-name-of-the-instrument.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-name-of-the-instrument.md "aeopres_model#/$defs/Properties/properties/instrument")

#### instrument Type

merged type ([Name of the instrument](model-defs-properties-properties-name-of-the-instrument.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-name-of-the-instrument-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-name-of-the-instrument-anyof-1.md "check type definition")

### sensor



`sensor`

*   is optional

*   Type: merged type ([Name of the sensor](model-defs-properties-properties-name-of-the-sensor.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-name-of-the-sensor.md "aeopres_model#/$defs/Properties/properties/sensor")

#### sensor Type

merged type ([Name of the sensor](model-defs-properties-properties-name-of-the-sensor.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-name-of-the-sensor-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-name-of-the-sensor-anyof-1.md "check type definition")

### sensor\_type



`sensor_type`

*   is optional

*   Type: merged type ([Type of sensor](model-defs-properties-properties-type-of-sensor.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-type-of-sensor.md "aeopres_model#/$defs/Properties/properties/sensor_type")

#### sensor\_type Type

merged type ([Type of sensor](model-defs-properties-properties-type-of-sensor.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-type-of-sensor-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-type-of-sensor-anyof-1.md "check type definition")

### gsd



`gsd`

*   is optional

*   Type: merged type ([Ground Sampling Distance (resolution)](model-defs-properties-properties-ground-sampling-distance-resolution.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-ground-sampling-distance-resolution.md "aeopres_model#/$defs/Properties/properties/gsd")

#### gsd Type

merged type ([Ground Sampling Distance (resolution)](model-defs-properties-properties-ground-sampling-distance-resolution.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-ground-sampling-distance-resolution-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-ground-sampling-distance-resolution-anyof-1.md "check type definition")

### data\_type



`data_type`

*   is optional

*   Type: merged type ([Type of data](model-defs-properties-properties-type-of-data.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-type-of-data.md "aeopres_model#/$defs/Properties/properties/data_type")

#### data\_type Type

merged type ([Type of data](model-defs-properties-properties-type-of-data.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-type-of-data-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-type-of-data-anyof-1.md "check type definition")

### data\_coverage



`data_coverage`

*   is optional

*   Type: merged type ([Estimate of data cover](model-defs-properties-properties-estimate-of-data-cover.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-estimate-of-data-cover.md "aeopres_model#/$defs/Properties/properties/data_coverage")

#### data\_coverage Type

merged type ([Estimate of data cover](model-defs-properties-properties-estimate-of-data-cover.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-estimate-of-data-cover-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-estimate-of-data-cover-anyof-1.md "check type definition")

### water\_coverage



`water_coverage`

*   is optional

*   Type: merged type ([Estimate of water cover](model-defs-properties-properties-estimate-of-water-cover.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-estimate-of-water-cover.md "aeopres_model#/$defs/Properties/properties/water_coverage")

#### water\_coverage Type

merged type ([Estimate of water cover](model-defs-properties-properties-estimate-of-water-cover.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-estimate-of-water-cover-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-estimate-of-water-cover-anyof-1.md "check type definition")

### locations



`locations`

*   is optional

*   Type: merged type ([List of locations covered by the item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md "aeopres_model#/$defs/Properties/properties/locations")

#### locations Type

merged type ([List of locations covered by the item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-list-of-locations-covered-by-the-item-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-list-of-locations-covered-by-the-item-anyof-1.md "check type definition")

### create\_datetime



`create_datetime`

*   is optional

*   Type: merged type ([Date of item creation in the catalog, managed by the ARLAS EO Registration Service](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-eo-registration-service.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-eo-registration-service.md "aeopres_model#/$defs/Properties/properties/create_datetime")

#### create\_datetime Type

merged type ([Date of item creation in the catalog, managed by the ARLAS EO Registration Service](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-eo-registration-service.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-eo-registration-service-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-eo-registration-service-anyof-1.md "check type definition")

### update\_datetime



`update_datetime`

*   is optional

*   Type: merged type ([Update date of the item in the catalog, managed by the ARLAS EO Registration Service](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-eo-registration-service.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-eo-registration-service.md "aeopres_model#/$defs/Properties/properties/update_datetime")

#### update\_datetime Type

merged type ([Update date of the item in the catalog, managed by the ARLAS EO Registration Service](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-eo-registration-service.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-eo-registration-service-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-eo-registration-service-anyof-1.md "check type definition")

### view:off\_nadir



`view:off_nadir`

*   is optional

*   Type: merged type ([The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md "aeopres_model#/$defs/Properties/properties/view:off_nadir")

#### view:off\_nadir Type

merged type ([The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90-anyof-1.md "check type definition")

### view:incidence\_angle



`view:incidence_angle`

*   is optional

*   Type: merged type ([The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight back to the satellite at the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md "aeopres_model#/$defs/Properties/properties/view:incidence_angle")

#### view:incidence\_angle Type

merged type ([The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight back to the satellite at the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90-anyof-1.md "check type definition")

### view:azimuth



`view:azimuth`

*   is optional

*   Type: merged type ([Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform) between the scene center and true north. Measured clockwise from north in degrees (0-360).](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md "aeopres_model#/$defs/Properties/properties/view:azimuth")

#### view:azimuth Type

merged type ([Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform) between the scene center and true north. Measured clockwise from north in degrees (0-360).](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360-anyof-1.md "check type definition")

### sview:un\_azimuth



`sview:un_azimuth`

*   is optional

*   Type: merged type ([Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun. Measured clockwise in degrees (0-360).](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md "aeopres_model#/$defs/Properties/properties/sview:un_azimuth")

#### sview:un\_azimuth Type

merged type ([Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun. Measured clockwise in degrees (0-360).](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360-anyof-1.md "check type definition")

### view:sun\_elevation



`view:sun_elevation`

*   is optional

*   Type: merged type ([Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° \[...\]](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md "aeopres_model#/$defs/Properties/properties/view:sun_elevation")

#### view:sun\_elevation Type

merged type ([Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° \[...\]](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10--anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10--anyof-1.md "check type definition")

### storage:requester\_pays



`storage:requester_pays`

*   is optional

*   Type: merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "aeopres_model#/$defs/Properties/properties/storage:requester_pays")

#### storage:requester\_pays Type

merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-1.md "check type definition")

### storage:tier



`storage:tier`

*   is optional

*   Type: merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "aeopres_model#/$defs/Properties/properties/storage:tier")

#### storage:tier Type

merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-1.md "check type definition")

### storage:platform



`storage:platform`

*   is optional

*   Type: merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "aeopres_model#/$defs/Properties/properties/storage:platform")

#### storage:platform Type

merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-1.md "check type definition")

### storage:region



`storage:region`

*   is optional

*   Type: merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "aeopres_model#/$defs/Properties/properties/storage:region")

#### storage:region Type

merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-1.md "check type definition")

### eo:cloud\_cover



`eo:cloud_cover`

*   is optional

*   Type: merged type ([Estimate of cloud cover.](model-defs-properties-properties-estimate-of-cloud-cover.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-estimate-of-cloud-cover.md "aeopres_model#/$defs/Properties/properties/eo:cloud_cover")

#### eo:cloud\_cover Type

merged type ([Estimate of cloud cover.](model-defs-properties-properties-estimate-of-cloud-cover.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-estimate-of-cloud-cover-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-estimate-of-cloud-cover-anyof-1.md "check type definition")

### eo:snow\_cover



`eo:snow_cover`

*   is optional

*   Type: merged type ([Estimate of snow and ice cover.](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md "aeopres_model#/$defs/Properties/properties/eo:snow_cover")

#### eo:snow\_cover Type

merged type ([Estimate of snow and ice cover.](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover-anyof-1.md "check type definition")

### eo:bands



`eo:bands`

*   is optional

*   Type: merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "aeopres_model#/$defs/Properties/properties/eo:bands")

#### eo:bands Type

merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-1.md "check type definition")

### processing:expression



`processing:expression`

*   is optional

*   Type: merged type ([An expression or processing chain that describes how the data has been processed. Alternatively, you can also link to a processing chain with the relation type processing-expression (see below).](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md "aeopres_model#/$defs/Properties/properties/processing:expression")

#### processing:expression Type

merged type ([An expression or processing chain that describes how the data has been processed. Alternatively, you can also link to a processing chain with the relation type processing-expression (see below).](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below-anyof-1.md "check type definition")

### processing:lineage



`processing:lineage`

*   is optional

*   Type: merged type ([Lineage Information provided as free text information about the how observations were processed or models that were used to create the resource being described NASA ISO.](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md "aeopres_model#/$defs/Properties/properties/processing:lineage")

#### processing:lineage Type

merged type ([Lineage Information provided as free text information about the how observations were processed or models that were used to create the resource being described NASA ISO.](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso-anyof-1.md "check type definition")

### processing:level



`processing:level`

*   is optional

*   Type: merged type ([The name commonly used to refer to the processing level to make it easier to search for product level across collections or items. The short name must be used (only L, not Level).](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md "aeopres_model#/$defs/Properties/properties/processing:level")

#### processing:level Type

merged type ([The name commonly used to refer to the processing level to make it easier to search for product level across collections or items. The short name must be used (only L, not Level).](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level-anyof-1.md "check type definition")

### processing:facility



`processing:facility`

*   is optional

*   Type: merged type ([The name of the facility that produced the data. For example, Copernicus S1 Core Ground Segment - DPA for product of Sentinel-1 satellites.](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md "aeopres_model#/$defs/Properties/properties/processing:facility")

#### processing:facility Type

merged type ([The name of the facility that produced the data. For example, Copernicus S1 Core Ground Segment - DPA for product of Sentinel-1 satellites.](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites-anyof-1.md "check type definition")

### processing:software



`processing:software`

*   is optional

*   Type: merged type ([A dictionary with name/version for key/value describing one or more softwares that produced the data.](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md "aeopres_model#/$defs/Properties/properties/processing:software")

#### processing:software Type

merged type ([A dictionary with name/version for key/value describing one or more softwares that produced the data.](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md))

any of

*   [Untitled object in Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data-anyof-1.md "check type definition")

### dc3:quality\_indicators



`dc3:quality_indicators`

*   is optional

*   Type: merged type ([Set of indicators for estimating the quality of the datacube based on the composition. The indicators are group based. A cube indicator is the product of its corresponding group indicator.](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md "aeopres_model#/$defs/Properties/properties/dc3:quality_indicators")

#### dc3:quality\_indicators Type

merged type ([Set of indicators for estimating the quality of the datacube based on the composition. The indicators are group based. A cube indicator is the product of its corresponding group indicator.](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md))

any of

*   [Indicators](model-defs-indicators.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator-anyof-1.md "check type definition")

### dc3:composition



`dc3:composition`

*   is optional

*   Type: merged type ([List of raster groups used for elaborating the cube temporal slices.](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md "aeopres_model#/$defs/Properties/properties/dc3:composition")

#### dc3:composition Type

merged type ([List of raster groups used for elaborating the cube temporal slices.](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices-anyof-1.md "check type definition")

### dc3:number\_of\_chunks



`dc3:number_of_chunks`

*   is optional

*   Type: merged type ([Number of chunks (if zarr or similar partitioned format) within the cube.](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md "aeopres_model#/$defs/Properties/properties/dc3:number_of_chunks")

#### dc3:number\_of\_chunks Type

merged type ([Number of chunks (if zarr or similar partitioned format) within the cube.](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube-anyof-1.md "check type definition")

### dc3:chunk\_weight



`dc3:chunk_weight`

*   is optional

*   Type: merged type ([Weight of a chunk (number of bytes).](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md "aeopres_model#/$defs/Properties/properties/dc3:chunk_weight")

#### dc3:chunk\_weight Type

merged type ([Weight of a chunk (number of bytes).](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes-anyof-1.md "check type definition")

### dc3:fill\_ratio



`dc3:fill_ratio`

*   is optional

*   Type: merged type ([1: the cube is full, 0 the cube is empty, in between the cube is partially filled.](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md "aeopres_model#/$defs/Properties/properties/dc3:fill_ratio")

#### dc3:fill\_ratio Type

merged type ([1: the cube is full, 0 the cube is empty, in between the cube is partially filled.](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled-anyof-1.md "check type definition")

### cube:dimensions



`cube:dimensions`

*   is optional

*   Type: merged type ([Uniquely named dimensions of the datacube.](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md "aeopres_model#/$defs/Properties/properties/cube:dimensions")

#### cube:dimensions Type

merged type ([Uniquely named dimensions of the datacube.](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md))

any of

*   [Untitled object in Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube-anyof-1.md "check type definition")

### cube:variables



`cube:variables`

*   is optional

*   Type: merged type ([Uniquely named variables of the datacube.](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md "aeopres_model#/$defs/Properties/properties/cube:variables")

#### cube:variables Type

merged type ([Uniquely named variables of the datacube.](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md))

any of

*   [Untitled object in Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube-anyof-1.md "check type definition")

### sar:instrument\_mode



`sar:instrument_mode`

*   is optional

*   Type: merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "aeopres_model#/$defs/Properties/properties/sar:instrument_mode")

#### sar:instrument\_mode Type

merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-1.md "check type definition")

### sar:frequency\_band



`sar:frequency_band`

*   is optional

*   Type: merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "aeopres_model#/$defs/Properties/properties/sar:frequency_band")

#### sar:frequency\_band Type

merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-1.md "check type definition")

### sar:center\_frequency



`sar:center_frequency`

*   is optional

*   Type: merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "aeopres_model#/$defs/Properties/properties/sar:center_frequency")

#### sar:center\_frequency Type

merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-1.md "check type definition")

### sar:polarizations



`sar:polarizations`

*   is optional

*   Type: merged type ([Any combination of polarizations.](model-defs-properties-properties-any-combination-of-polarizations.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-any-combination-of-polarizations.md "aeopres_model#/$defs/Properties/properties/sar:polarizations")

#### sar:polarizations Type

merged type ([Any combination of polarizations.](model-defs-properties-properties-any-combination-of-polarizations.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-any-combination-of-polarizations-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-any-combination-of-polarizations-anyof-1.md "check type definition")

### sar:product\_type



`sar:product_type`

*   is optional

*   Type: merged type ([The product type, for example SSC, MGD, or SGC](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "aeopres_model#/$defs/Properties/properties/sar:product_type")

#### sar:product\_type Type

merged type ([The product type, for example SSC, MGD, or SGC](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-1.md "check type definition")

### sar:resolution\_range



`sar:resolution_range`

*   is optional

*   Type: merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Properties/properties/sar:resolution_range")

#### sar:resolution\_range Type

merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

### sar:resolution\_azimuth



`sar:resolution_azimuth`

*   is optional

*   Type: merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "aeopres_model#/$defs/Properties/properties/sar:resolution_azimuth")

#### sar:resolution\_azimuth Type

merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

### sar:pixel\_spacing\_range



`sar:pixel_spacing_range`

*   is optional

*   Type: merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Properties/properties/sar:pixel_spacing_range")

#### sar:pixel\_spacing\_range Type

merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

### sar:pixel\_spacing\_azimuth



`sar:pixel_spacing_azimuth`

*   is optional

*   Type: merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "aeopres_model#/$defs/Properties/properties/sar:pixel_spacing_azimuth")

#### sar:pixel\_spacing\_azimuth Type

merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

### sar:looks\_range



`sar:looks_range`

*   is optional

*   Type: merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "aeopres_model#/$defs/Properties/properties/sar:looks_range")

#### sar:looks\_range Type

merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-1.md "check type definition")

### sar:looks\_azimuth



`sar:looks_azimuth`

*   is optional

*   Type: merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "aeopres_model#/$defs/Properties/properties/sar:looks_azimuth")

#### sar:looks\_azimuth Type

merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-1.md "check type definition")

### sar:looks\_equivalent\_number



`sar:looks_equivalent_number`

*   is optional

*   Type: merged type ([The equivalent number of looks (ENL).](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md "aeopres_model#/$defs/Properties/properties/sar:looks_equivalent_number")

#### sar:looks\_equivalent\_number Type

merged type ([The equivalent number of looks (ENL).](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md))

any of

*   [Untitled number in Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl-anyof-1.md "check type definition")

### sar:observation\_direction



`sar:observation_direction`

*   is optional

*   Type: merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "aeopres_model#/$defs/Properties/properties/sar:observation_direction")

#### sar:observation\_direction Type

merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-1.md "check type definition")

### proj:epsg



`proj:epsg`

*   is optional

*   Type: merged type ([EPSG code of the datasource.](model-defs-properties-properties-epsg-code-of-the-datasource.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-epsg-code-of-the-datasource.md "aeopres_model#/$defs/Properties/properties/proj:epsg")

#### proj:epsg Type

merged type ([EPSG code of the datasource.](model-defs-properties-properties-epsg-code-of-the-datasource.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-epsg-code-of-the-datasource-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-epsg-code-of-the-datasource-anyof-1.md "check type definition")

### proj:wkt2



`proj:wkt2`

*   is optional

*   Type: merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "aeopres_model#/$defs/Properties/properties/proj:wkt2")

#### proj:wkt2 Type

merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-1.md "check type definition")

### proj:geometry



`proj:geometry`

*   is optional

*   Type: merged type ([Defines the footprint of this Item.](model-defs-properties-properties-defines-the-footprint-of-this-item.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-defines-the-footprint-of-this-item.md "aeopres_model#/$defs/Properties/properties/proj:geometry")

#### proj:geometry Type

merged type ([Defines the footprint of this Item.](model-defs-properties-properties-defines-the-footprint-of-this-item.md))

any of

*   [Untitled undefined type in Item](model-defs-properties-properties-defines-the-footprint-of-this-item-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-defines-the-footprint-of-this-item-anyof-1.md "check type definition")

### proj:bbox



`proj:bbox`

*   is optional

*   Type: merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "aeopres_model#/$defs/Properties/properties/proj:bbox")

#### proj:bbox Type

merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-1.md "check type definition")

### proj:centroid



`proj:centroid`

*   is optional

*   Type: merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "aeopres_model#/$defs/Properties/properties/proj:centroid")

#### proj:centroid Type

merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

any of

*   [Untitled undefined type in Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-1.md "check type definition")

### proj:shape



`proj:shape`

*   is optional

*   Type: merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "aeopres_model#/$defs/Properties/properties/proj:shape")

#### proj:shape Type

merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-1.md "check type definition")

### proj:transform



`proj:transform`

*   is optional

*   Type: merged type ([The affine transformation coefficients for the default grid.](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md "aeopres_model#/$defs/Properties/properties/proj:transform")

#### proj:transform Type

merged type ([The affine transformation coefficients for the default grid.](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-1.md "check type definition")

### generated:has\_overview



`generated:has_overview`

*   is optional

*   Type: merged type ([Whether the item has an overview or not.](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_overview")

#### generated:has\_overview Type

merged type ([Whether the item has an overview or not.](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not-anyof-1.md "check type definition")

### generated:has\_thumbnail



`generated:has_thumbnail`

*   is optional

*   Type: merged type ([Whether the item has a thumbnail or not.](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_thumbnail")

#### generated:has\_thumbnail Type

merged type ([Whether the item has a thumbnail or not.](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not-anyof-1.md "check type definition")

### generated:has\_metadata



`generated:has_metadata`

*   is optional

*   Type: merged type ([Whether the item has a metadata file or not.](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_metadata")

#### generated:has\_metadata Type

merged type ([Whether the item has a metadata file or not.](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not-anyof-1.md "check type definition")

### generated:has\_data



`generated:has_data`

*   is optional

*   Type: merged type ([Whether the item has a data file or not.](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_data")

#### generated:has\_data Type

merged type ([Whether the item has a data file or not.](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not-anyof-1.md "check type definition")

### generated:has\_cog



`generated:has_cog`

*   is optional

*   Type: merged type ([Whether the item has a cog or not.](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_cog")

#### generated:has\_cog Type

merged type ([Whether the item has a cog or not.](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not-anyof-1.md "check type definition")

### generated:has\_zarr



`generated:has_zarr`

*   is optional

*   Type: merged type ([Whether the item has a zarr or not.](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md "aeopres_model#/$defs/Properties/properties/generated:has_zarr")

#### generated:has\_zarr Type

merged type ([Whether the item has a zarr or not.](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md))

any of

*   [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not-anyof-1.md "check type definition")

### generated:date\_keywords



`generated:date_keywords`

*   is optional

*   Type: merged type ([A list of keywords indicating clues on the date](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md "aeopres_model#/$defs/Properties/properties/generated:date_keywords")

#### generated:date\_keywords Type

merged type ([A list of keywords indicating clues on the date](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date-anyof-1.md "check type definition")

### generated:day\_of\_week



`generated:day_of_week`

*   is optional

*   Type: merged type ([Day of week.](model-defs-properties-properties-day-of-week.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-day-of-week.md "aeopres_model#/$defs/Properties/properties/generated:day_of_week")

#### generated:day\_of\_week Type

merged type ([Day of week.](model-defs-properties-properties-day-of-week.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-day-of-week-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-day-of-week-anyof-1.md "check type definition")

### generated:day\_of\_year



`generated:day_of_year`

*   is optional

*   Type: merged type ([Day of year.](model-defs-properties-properties-day-of-year.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-day-of-year.md "aeopres_model#/$defs/Properties/properties/generated:day_of_year")

#### generated:day\_of\_year Type

merged type ([Day of year.](model-defs-properties-properties-day-of-year.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-day-of-year-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-day-of-year-anyof-1.md "check type definition")

### generated:hour\_of\_day



`generated:hour_of_day`

*   is optional

*   Type: merged type ([Hour of day.](model-defs-properties-properties-hour-of-day.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-hour-of-day.md "aeopres_model#/$defs/Properties/properties/generated:hour_of_day")

#### generated:hour\_of\_day Type

merged type ([Hour of day.](model-defs-properties-properties-hour-of-day.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-hour-of-day-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-hour-of-day-anyof-1.md "check type definition")

### generated:minute\_of\_day



`generated:minute_of_day`

*   is optional

*   Type: merged type ([Minute of day.](model-defs-properties-properties-minute-of-day.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-minute-of-day.md "aeopres_model#/$defs/Properties/properties/generated:minute_of_day")

#### generated:minute\_of\_day Type

merged type ([Minute of day.](model-defs-properties-properties-minute-of-day.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-minute-of-day-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-minute-of-day-anyof-1.md "check type definition")

### generated:month



`generated:month`

*   is optional

*   Type: merged type ([Month](model-defs-properties-properties-month.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-month.md "aeopres_model#/$defs/Properties/properties/generated:month")

#### generated:month Type

merged type ([Month](model-defs-properties-properties-month.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-month-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-month-anyof-1.md "check type definition")

### generated:year



`generated:year`

*   is optional

*   Type: merged type ([Year](model-defs-properties-properties-year.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-year.md "aeopres_model#/$defs/Properties/properties/generated:year")

#### generated:year Type

merged type ([Year](model-defs-properties-properties-year.md))

any of

*   [Untitled integer in Item](model-defs-properties-properties-year-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-year-anyof-1.md "check type definition")

### generated:season



`generated:season`

*   is optional

*   Type: merged type ([Season](model-defs-properties-properties-season.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-season.md "aeopres_model#/$defs/Properties/properties/generated:season")

#### generated:season Type

merged type ([Season](model-defs-properties-properties-season.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-season-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-season-anyof-1.md "check type definition")

### generated:tltrbrbl



`generated:tltrbrbl`

*   is optional

*   Type: merged type ([The coordinates of the top left, top right, bottom right, bottom left corners of the item.](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md "aeopres_model#/$defs/Properties/properties/generated:tltrbrbl")

#### generated:tltrbrbl Type

merged type ([The coordinates of the top left, top right, bottom right, bottom left corners of the item.](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item-anyof-1.md "check type definition")

### generated:band\_common\_names



`generated:band_common_names`

*   is optional

*   Type: merged type ([List of the band common names.](model-defs-properties-properties-list-of-the-band-common-names.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-list-of-the-band-common-names.md "aeopres_model#/$defs/Properties/properties/generated:band_common_names")

#### generated:band\_common\_names Type

merged type ([List of the band common names.](model-defs-properties-properties-list-of-the-band-common-names.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-list-of-the-band-common-names-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-list-of-the-band-common-names-anyof-1.md "check type definition")

### generated:band\_names



`generated:band_names`

*   is optional

*   Type: merged type ([List of the band names.](model-defs-properties-properties-list-of-the-band-names.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-list-of-the-band-names.md "aeopres_model#/$defs/Properties/properties/generated:band_names")

#### generated:band\_names Type

merged type ([List of the band names.](model-defs-properties-properties-list-of-the-band-names.md))

any of

*   [Untitled array in Item](model-defs-properties-properties-list-of-the-band-names-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-list-of-the-band-names-anyof-1.md "check type definition")

### generated:geohash2



`generated:geohash2`

*   is optional

*   Type: merged type ([Geohash on the first two characters.](model-defs-properties-properties-geohash-on-the-first-two-characters.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-geohash-on-the-first-two-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash2")

#### generated:geohash2 Type

merged type ([Geohash on the first two characters.](model-defs-properties-properties-geohash-on-the-first-two-characters.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-two-characters-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-two-characters-anyof-1.md "check type definition")

### generated:geohash3



`generated:geohash3`

*   is optional

*   Type: merged type ([Geohash on the first three characters.](model-defs-properties-properties-geohash-on-the-first-three-characters.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-geohash-on-the-first-three-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash3")

#### generated:geohash3 Type

merged type ([Geohash on the first three characters.](model-defs-properties-properties-geohash-on-the-first-three-characters.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-three-characters-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-three-characters-anyof-1.md "check type definition")

### generated:geohash4



`generated:geohash4`

*   is optional

*   Type: merged type ([Geohash on the first four characters.](model-defs-properties-properties-geohash-on-the-first-four-characters.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-geohash-on-the-first-four-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash4")

#### generated:geohash4 Type

merged type ([Geohash on the first four characters.](model-defs-properties-properties-geohash-on-the-first-four-characters.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-four-characters-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-four-characters-anyof-1.md "check type definition")

### generated:geohash5



`generated:geohash5`

*   is optional

*   Type: merged type ([Geohash on the first five characters.](model-defs-properties-properties-geohash-on-the-first-five-characters.md))

*   cannot be null

*   defined in: [Item](model-defs-properties-properties-geohash-on-the-first-five-characters.md "aeopres_model#/$defs/Properties/properties/generated:geohash5")

#### generated:geohash5 Type

merged type ([Geohash on the first five characters.](model-defs-properties-properties-geohash-on-the-first-five-characters.md))

any of

*   [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-five-characters-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-five-characters-anyof-1.md "check type definition")

### Additional Properties

Additional properties are allowed and do not have to follow a specific schema

## Definitions group Raster

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/Raster"}
```

| Property        | Type     | Required | Nullable       | Defined by                                                                                 |
| :-------------- | :------- | :------- | :------------- | :----------------------------------------------------------------------------------------- |
| [type](#type-1) | `object` | Required | cannot be null | [Item](model-defs-rastertype.md "aeopres_model#/$defs/Raster/properties/type")             |
| [path](#path)   | `string` | Required | cannot be null | [Item](model-defs-raster-properties-path.md "aeopres_model#/$defs/Raster/properties/path") |
| [id](#id-1)     | `string` | Required | cannot be null | [Item](model-defs-raster-properties-id.md "aeopres_model#/$defs/Raster/properties/id")     |

### type



`type`

*   is required

*   Type: `object` ([RasterType](model-defs-rastertype.md))

*   cannot be null

*   defined in: [Item](model-defs-rastertype.md "aeopres_model#/$defs/Raster/properties/type")

#### type Type

`object` ([RasterType](model-defs-rastertype.md))

### path



`path`

*   is required

*   Type: `string` ([Path](model-defs-raster-properties-path.md))

*   cannot be null

*   defined in: [Item](model-defs-raster-properties-path.md "aeopres_model#/$defs/Raster/properties/path")

#### path Type

`string` ([Path](model-defs-raster-properties-path.md))

### id



`id`

*   is required

*   Type: `string` ([Id](model-defs-raster-properties-id.md))

*   cannot be null

*   defined in: [Item](model-defs-raster-properties-id.md "aeopres_model#/$defs/Raster/properties/id")

#### id Type

`string` ([Id](model-defs-raster-properties-id.md))

## Definitions group RasterType

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/RasterType"}
```

| Property          | Type     | Required | Nullable       | Defined by                                                                                             |
| :---------------- | :------- | :------- | :------------- | :----------------------------------------------------------------------------------------------------- |
| [source](#source) | `string` | Required | cannot be null | [Item](model-defs-rastertype-properties-source.md "aeopres_model#/$defs/RasterType/properties/source") |
| [format](#format) | `string` | Required | cannot be null | [Item](model-defs-rastertype-properties-format.md "aeopres_model#/$defs/RasterType/properties/format") |

### source



`source`

*   is required

*   Type: `string` ([Source](model-defs-rastertype-properties-source.md))

*   cannot be null

*   defined in: [Item](model-defs-rastertype-properties-source.md "aeopres_model#/$defs/RasterType/properties/source")

#### source Type

`string` ([Source](model-defs-rastertype-properties-source.md))

### format



`format`

*   is required

*   Type: `string` ([Format](model-defs-rastertype-properties-format.md))

*   cannot be null

*   defined in: [Item](model-defs-rastertype-properties-format.md "aeopres_model#/$defs/RasterType/properties/format")

#### format Type

`string` ([Format](model-defs-rastertype-properties-format.md))

## Definitions group VariableType

Reference this group by using

```json
{"$ref":"aeopres_model#/$defs/VariableType"}
```

| Property | Type | Required | Nullable | Defined by |
| :------- | :--- | :------- | :------- | :--------- |
