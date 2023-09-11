# Indicators Schema

```txt
airs_model#/$defs/Properties/properties/dc3__quality_indicators/anyOf/0
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                                |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :------------------------------------------------------------------------ |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json\*](../../out/model.schema.json "open original schema") |

## 0 Type

`object` ([Indicators](model-defs-indicators.md))

# 0 Properties

| Property                               | Type   | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                                  |
| :------------------------------------- | :----- | :------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [time\_compacity](#time_compacity)     | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md "airs_model#/$defs/Indicators/properties/time_compacity") |
| [spatial\_coverage](#spatial_coverage) | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md "airs_model#/$defs/Indicators/properties/spatial_coverage")                                  |
| [group\_lightness](#group_lightness)   | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md "airs_model#/$defs/Indicators/properties/group_lightness")             |
| [time\_regularity](#time_regularity)   | Merged | Optional | cannot be null | [Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md "airs_model#/$defs/Indicators/properties/time_regularity")                              |

## time\_compacity



`time_compacity`

*   is optional

*   Type: merged type ([Indicates whether the temporal extend of the temporal slices (groups) are compact or not compared to the cube temporal extend. Computed as follow: 1-range(group rasters) / range(cube rasters).](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md "airs_model#/$defs/Indicators/properties/time_compacity")

### time\_compacity Type

merged type ([Indicates whether the temporal extend of the temporal slices (groups) are compact or not compared to the cube temporal extend. Computed as follow: 1-range(group rasters) / range(cube rasters).](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-whether-the-temporal-extend-of-the-temporal-slices-groups-are-compact-or-not-compared-to-the-cube-temporal-extend-computed-as-follow-1-rangegroup-rasters--rangecube-rasters-anyof-1.md "check type definition")

## spatial\_coverage



`spatial_coverage`

*   is optional

*   Type: merged type ([Indicates the proportion of the region of interest that is covered by the input rasters. Computed as follow: area(intersection(union(rasters),roi)) / area(roi))](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md "airs_model#/$defs/Indicators/properties/spatial_coverage")

### spatial\_coverage Type

merged type ([Indicates the proportion of the region of interest that is covered by the input rasters. Computed as follow: area(intersection(union(rasters),roi)) / area(roi))](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-the-proportion-of-the-region-of-interest-that-is-covered-by-the-input-rasters-computed-as-follow-areaintersectionunionrastersroi--arearoi-anyof-1.md "check type definition")

## group\_lightness



`group_lightness`

*   is optional

*   Type: merged type ([Indicates the proportion of non overlapping regions between the different input rasters. Computed as follow: area(intersection(union(rasters),roi)) / sum(area(intersection(raster, roi)))](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md "airs_model#/$defs/Indicators/properties/group_lightness")

### group\_lightness Type

merged type ([Indicates the proportion of non overlapping regions between the different input rasters. Computed as follow: area(intersection(union(rasters),roi)) / sum(area(intersection(raster, roi)))](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-the-proportion-of-non-overlapping-regions-between-the-different-input-rasters-computed-as-follow-areaintersectionunionrastersroi--sumareaintersectionraster-roi-anyof-1.md "check type definition")

## time\_regularity



`time_regularity`

*   is optional

*   Type: merged type ([Indicates the regularity of the extends between the temporal slices (groups). Computed as follow: 1-std(inter group temporal gaps)/avg(inter group temporal gaps)](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md))

*   cannot be null

*   defined in: [Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md "airs_model#/$defs/Indicators/properties/time_regularity")

### time\_regularity Type

merged type ([Indicates the regularity of the extends between the temporal slices (groups). Computed as follow: 1-std(inter group temporal gaps)/avg(inter group temporal gaps)](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps.md))

any of

*   [Untitled number in Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps-anyof-0.md "check type definition")

*   [Untitled null in Item](model-defs-indicators-properties-indicates-the-regularity-of-the-extends-between-the-temporal-slices-groups-computed-as-follow-1-stdinter-group-temporal-gapsavginter-group-temporal-gaps-anyof-1.md "check type definition")
