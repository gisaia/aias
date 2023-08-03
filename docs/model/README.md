# README

## Top-level Schemas

*   [Item](./model.md) – `aeopres_model`

## Other Schemas

### Objects

*   [Asset](./model-defs-asset.md) – `aeopres_model#/$defs/Asset`

*   [Band](./model-defs-band.md) – `aeopres_model#/$defs/Band`

*   [Group](./model-defs-group.md) – `aeopres_model#/$defs/Group`

*   [Indicators](./model-defs-indicators.md) – `aeopres_model#/$defs/Indicators`

*   [Properties](./model-defs-properties.md) – `aeopres_model#/$defs/Properties`

*   [Raster](./model-defs-raster.md) – `aeopres_model#/$defs/Raster`

*   [RasterType](./model-defs-rastertype.md) – `aeopres_model#/$defs/RasterType`

*   [Untitled object in Item](./model-defs-asset-properties-optional-additional-fields-for-this-asset-this-is-used-by-extensions-as-a-way-to-serialize-and-deserialize-properties-on-asset-object-json-anyof-0.md) – `aeopres_model#/$defs/Asset/properties/extra_fields/anyOf/0`

*   [Untitled object in Item](./model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/processing:software/anyOf/0`

*   [Untitled object in Item](./model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/cube:dimensions/anyOf/0`

*   [Untitled object in Item](./model-defs-properties-properties-uniquely-named-variables-of-the-datacube-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/cube:variables/anyOf/0`

*   [Untitled object in Item](./model-properties-defines-the-full-footprint-of-the-asset-represented-by-this-item-formatted-according-to-rfc-7946-section-31-geojson-httpstoolsietforghtmlrfc7946_-anyof-0.md) – `aeopres_model#/properties/geometry/anyOf/0`

*   [Untitled object in Item](./model-properties-a-dictionary-mapping-string-keys-to-asset-objects-all-asset-values-in-the-dictionary-will-have-their-owner-attribute-set-to-the-created-item-anyof-0.md) – `aeopres_model#/properties/assets/anyOf/0`

### Arrays

*   [Untitled array in Item](./model-defs-asset-properties-optional-semantic-roles-ie-thumbnail-overview-data-metadata-of-the-asset-anyof-0.md) – `aeopres_model#/$defs/Asset/properties/roles/anyOf/0`

*   [Untitled array in Item](./model-defs-asset-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-0.md) – `aeopres_model#/$defs/Asset/properties/eo:bands/anyOf/0`

*   [Untitled array in Item](./model-defs-asset-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-0.md) – `aeopres_model#/$defs/Asset/properties/proj:bbox/anyOf/0`

*   [Untitled array in Item](./model-defs-asset-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-0.md) – `aeopres_model#/$defs/Asset/properties/proj:shape/anyOf/0`

*   [Untitled array in Item](./model-defs-asset-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-0.md) – `aeopres_model#/$defs/Asset/properties/proj:transform/anyOf/0`

*   [Untitled array in Item](./model-defs-group-properties-the-rasters-belonging-to-this-temporal-group-anyof-0.md) – `aeopres_model#/$defs/Group/properties/rasters/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-list-of-locations-covered-by-the-item-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/locations/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/eo:bands/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/dc3:composition/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/proj:bbox/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/proj:shape/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/proj:transform/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/generated:date_keywords/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/generated:tltrbrbl/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item-anyof-0-items.md) – `aeopres_model#/$defs/Properties/properties/generated:tltrbrbl/anyOf/0/items`

*   [Untitled array in Item](./model-defs-properties-properties-list-of-the-band-common-names-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/generated:band_common_names/anyOf/0`

*   [Untitled array in Item](./model-defs-properties-properties-list-of-the-band-names-anyof-0.md) – `aeopres_model#/$defs/Properties/properties/generated:band_names/anyOf/0`

*   [Untitled array in Item](./model-properties-bounding-box-of-the-asset-represented-by-this-item-using-either-2d-or-3d-geometries-the-length-of-the-array-must-be-2n-where-n-is-the-number-of-dimensions-could-also-be-none-in-the-case-of-a-null-geometry-anyof-0.md) – `aeopres_model#/properties/bbox/anyOf/0`

*   [Untitled array in Item](./model-properties-coordinates-latlon-of-the-geometrys-centroid-anyof-0.md) – `aeopres_model#/properties/centroid/anyOf/0`
