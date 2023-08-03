# Group Schema

```txt
aeopres_model#/$defs/Properties/properties/dc3:composition/anyOf/0/items
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## items Type

`object` ([Group](model-defs-group.md))

# items Properties

| Property                                   | Type   | Required | Nullable       | Defined by                                                                                                                                                                                          |
| :----------------------------------------- | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [timestamp](#timestamp)                    | Merged | Optional | cannot be null | [Item](model-defs-group-properties-the-timestamp-of-this-temporal-group.md "aeopres_model#/$defs/Group/properties/timestamp")                                                                       |
| [rasters](#rasters)                        | Merged | Optional | cannot be null | [Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md "aeopres_model#/$defs/Group/properties/rasters")                                                                 |
| [quality\_indicators](#quality_indicators) | Merged | Optional | cannot be null | [Item](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md "aeopres_model#/$defs/Group/properties/quality_indicators") |

## timestamp



`timestamp`

*   is optional

*   Type: merged type ([The timestamp of this temporal group.](model-defs-group-properties-the-timestamp-of-this-temporal-group.md))

*   cannot be null

*   defined in: [Item](model-defs-group-properties-the-timestamp-of-this-temporal-group.md "aeopres_model#/$defs/Group/properties/timestamp")

### timestamp Type

merged type ([The timestamp of this temporal group.](model-defs-group-properties-the-timestamp-of-this-temporal-group.md))

any of

*   [Untitled integer in Item](model-defs-group-properties-the-timestamp-of-this-temporal-group-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-group-properties-the-timestamp-of-this-temporal-group-anyof-1.md "check type definition")

## rasters



`rasters`

*   is optional

*   Type: merged type ([The rasters belonging to this temporal group.](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md))

*   cannot be null

*   defined in: [Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md "aeopres_model#/$defs/Group/properties/rasters")

### rasters Type

merged type ([The rasters belonging to this temporal group.](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group.md))

any of

*   [Untitled array in Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-group-properties-the-rasters-belonging-to-this-temporal-group-anyof-1.md "check type definition")

## quality\_indicators



`quality_indicators`

*   is optional

*   Type: merged type ([Set of indicators for estimating the quality of the datacube group. The indicators are group based.](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md))

*   cannot be null

*   defined in: [Item](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md "aeopres_model#/$defs/Group/properties/quality_indicators")

### quality\_indicators Type

merged type ([Set of indicators for estimating the quality of the datacube group. The indicators are group based.](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based.md))

any of

*   [Indicators](model-defs-indicators.md "check type definition")

*   [Untitled null in Item](model-defs-group-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-group-the-indicators-are-group-based-anyof-1.md "check type definition")
