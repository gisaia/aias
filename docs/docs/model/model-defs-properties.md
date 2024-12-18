# Properties Schema

```txt
airs_model#/properties/properties/anyOf/0
```



| Abstract            | Extensible | Status         | Identifiable | Custom Properties | Additional Properties | Access Restrictions | Defined In                                                      |
| :------------------ | :--------- | :------------- | :----------- | :---------------- | :-------------------- | :------------------ | :-------------------------------------------------------------- |
| Can be instantiated | No         | Unknown status | No           | Forbidden         | Allowed               | none                | [model.schema.json\*](model.schema.json "open original schema") |

## 0 Type

`object` ([Properties](model-defs-properties.md))

# 0 Properties

| Property                                                                  | Type   | Required | Nullable       | Defined by                                                                                                                                                                                                                                                                                                               |
| :------------------------------------------------------------------------ | :----- | :------- | :------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [datetime](#datetime)                                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md "airs_model#/$defs/Properties/properties/datetime")                                                                                                                             |
| [start\_datetime](#start_datetime)                                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md "airs_model#/$defs/Properties/properties/start_datetime")                                                                                                       |
| [end\_datetime](#end_datetime)                                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md "airs_model#/$defs/Properties/properties/end_datetime")                                                                                                             |
| [keywords](#keywords)                                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-a-list-of-keywords.md "airs_model#/$defs/Properties/properties/keywords")                                                                                                                                                                                                        |
| [programme](#programme)                                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-programme.md "airs_model#/$defs/Properties/properties/programme")                                                                                                                                                                                                    |
| [constellation](#constellation)                                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-constellation.md "airs_model#/$defs/Properties/properties/constellation")                                                                                                                                                                                            |
| [satellite](#satellite)                                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-satellite.md "airs_model#/$defs/Properties/properties/satellite")                                                                                                                                                                                                    |
| [platform](#platform)                                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-satellite-platform.md "airs_model#/$defs/Properties/properties/platform")                                                                                                                                                                                            |
| [instrument](#instrument)                                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-instrument.md "airs_model#/$defs/Properties/properties/instrument")                                                                                                                                                                                                  |
| [sensor](#sensor)                                                         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-sensor.md "airs_model#/$defs/Properties/properties/sensor")                                                                                                                                                                                                          |
| [sensor\_mode](#sensor_mode)                                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-mode-of-the-sensor-during-acquisition.md "airs_model#/$defs/Properties/properties/sensor_mode")                                                                                                                                                                                  |
| [sensor\_type](#sensor_type)                                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-type-of-sensor.md "airs_model#/$defs/Properties/properties/sensor_type")                                                                                                                                                                                                         |
| [annotations](#annotations)                                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-human-annotations-for-the-item.md "airs_model#/$defs/Properties/properties/annotations")                                                                                                                                                                                         |
| [gsd](#gsd)                                                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-ground-sampling-distance-resolution.md "airs_model#/$defs/Properties/properties/gsd")                                                                                                                                                                                            |
| [secondary\_id](#secondary_id)                                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-secondary-identifier.md "airs_model#/$defs/Properties/properties/secondary_id")                                                                                                                                                                                                  |
| [data\_type](#data_type)                                                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-type-of-data.md "airs_model#/$defs/Properties/properties/data_type")                                                                                                                                                                                                             |
| [item\_type](#item_type)                                                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-type-of-data-resourcetype.md "airs_model#/$defs/Properties/properties/item_type")                                                                                                                                                                                                |
| [item\_format](#item_format)                                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-data-format-itemformat.md "airs_model#/$defs/Properties/properties/item_format")                                                                                                                                                                                                 |
| [main\_asset\_format](#main_asset_format)                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-data-format-of-the-main-asset-assetformat.md "airs_model#/$defs/Properties/properties/main_asset_format")                                                                                                                                                                        |
| [main\_asset\_name](#main_asset_name)                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-name-of-the-main-asset-assetformat.md "airs_model#/$defs/Properties/properties/main_asset_name")                                                                                                                                                                                 |
| [observation\_type](#observation_type)                                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-type-of-observation-observationtype.md "airs_model#/$defs/Properties/properties/observation_type")                                                                                                                                                                               |
| [data\_coverage](#data_coverage)                                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-data-cover.md "airs_model#/$defs/Properties/properties/data_coverage")                                                                                                                                                                                               |
| [water\_coverage](#water_coverage)                                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-water-cover.md "airs_model#/$defs/Properties/properties/water_coverage")                                                                                                                                                                                             |
| [locations](#locations)                                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md "airs_model#/$defs/Properties/properties/locations")                                                                                                                                                                                    |
| [create\_datetime](#create_datetime)                                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-item-registration-service.md "airs_model#/$defs/Properties/properties/create_datetime")                                                                                                                                |
| [update\_datetime](#update_datetime)                                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-item-registration-service.md "airs_model#/$defs/Properties/properties/update_datetime")                                                                                                                              |
| [view\_\_off\_nadir](#view__off_nadir)                                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md "airs_model#/$defs/Properties/properties/view__off_nadir")                                                                                                                |
| [view\_\_incidence\_angle](#view__incidence_angle)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md "airs_model#/$defs/Properties/properties/view__incidence_angle")                            |
| [view\_\_azimuth](#view__azimuth)                                         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md "airs_model#/$defs/Properties/properties/view__azimuth")                  |
| [view\_\_sun\_azimuth](#view__sun_azimuth)                                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md "airs_model#/$defs/Properties/properties/view__sun_azimuth")                                                                |
| [view\_\_sun\_elevation](#view__sun_elevation)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md "airs_model#/$defs/Properties/properties/view__sun_elevation") |
| [storage\_\_requester\_pays](#storage__requester_pays)                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "airs_model#/$defs/Properties/properties/storage__requester_pays")                                                                      |
| [storage\_\_tier](#storage__tier)                                         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "airs_model#/$defs/Properties/properties/storage__tier")                                                                                                                                                                    |
| [storage\_\_platform](#storage__platform)                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "airs_model#/$defs/Properties/properties/storage__platform")                                                                                                                                                            |
| [storage\_\_region](#storage__region)                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "airs_model#/$defs/Properties/properties/storage__region")                                                                                          |
| [eo\_\_cloud\_cover](#eo__cloud_cover)                                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-cloud-cover.md "airs_model#/$defs/Properties/properties/eo__cloud_cover")                                                                                                                                                                                            |
| [eo\_\_snow\_cover](#eo__snow_cover)                                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md "airs_model#/$defs/Properties/properties/eo__snow_cover")                                                                                                                                                                                      |
| [eo\_\_bands](#eo__bands)                                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "airs_model#/$defs/Properties/properties/eo__bands")                                                                                                                       |
| [processing\_\_expression](#processing__expression)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md "airs_model#/$defs/Properties/properties/processing__expression")               |
| [processing\_\_lineage](#processing__lineage)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md "airs_model#/$defs/Properties/properties/processing__lineage")                                       |
| [processing\_\_level](#processing__level)                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md "airs_model#/$defs/Properties/properties/processing__level")                                   |
| [processing\_\_facility](#processing__facility)                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md "airs_model#/$defs/Properties/properties/processing__facility")                                                                      |
| [processing\_\_software](#processing__software)                           | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md "airs_model#/$defs/Properties/properties/processing__software")                                                                                                            |
| [dc3\_\_quality\_indicators](#dc3__quality_indicators)                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md "airs_model#/$defs/Properties/properties/dc3__quality_indicators")                  |
| [dc3\_\_composition](#dc3__composition)                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md "airs_model#/$defs/Properties/properties/dc3__composition")                                                                                                                                               |
| [dc3\_\_number\_of\_chunks](#dc3__number_of_chunks)                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md "airs_model#/$defs/Properties/properties/dc3__number_of_chunks")                                                                                                                                       |
| [dc3\_\_chunk\_weight](#dc3__chunk_weight)                                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md "airs_model#/$defs/Properties/properties/dc3__chunk_weight")                                                                                                                                                                                |
| [dc3\_\_fill\_ratio](#dc3__fill_ratio)                                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md "airs_model#/$defs/Properties/properties/dc3__fill_ratio")                                                                                                                                     |
| [cube\_\_dimensions](#cube__dimensions)                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md "airs_model#/$defs/Properties/properties/cube__dimensions")                                                                                                                                                                         |
| [cube\_\_variables](#cube__variables)                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md "airs_model#/$defs/Properties/properties/cube__variables")                                                                                                                                                                           |
| [acq\_\_acquisition\_mode](#acq__acquisition_mode)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-of-the-acquisition-mode.md "airs_model#/$defs/Properties/properties/acq__acquisition_mode")                                                                                                                                                                             |
| [acq\_\_acquisition\_orbit\_direction](#acq__acquisition_orbit_direction) | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-acquisition-orbit-direction-ascending-or-descending.md "airs_model#/$defs/Properties/properties/acq__acquisition_orbit_direction")                                                                                                                                               |
| [acq\_\_acquisition\_type](#acq__acquisition_type)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-acquisition-type-strip.md "airs_model#/$defs/Properties/properties/acq__acquisition_type")                                                                                                                                                                                       |
| [acq\_\_acquisition\_orbit](#acq__acquisition_orbit)                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-acquisition-orbit.md "airs_model#/$defs/Properties/properties/acq__acquisition_orbit")                                                                                                                                                                                           |
| [acq\_\_across\_track](#acq__across_track)                                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-across-track-angle.md "airs_model#/$defs/Properties/properties/acq__across_track")                                                                                                                                                                                               |
| [acq\_\_along\_track](#acq__along_track)                                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-along-track-angle.md "airs_model#/$defs/Properties/properties/acq__along_track")                                                                                                                                                                                                 |
| [acq\_\_archiving\_date](#acq__archiving_date)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-archiving-date.md "airs_model#/$defs/Properties/properties/acq__archiving_date")                                                                                                                                                                                                 |
| [acq\_\_download\_orbit](#acq__download_orbit)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-download-orbit.md "airs_model#/$defs/Properties/properties/acq__download_orbit")                                                                                                                                                                                                 |
| [acq\_\_request\_id](#acq__request_id)                                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-original-request-identifier.md "airs_model#/$defs/Properties/properties/acq__request_id")                                                                                                                                                                                        |
| [acq\_\_quality\_average](#acq__quality_average)                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-quality-average.md "airs_model#/$defs/Properties/properties/acq__quality_average")                                                                                                                                                                                               |
| [acq\_\_quality\_computation](#acq__quality_computation)                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-quality-computation.md "airs_model#/$defs/Properties/properties/acq__quality_computation")                                                                                                                                                                                       |
| [acq\_\_receiving\_station](#acq__receiving_station)                      | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-receiving-station.md "airs_model#/$defs/Properties/properties/acq__receiving_station")                                                                                                                                                                                           |
| [acq\_\_reception\_date](#acq__reception_date)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-reception-date.md "airs_model#/$defs/Properties/properties/acq__reception_date")                                                                                                                                                                                                 |
| [acq\_\_spectral\_mode](#acq__spectral_mode)                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-spectral-mode.md "airs_model#/$defs/Properties/properties/acq__spectral_mode")                                                                                                                                                                                                   |
| [sar\_\_instrument\_mode](#sar__instrument_mode)                          | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "airs_model#/$defs/Properties/properties/sar__instrument_mode")                               |
| [sar\_\_frequency\_band](#sar__frequency_band)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "airs_model#/$defs/Properties/properties/sar__frequency_band")                                           |
| [sar\_\_center\_frequency](#sar__center_frequency)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "airs_model#/$defs/Properties/properties/sar__center_frequency")                                                                                                                                                      |
| [sar\_\_polarizations](#sar__polarizations)                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-any-combination-of-polarizations.md "airs_model#/$defs/Properties/properties/sar__polarizations")                                                                                                                                                                                |
| [sar\_\_product\_type](#sar__product_type)                                | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "airs_model#/$defs/Properties/properties/sar__product_type")                                                                                                                                                                      |
| [sar\_\_resolution\_range](#sar__resolution_range)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Properties/properties/sar__resolution_range")                                                                           |
| [sar\_\_resolution\_azimuth](#sar__resolution_azimuth)                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Properties/properties/sar__resolution_azimuth")                                                                            |
| [sar\_\_pixel\_spacing\_range](#sar__pixel_spacing_range)                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Properties/properties/sar__pixel_spacing_range")                          |
| [sar\_\_pixel\_spacing\_azimuth](#sar__pixel_spacing_azimuth)             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Properties/properties/sar__pixel_spacing_azimuth")                           |
| [sar\_\_looks\_range](#sar__looks_range)                                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "airs_model#/$defs/Properties/properties/sar__looks_range")                                                                                                      |
| [sar\_\_looks\_azimuth](#sar__looks_azimuth)                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "airs_model#/$defs/Properties/properties/sar__looks_azimuth")                                                                                                       |
| [sar\_\_looks\_equivalent\_number](#sar__looks_equivalent_number)         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md "airs_model#/$defs/Properties/properties/sar__looks_equivalent_number")                                                                                                                                                                    |
| [sar\_\_observation\_direction](#sar__observation_direction)              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "airs_model#/$defs/Properties/properties/sar__observation_direction")                                                                                                      |
| [proj\_\_epsg](#proj__epsg)                                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-epsg-code-of-the-datasource.md "airs_model#/$defs/Properties/properties/proj__epsg")                                                                                                                                                                                             |
| [proj\_\_wkt2](#proj__wkt2)                                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "airs_model#/$defs/Properties/properties/proj__wkt2")                                                                                                    |
| [proj\_\_geometry](#proj__geometry)                                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-defines-the-footprint-of-this-item.md "airs_model#/$defs/Properties/properties/proj__geometry")                                                                                                                                                                                  |
| [proj\_\_bbox](#proj__bbox)                                               | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "airs_model#/$defs/Properties/properties/proj__bbox")                                                                                                                                                          |
| [proj\_\_centroid](#proj__centroid)                                       | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "airs_model#/$defs/Properties/properties/proj__centroid")                                                                                                                                                        |
| [proj\_\_shape](#proj__shape)                                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "airs_model#/$defs/Properties/properties/proj__shape")                                                                                                                                                            |
| [proj\_\_transform](#proj__transform)                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md "airs_model#/$defs/Properties/properties/proj__transform")                                                                                                                                                        |
| [generated\_\_has\_overview](#generated__has_overview)                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md "airs_model#/$defs/Properties/properties/generated__has_overview")                                                                                                                                                                    |
| [generated\_\_has\_thumbnail](#generated__has_thumbnail)                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md "airs_model#/$defs/Properties/properties/generated__has_thumbnail")                                                                                                                                                                   |
| [generated\_\_has\_metadata](#generated__has_metadata)                    | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md "airs_model#/$defs/Properties/properties/generated__has_metadata")                                                                                                                                                                |
| [generated\_\_has\_data](#generated__has_data)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md "airs_model#/$defs/Properties/properties/generated__has_data")                                                                                                                                                                        |
| [generated\_\_has\_cog](#generated__has_cog)                              | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md "airs_model#/$defs/Properties/properties/generated__has_cog")                                                                                                                                                                               |
| [generated\_\_has\_zarr](#generated__has_zarr)                            | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md "airs_model#/$defs/Properties/properties/generated__has_zarr")                                                                                                                                                                             |
| [generated\_\_date\_keywords](#generated__date_keywords)                  | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md "airs_model#/$defs/Properties/properties/generated__date_keywords")                                                                                                                                                           |
| [generated\_\_day\_of\_week](#generated__day_of_week)                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-day-of-week.md "airs_model#/$defs/Properties/properties/generated__day_of_week")                                                                                                                                                                                                 |
| [generated\_\_day\_of\_year](#generated__day_of_year)                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-day-of-year.md "airs_model#/$defs/Properties/properties/generated__day_of_year")                                                                                                                                                                                                 |
| [generated\_\_hour\_of\_day](#generated__hour_of_day)                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-hour-of-day.md "airs_model#/$defs/Properties/properties/generated__hour_of_day")                                                                                                                                                                                                 |
| [generated\_\_minute\_of\_day](#generated__minute_of_day)                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-minute-of-day.md "airs_model#/$defs/Properties/properties/generated__minute_of_day")                                                                                                                                                                                             |
| [generated\_\_month](#generated__month)                                   | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-month.md "airs_model#/$defs/Properties/properties/generated__month")                                                                                                                                                                                                             |
| [generated\_\_year](#generated__year)                                     | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-year.md "airs_model#/$defs/Properties/properties/generated__year")                                                                                                                                                                                                               |
| [generated\_\_season](#generated__season)                                 | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-season.md "airs_model#/$defs/Properties/properties/generated__season")                                                                                                                                                                                                           |
| [generated\_\_tltrbrbl](#generated__tltrbrbl)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md "airs_model#/$defs/Properties/properties/generated__tltrbrbl")                                                                                                                         |
| [generated\_\_band\_common\_names](#generated__band_common_names)         | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-the-band-common-names.md "airs_model#/$defs/Properties/properties/generated__band_common_names")                                                                                                                                                                         |
| [generated\_\_band\_names](#generated__band_names)                        | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-list-of-the-band-names.md "airs_model#/$defs/Properties/properties/generated__band_names")                                                                                                                                                                                       |
| [generated\_\_geohash2](#generated__geohash2)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-two-characters.md "airs_model#/$defs/Properties/properties/generated__geohash2")                                                                                                                                                                            |
| [generated\_\_geohash3](#generated__geohash3)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-three-characters.md "airs_model#/$defs/Properties/properties/generated__geohash3")                                                                                                                                                                          |
| [generated\_\_geohash4](#generated__geohash4)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-four-characters.md "airs_model#/$defs/Properties/properties/generated__geohash4")                                                                                                                                                                           |
| [generated\_\_geohash5](#generated__geohash5)                             | Merged | Optional | cannot be null | [Item](model-defs-properties-properties-geohash-on-the-first-five-characters.md "airs_model#/$defs/Properties/properties/generated__geohash5")                                                                                                                                                                           |
| Additional Properties                                                     | Any    | Optional | can be null    |                                                                                                                                                                                                                                                                                                                          |

## datetime



`datetime`

* is optional

* Type: merged type ([datetime associated with this item. If None, a start\_datetime and end\_datetime must be supplied.](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md "airs_model#/$defs/Properties/properties/datetime")

### datetime Type

merged type ([datetime associated with this item. If None, a start\_datetime and end\_datetime must be supplied.](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied.md))

any of

* [Untitled string in Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-datetime-associated-with-this-item-if-none-a-start_datetime-and-end_datetime-must-be-supplied-anyof-1.md "check type definition")

## start\_datetime



`start_datetime`

* is optional

* Type: merged type ([Optional start datetime, part of common metadata. This value will override any start\_datetime key in properties.](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md "airs_model#/$defs/Properties/properties/start_datetime")

### start\_datetime Type

merged type ([Optional start datetime, part of common metadata. This value will override any start\_datetime key in properties.](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties.md))

any of

* [Untitled string in Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-optional-start-datetime-part-of-common-metadata-this-value-will-override-any-start_datetime-key-in-properties-anyof-1.md "check type definition")

## end\_datetime



`end_datetime`

* is optional

* Type: merged type ([Optional end datetime, part of common metadata. This value will override any end\_datetime key in properties.](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md "airs_model#/$defs/Properties/properties/end_datetime")

### end\_datetime Type

merged type ([Optional end datetime, part of common metadata. This value will override any end\_datetime key in properties.](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties.md))

any of

* [Untitled string in Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-optional-end-datetime-part-of-common-metadata-this-value-will-override-any-end_datetime-key-in-properties-anyof-1.md "check type definition")

## keywords



`keywords`

* is optional

* Type: merged type ([A list of keywords](model-defs-properties-properties-a-list-of-keywords.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-a-list-of-keywords.md "airs_model#/$defs/Properties/properties/keywords")

### keywords Type

merged type ([A list of keywords](model-defs-properties-properties-a-list-of-keywords.md))

any of

* [Untitled array in Item](model-defs-properties-properties-a-list-of-keywords-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-a-list-of-keywords-anyof-1.md "check type definition")

## programme



`programme`

* is optional

* Type: merged type ([Name of the programme](model-defs-properties-properties-name-of-the-programme.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-programme.md "airs_model#/$defs/Properties/properties/programme")

### programme Type

merged type ([Name of the programme](model-defs-properties-properties-name-of-the-programme.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-programme-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-programme-anyof-1.md "check type definition")

## constellation



`constellation`

* is optional

* Type: merged type ([Name of the constellation](model-defs-properties-properties-name-of-the-constellation.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-constellation.md "airs_model#/$defs/Properties/properties/constellation")

### constellation Type

merged type ([Name of the constellation](model-defs-properties-properties-name-of-the-constellation.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-constellation-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-constellation-anyof-1.md "check type definition")

## satellite



`satellite`

* is optional

* Type: merged type ([Name of the satellite](model-defs-properties-properties-name-of-the-satellite.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-satellite.md "airs_model#/$defs/Properties/properties/satellite")

### satellite Type

merged type ([Name of the satellite](model-defs-properties-properties-name-of-the-satellite.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-satellite-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-satellite-anyof-1.md "check type definition")

## platform



`platform`

* is optional

* Type: merged type ([Name of the satellite platform](model-defs-properties-properties-name-of-the-satellite-platform.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-satellite-platform.md "airs_model#/$defs/Properties/properties/platform")

### platform Type

merged type ([Name of the satellite platform](model-defs-properties-properties-name-of-the-satellite-platform.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-satellite-platform-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-satellite-platform-anyof-1.md "check type definition")

## instrument



`instrument`

* is optional

* Type: merged type ([Name of the instrument](model-defs-properties-properties-name-of-the-instrument.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-instrument.md "airs_model#/$defs/Properties/properties/instrument")

### instrument Type

merged type ([Name of the instrument](model-defs-properties-properties-name-of-the-instrument.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-instrument-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-instrument-anyof-1.md "check type definition")

## sensor



`sensor`

* is optional

* Type: merged type ([Name of the sensor](model-defs-properties-properties-name-of-the-sensor.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-sensor.md "airs_model#/$defs/Properties/properties/sensor")

### sensor Type

merged type ([Name of the sensor](model-defs-properties-properties-name-of-the-sensor.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-sensor-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-sensor-anyof-1.md "check type definition")

## sensor\_mode



`sensor_mode`

* is optional

* Type: merged type ([Mode of the sensor during acquisition](model-defs-properties-properties-mode-of-the-sensor-during-acquisition.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-mode-of-the-sensor-during-acquisition.md "airs_model#/$defs/Properties/properties/sensor_mode")

### sensor\_mode Type

merged type ([Mode of the sensor during acquisition](model-defs-properties-properties-mode-of-the-sensor-during-acquisition.md))

any of

* [Untitled string in Item](model-defs-properties-properties-mode-of-the-sensor-during-acquisition-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-mode-of-the-sensor-during-acquisition-anyof-1.md "check type definition")

## sensor\_type



`sensor_type`

* is optional

* Type: merged type ([Type of sensor](model-defs-properties-properties-type-of-sensor.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-type-of-sensor.md "airs_model#/$defs/Properties/properties/sensor_type")

### sensor\_type Type

merged type ([Type of sensor](model-defs-properties-properties-type-of-sensor.md))

any of

* [Untitled string in Item](model-defs-properties-properties-type-of-sensor-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-type-of-sensor-anyof-1.md "check type definition")

## annotations



`annotations`

* is optional

* Type: merged type ([Human annotations for the item](model-defs-properties-properties-human-annotations-for-the-item.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-human-annotations-for-the-item.md "airs_model#/$defs/Properties/properties/annotations")

### annotations Type

merged type ([Human annotations for the item](model-defs-properties-properties-human-annotations-for-the-item.md))

any of

* [Untitled string in Item](model-defs-properties-properties-human-annotations-for-the-item-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-human-annotations-for-the-item-anyof-1.md "check type definition")

## gsd



`gsd`

* is optional

* Type: merged type ([Ground Sampling Distance (resolution)](model-defs-properties-properties-ground-sampling-distance-resolution.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-ground-sampling-distance-resolution.md "airs_model#/$defs/Properties/properties/gsd")

### gsd Type

merged type ([Ground Sampling Distance (resolution)](model-defs-properties-properties-ground-sampling-distance-resolution.md))

any of

* [Untitled number in Item](model-defs-properties-properties-ground-sampling-distance-resolution-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-ground-sampling-distance-resolution-anyof-1.md "check type definition")

## secondary\_id



`secondary_id`

* is optional

* Type: merged type ([Secondary identifier](model-defs-properties-properties-secondary-identifier.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-secondary-identifier.md "airs_model#/$defs/Properties/properties/secondary_id")

### secondary\_id Type

merged type ([Secondary identifier](model-defs-properties-properties-secondary-identifier.md))

any of

* [Untitled string in Item](model-defs-properties-properties-secondary-identifier-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-secondary-identifier-anyof-1.md "check type definition")

## data\_type



`data_type`

* is optional

* Type: merged type ([Type of data](model-defs-properties-properties-type-of-data.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-type-of-data.md "airs_model#/$defs/Properties/properties/data_type")

### data\_type Type

merged type ([Type of data](model-defs-properties-properties-type-of-data.md))

any of

* [Untitled string in Item](model-defs-properties-properties-type-of-data-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-type-of-data-anyof-1.md "check type definition")

## item\_type



`item_type`

* is optional

* Type: merged type ([Type of data (ResourceType)](model-defs-properties-properties-type-of-data-resourcetype.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-type-of-data-resourcetype.md "airs_model#/$defs/Properties/properties/item_type")

### item\_type Type

merged type ([Type of data (ResourceType)](model-defs-properties-properties-type-of-data-resourcetype.md))

any of

* [Untitled string in Item](model-defs-properties-properties-type-of-data-resourcetype-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-type-of-data-resourcetype-anyof-1.md "check type definition")

## item\_format



`item_format`

* is optional

* Type: merged type ([Data format (ItemFormat)](model-defs-properties-properties-data-format-itemformat.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-data-format-itemformat.md "airs_model#/$defs/Properties/properties/item_format")

### item\_format Type

merged type ([Data format (ItemFormat)](model-defs-properties-properties-data-format-itemformat.md))

any of

* [Untitled string in Item](model-defs-properties-properties-data-format-itemformat-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-data-format-itemformat-anyof-1.md "check type definition")

## main\_asset\_format



`main_asset_format`

* is optional

* Type: merged type ([Data format of the main asset (AssetFormat)](model-defs-properties-properties-data-format-of-the-main-asset-assetformat.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-data-format-of-the-main-asset-assetformat.md "airs_model#/$defs/Properties/properties/main_asset_format")

### main\_asset\_format Type

merged type ([Data format of the main asset (AssetFormat)](model-defs-properties-properties-data-format-of-the-main-asset-assetformat.md))

any of

* [Untitled string in Item](model-defs-properties-properties-data-format-of-the-main-asset-assetformat-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-data-format-of-the-main-asset-assetformat-anyof-1.md "check type definition")

## main\_asset\_name



`main_asset_name`

* is optional

* Type: merged type ([Name of the main asset (AssetFormat)](model-defs-properties-properties-name-of-the-main-asset-assetformat.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-name-of-the-main-asset-assetformat.md "airs_model#/$defs/Properties/properties/main_asset_name")

### main\_asset\_name Type

merged type ([Name of the main asset (AssetFormat)](model-defs-properties-properties-name-of-the-main-asset-assetformat.md))

any of

* [Untitled string in Item](model-defs-properties-properties-name-of-the-main-asset-assetformat-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-name-of-the-main-asset-assetformat-anyof-1.md "check type definition")

## observation\_type



`observation_type`

* is optional

* Type: merged type ([Type of observation (ObservationType)](model-defs-properties-properties-type-of-observation-observationtype.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-type-of-observation-observationtype.md "airs_model#/$defs/Properties/properties/observation_type")

### observation\_type Type

merged type ([Type of observation (ObservationType)](model-defs-properties-properties-type-of-observation-observationtype.md))

any of

* [Untitled string in Item](model-defs-properties-properties-type-of-observation-observationtype-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-type-of-observation-observationtype-anyof-1.md "check type definition")

## data\_coverage



`data_coverage`

* is optional

* Type: merged type ([Estimate of data cover](model-defs-properties-properties-estimate-of-data-cover.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-estimate-of-data-cover.md "airs_model#/$defs/Properties/properties/data_coverage")

### data\_coverage Type

merged type ([Estimate of data cover](model-defs-properties-properties-estimate-of-data-cover.md))

any of

* [Untitled number in Item](model-defs-properties-properties-estimate-of-data-cover-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-estimate-of-data-cover-anyof-1.md "check type definition")

## water\_coverage



`water_coverage`

* is optional

* Type: merged type ([Estimate of water cover](model-defs-properties-properties-estimate-of-water-cover.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-estimate-of-water-cover.md "airs_model#/$defs/Properties/properties/water_coverage")

### water\_coverage Type

merged type ([Estimate of water cover](model-defs-properties-properties-estimate-of-water-cover.md))

any of

* [Untitled number in Item](model-defs-properties-properties-estimate-of-water-cover-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-estimate-of-water-cover-anyof-1.md "check type definition")

## locations



`locations`

* is optional

* Type: merged type ([List of locations covered by the item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md "airs_model#/$defs/Properties/properties/locations")

### locations Type

merged type ([List of locations covered by the item](model-defs-properties-properties-list-of-locations-covered-by-the-item.md))

any of

* [Untitled array in Item](model-defs-properties-properties-list-of-locations-covered-by-the-item-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-list-of-locations-covered-by-the-item-anyof-1.md "check type definition")

## create\_datetime



`create_datetime`

* is optional

* Type: merged type ([Date of item creation in the catalog, managed by the ARLAS Item Registration Service](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-item-registration-service.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-item-registration-service.md "airs_model#/$defs/Properties/properties/create_datetime")

### create\_datetime Type

merged type ([Date of item creation in the catalog, managed by the ARLAS Item Registration Service](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-item-registration-service.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-item-registration-service-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-date-of-item-creation-in-the-catalog-managed-by-the-arlas-item-registration-service-anyof-1.md "check type definition")

## update\_datetime



`update_datetime`

* is optional

* Type: merged type ([Update date of the item in the catalog, managed by the ARLAS Item Registration Service](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-item-registration-service.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-item-registration-service.md "airs_model#/$defs/Properties/properties/update_datetime")

### update\_datetime Type

merged type ([Update date of the item in the catalog, managed by the ARLAS Item Registration Service](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-item-registration-service.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-item-registration-service-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-update-date-of-the-item-in-the-catalog-managed-by-the-arlas-item-registration-service-anyof-1.md "check type definition")

## view\_\_off\_nadir



`view__off_nadir`

* is optional

* Type: merged type ([The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md "airs_model#/$defs/Properties/properties/view__off_nadir")

### view\_\_off\_nadir Type

merged type ([The angle from the sensor between nadir (straight down) and the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-angle-from-the-sensor-between-nadir-straight-down-and-the-scene-center-measured-in-degrees-0-90-anyof-1.md "check type definition")

## view\_\_incidence\_angle



`view__incidence_angle`

* is optional

* Type: merged type ([The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight back to the satellite at the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md "airs_model#/$defs/Properties/properties/view__incidence_angle")

### view\_\_incidence\_angle Type

merged type ([The incidence angle is the angle between the vertical (normal) to the intercepting surface and the line of sight back to the satellite at the scene center. Measured in degrees (0-90).](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-incidence-angle-is-the-angle-between-the-vertical-normal-to-the-intercepting-surface-and-the-line-of-sight-back-to-the-satellite-at-the-scene-center-measured-in-degrees-0-90-anyof-1.md "check type definition")

## view\_\_azimuth



`view__azimuth`

* is optional

* Type: merged type ([Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform) between the scene center and true north. Measured clockwise from north in degrees (0-360).](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md "airs_model#/$defs/Properties/properties/view__azimuth")

### view\_\_azimuth Type

merged type ([Viewing azimuth angle. The angle measured from the sub-satellite point (point on the ground below the platform) between the scene center and true north. Measured clockwise from north in degrees (0-360).](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360.md))

any of

* [Untitled number in Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-viewing-azimuth-angle-the-angle-measured-from-the-sub-satellite-point-point-on-the-ground-below-the-platform-between-the-scene-center-and-true-north-measured-clockwise-from-north-in-degrees-0-360-anyof-1.md "check type definition")

## view\_\_sun\_azimuth



`view__sun_azimuth`

* is optional

* Type: merged type ([Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun. Measured clockwise in degrees (0-360).](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md "airs_model#/$defs/Properties/properties/view__sun_azimuth")

### view\_\_sun\_azimuth Type

merged type ([Sun azimuth angle. From the scene center point on the ground, this is the angle between truth north and the sun. Measured clockwise in degrees (0-360).](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360.md))

any of

* [Untitled number in Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-sun-azimuth-angle-from-the-scene-center-point-on-the-ground-this-is-the-angle-between-truth-north-and-the-sun-measured-clockwise-in-degrees-0-360-anyof-1.md "check type definition")

## view\_\_sun\_elevation



`view__sun_elevation`

* is optional

* Type: merged type ([Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° \[...\]](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md "airs_model#/$defs/Properties/properties/view__sun_elevation")

### view\_\_sun\_elevation Type

merged type ([Sun elevation angle. The angle from the tangent of the scene center point to the sun. Measured from the horizon in degrees (-90-90). Negative values indicate the sun is below the horizon, e.g. sun elevation of -10° \[...\]](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10-.md))

any of

* [Untitled number in Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10--anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-sun-elevation-angle-the-angle-from-the-tangent-of-the-scene-center-point-to-the-sun-measured-from-the-horizon-in-degrees--90-90-negative-values-indicate-the-sun-is-below-the-horizon-eg-sun-elevation-of--10--anyof-1.md "check type definition")

## storage\_\_requester\_pays



`storage__requester_pays`

* is optional

* Type: merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md "airs_model#/$defs/Properties/properties/storage__requester_pays")

### storage\_\_requester\_pays Type

merged type ([Is the data requester pays or is it data manager/cloud provider pays. Defaults to false. Whether the requester pays for accessing assets](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-is-the-data-requester-pays-or-is-it-data-managercloud-provider-pays-defaults-to-false-whether-the-requester-pays-for-accessing-assets-anyof-1.md "check type definition")

## storage\_\_tier



`storage__tier`

* is optional

* Type: merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md "airs_model#/$defs/Properties/properties/storage__tier")

### storage\_\_tier Type

merged type ([Cloud Provider Storage Tiers (Standard, Glacier, etc.)](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc.md))

any of

* [Untitled string in Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-cloud-provider-storage-tiers-standard-glacier-etc-anyof-1.md "check type definition")

## storage\_\_platform



`storage__platform`

* is optional

* Type: merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md "airs_model#/$defs/Properties/properties/storage__platform")

### storage\_\_platform Type

merged type ([PaaS solutions (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other.md))

any of

* [Untitled string in Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-paas-solutions-alibaba-aws-azure-gcp-ibm-oracle-other-anyof-1.md "check type definition")

## storage\_\_region



`storage__region`

* is optional

* Type: merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md "airs_model#/$defs/Properties/properties/storage__region")

### storage\_\_region Type

merged type ([The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-region-where-the-data-is-stored-relevant-to-speed-of-access-and-inter-region-egress-costs-as-defined-by-paas-provider-anyof-1.md "check type definition")

## eo\_\_cloud\_cover



`eo__cloud_cover`

* is optional

* Type: merged type ([Estimate of cloud cover.](model-defs-properties-properties-estimate-of-cloud-cover.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-estimate-of-cloud-cover.md "airs_model#/$defs/Properties/properties/eo__cloud_cover")

### eo\_\_cloud\_cover Type

merged type ([Estimate of cloud cover.](model-defs-properties-properties-estimate-of-cloud-cover.md))

any of

* [Untitled number in Item](model-defs-properties-properties-estimate-of-cloud-cover-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-estimate-of-cloud-cover-anyof-1.md "check type definition")

## eo\_\_snow\_cover



`eo__snow_cover`

* is optional

* Type: merged type ([Estimate of snow and ice cover.](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md "airs_model#/$defs/Properties/properties/eo__snow_cover")

### eo\_\_snow\_cover Type

merged type ([Estimate of snow and ice cover.](model-defs-properties-properties-estimate-of-snow-and-ice-cover.md))

any of

* [Untitled number in Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-estimate-of-snow-and-ice-cover-anyof-1.md "check type definition")

## eo\_\_bands



`eo__bands`

* is optional

* Type: merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md "airs_model#/$defs/Properties/properties/eo__bands")

### eo\_\_bands Type

merged type ([An array of available bands where each object is a Band Object. If given, requires at least one band.](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band.md))

any of

* [Untitled array in Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-an-array-of-available-bands-where-each-object-is-a-band-object-if-given-requires-at-least-one-band-anyof-1.md "check type definition")

## processing\_\_expression



`processing__expression`

* is optional

* Type: merged type ([An expression or processing chain that describes how the data has been processed. Alternatively, you can also link to a processing chain with the relation type processing-expression (see below).](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md "airs_model#/$defs/Properties/properties/processing__expression")

### processing\_\_expression Type

merged type ([An expression or processing chain that describes how the data has been processed. Alternatively, you can also link to a processing chain with the relation type processing-expression (see below).](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below.md))

any of

* [Untitled string in Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-an-expression-or-processing-chain-that-describes-how-the-data-has-been-processed-alternatively-you-can-also-link-to-a-processing-chain-with-the-relation-type-processing-expression-see-below-anyof-1.md "check type definition")

## processing\_\_lineage



`processing__lineage`

* is optional

* Type: merged type ([Lineage Information provided as free text information about the how observations were processed or models that were used to create the resource being described NASA ISO.](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md "airs_model#/$defs/Properties/properties/processing__lineage")

### processing\_\_lineage Type

merged type ([Lineage Information provided as free text information about the how observations were processed or models that were used to create the resource being described NASA ISO.](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso.md))

any of

* [Untitled string in Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-lineage-information-provided-as-free-text-information-about-the-how-observations-were-processed-or-models-that-were-used-to-create-the-resource-being-described-nasa-iso-anyof-1.md "check type definition")

## processing\_\_level



`processing__level`

* is optional

* Type: merged type ([The name commonly used to refer to the processing level to make it easier to search for product level across collections or items. The short name must be used (only L, not Level).](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md "airs_model#/$defs/Properties/properties/processing__level")

### processing\_\_level Type

merged type ([The name commonly used to refer to the processing level to make it easier to search for product level across collections or items. The short name must be used (only L, not Level).](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-name-commonly-used-to-refer-to-the-processing-level-to-make-it-easier-to-search-for-product-level-across-collections-or-items-the-short-name-must-be-used-only-l-not-level-anyof-1.md "check type definition")

## processing\_\_facility



`processing__facility`

* is optional

* Type: merged type ([The name of the facility that produced the data. For example, Copernicus S1 Core Ground Segment - DPA for product of Sentinel-1 satellites.](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md "airs_model#/$defs/Properties/properties/processing__facility")

### processing\_\_facility Type

merged type ([The name of the facility that produced the data. For example, Copernicus S1 Core Ground Segment - DPA for product of Sentinel-1 satellites.](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-name-of-the-facility-that-produced-the-data-for-example-copernicus-s1-core-ground-segment---dpa-for-product-of-sentinel-1-satellites-anyof-1.md "check type definition")

## processing\_\_software



`processing__software`

* is optional

* Type: merged type ([A dictionary with name/version for key/value describing one or more softwares that produced the data.](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md "airs_model#/$defs/Properties/properties/processing__software")

### processing\_\_software Type

merged type ([A dictionary with name/version for key/value describing one or more softwares that produced the data.](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data.md))

any of

* [Untitled object in Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-a-dictionary-with-nameversion-for-keyvalue-describing-one-or-more-softwares-that-produced-the-data-anyof-1.md "check type definition")

## dc3\_\_quality\_indicators



`dc3__quality_indicators`

* is optional

* Type: merged type ([Set of indicators for estimating the quality of the datacube based on the composition. The indicators are group based. A cube indicator is the product of its corresponding group indicator.](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md "airs_model#/$defs/Properties/properties/dc3__quality_indicators")

### dc3\_\_quality\_indicators Type

merged type ([Set of indicators for estimating the quality of the datacube based on the composition. The indicators are group based. A cube indicator is the product of its corresponding group indicator.](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator.md))

any of

* [Indicators](model-defs-indicators.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-set-of-indicators-for-estimating-the-quality-of-the-datacube-based-on-the-composition-the-indicators-are-group-based-a-cube-indicator-is-the-product-of-its-corresponding-group-indicator-anyof-1.md "check type definition")

## dc3\_\_composition



`dc3__composition`

* is optional

* Type: merged type ([List of raster groups used for elaborating the cube temporal slices.](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md "airs_model#/$defs/Properties/properties/dc3__composition")

### dc3\_\_composition Type

merged type ([List of raster groups used for elaborating the cube temporal slices.](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices.md))

any of

* [Untitled array in Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-list-of-raster-groups-used-for-elaborating-the-cube-temporal-slices-anyof-1.md "check type definition")

## dc3\_\_number\_of\_chunks



`dc3__number_of_chunks`

* is optional

* Type: merged type ([Number of chunks (if zarr or similar partitioned format) within the cube.](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md "airs_model#/$defs/Properties/properties/dc3__number_of_chunks")

### dc3\_\_number\_of\_chunks Type

merged type ([Number of chunks (if zarr or similar partitioned format) within the cube.](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-number-of-chunks-if-zarr-or-similar-partitioned-format-within-the-cube-anyof-1.md "check type definition")

## dc3\_\_chunk\_weight



`dc3__chunk_weight`

* is optional

* Type: merged type ([Weight of a chunk (number of bytes).](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md "airs_model#/$defs/Properties/properties/dc3__chunk_weight")

### dc3\_\_chunk\_weight Type

merged type ([Weight of a chunk (number of bytes).](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-weight-of-a-chunk-number-of-bytes-anyof-1.md "check type definition")

## dc3\_\_fill\_ratio



`dc3__fill_ratio`

* is optional

* Type: merged type ([1: the cube is full, 0 the cube is empty, in between the cube is partially filled.](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md "airs_model#/$defs/Properties/properties/dc3__fill_ratio")

### dc3\_\_fill\_ratio Type

merged type ([1: the cube is full, 0 the cube is empty, in between the cube is partially filled.](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled.md))

any of

* [Untitled number in Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-1-the-cube-is-full-0-the-cube-is-empty-in-between-the-cube-is-partially-filled-anyof-1.md "check type definition")

## cube\_\_dimensions



`cube__dimensions`

* is optional

* Type: merged type ([Uniquely named dimensions of the datacube.](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md "airs_model#/$defs/Properties/properties/cube__dimensions")

### cube\_\_dimensions Type

merged type ([Uniquely named dimensions of the datacube.](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube.md))

any of

* [Untitled object in Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-uniquely-named-dimensions-of-the-datacube-anyof-1.md "check type definition")

## cube\_\_variables



`cube__variables`

* is optional

* Type: merged type ([Uniquely named variables of the datacube.](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md "airs_model#/$defs/Properties/properties/cube__variables")

### cube\_\_variables Type

merged type ([Uniquely named variables of the datacube.](model-defs-properties-properties-uniquely-named-variables-of-the-datacube.md))

any of

* [Untitled object in Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-uniquely-named-variables-of-the-datacube-anyof-1.md "check type definition")

## acq\_\_acquisition\_mode



`acq__acquisition_mode`

* is optional

* Type: merged type ([The name of the acquisition mode.](model-defs-properties-properties-the-name-of-the-acquisition-mode.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-name-of-the-acquisition-mode.md "airs_model#/$defs/Properties/properties/acq__acquisition_mode")

### acq\_\_acquisition\_mode Type

merged type ([The name of the acquisition mode.](model-defs-properties-properties-the-name-of-the-acquisition-mode.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-name-of-the-acquisition-mode-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-name-of-the-acquisition-mode-anyof-1.md "check type definition")

## acq\_\_acquisition\_orbit\_direction



`acq__acquisition_orbit_direction`

* is optional

* Type: merged type ([Acquisition orbit direction (ASCENDING or DESCENDING).](model-defs-properties-properties-acquisition-orbit-direction-ascending-or-descending.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-acquisition-orbit-direction-ascending-or-descending.md "airs_model#/$defs/Properties/properties/acq__acquisition_orbit_direction")

### acq\_\_acquisition\_orbit\_direction Type

merged type ([Acquisition orbit direction (ASCENDING or DESCENDING).](model-defs-properties-properties-acquisition-orbit-direction-ascending-or-descending.md))

any of

* [Untitled string in Item](model-defs-properties-properties-acquisition-orbit-direction-ascending-or-descending-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-acquisition-orbit-direction-ascending-or-descending-anyof-1.md "check type definition")

## acq\_\_acquisition\_type



`acq__acquisition_type`

* is optional

* Type: merged type ([Acquisition type (STRIP)](model-defs-properties-properties-acquisition-type-strip.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-acquisition-type-strip.md "airs_model#/$defs/Properties/properties/acq__acquisition_type")

### acq\_\_acquisition\_type Type

merged type ([Acquisition type (STRIP)](model-defs-properties-properties-acquisition-type-strip.md))

any of

* [Untitled string in Item](model-defs-properties-properties-acquisition-type-strip-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-acquisition-type-strip-anyof-1.md "check type definition")

## acq\_\_acquisition\_orbit



`acq__acquisition_orbit`

* is optional

* Type: merged type ([Acquisition orbit](model-defs-properties-properties-acquisition-orbit.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-acquisition-orbit.md "airs_model#/$defs/Properties/properties/acq__acquisition_orbit")

### acq\_\_acquisition\_orbit Type

merged type ([Acquisition orbit](model-defs-properties-properties-acquisition-orbit.md))

any of

* [Untitled number in Item](model-defs-properties-properties-acquisition-orbit-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-acquisition-orbit-anyof-1.md "check type definition")

## acq\_\_across\_track



`acq__across_track`

* is optional

* Type: merged type ([Across track angle](model-defs-properties-properties-across-track-angle.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-across-track-angle.md "airs_model#/$defs/Properties/properties/acq__across_track")

### acq\_\_across\_track Type

merged type ([Across track angle](model-defs-properties-properties-across-track-angle.md))

any of

* [Untitled number in Item](model-defs-properties-properties-across-track-angle-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-across-track-angle-anyof-1.md "check type definition")

## acq\_\_along\_track



`acq__along_track`

* is optional

* Type: merged type ([Along track angle](model-defs-properties-properties-along-track-angle.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-along-track-angle.md "airs_model#/$defs/Properties/properties/acq__along_track")

### acq\_\_along\_track Type

merged type ([Along track angle](model-defs-properties-properties-along-track-angle.md))

any of

* [Untitled number in Item](model-defs-properties-properties-along-track-angle-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-along-track-angle-anyof-1.md "check type definition")

## acq\_\_archiving\_date



`acq__archiving_date`

* is optional

* Type: merged type ([Archiving date](model-defs-properties-properties-archiving-date.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-archiving-date.md "airs_model#/$defs/Properties/properties/acq__archiving_date")

### acq\_\_archiving\_date Type

merged type ([Archiving date](model-defs-properties-properties-archiving-date.md))

any of

* [Untitled string in Item](model-defs-properties-properties-archiving-date-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-archiving-date-anyof-1.md "check type definition")

## acq\_\_download\_orbit



`acq__download_orbit`

* is optional

* Type: merged type ([Download orbit](model-defs-properties-properties-download-orbit.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-download-orbit.md "airs_model#/$defs/Properties/properties/acq__download_orbit")

### acq\_\_download\_orbit Type

merged type ([Download orbit](model-defs-properties-properties-download-orbit.md))

any of

* [Untitled number in Item](model-defs-properties-properties-download-orbit-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-download-orbit-anyof-1.md "check type definition")

## acq\_\_request\_id



`acq__request_id`

* is optional

* Type: merged type ([Original request identifier](model-defs-properties-properties-original-request-identifier.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-original-request-identifier.md "airs_model#/$defs/Properties/properties/acq__request_id")

### acq\_\_request\_id Type

merged type ([Original request identifier](model-defs-properties-properties-original-request-identifier.md))

any of

* [Untitled string in Item](model-defs-properties-properties-original-request-identifier-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-original-request-identifier-anyof-1.md "check type definition")

## acq\_\_quality\_average



`acq__quality_average`

* is optional

* Type: merged type ([Quality average](model-defs-properties-properties-quality-average.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-quality-average.md "airs_model#/$defs/Properties/properties/acq__quality_average")

### acq\_\_quality\_average Type

merged type ([Quality average](model-defs-properties-properties-quality-average.md))

any of

* [Untitled number in Item](model-defs-properties-properties-quality-average-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-quality-average-anyof-1.md "check type definition")

## acq\_\_quality\_computation



`acq__quality_computation`

* is optional

* Type: merged type ([Quality computation](model-defs-properties-properties-quality-computation.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-quality-computation.md "airs_model#/$defs/Properties/properties/acq__quality_computation")

### acq\_\_quality\_computation Type

merged type ([Quality computation](model-defs-properties-properties-quality-computation.md))

any of

* [Untitled string in Item](model-defs-properties-properties-quality-computation-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-quality-computation-anyof-1.md "check type definition")

## acq\_\_receiving\_station



`acq__receiving_station`

* is optional

* Type: merged type ([Receiving station](model-defs-properties-properties-receiving-station.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-receiving-station.md "airs_model#/$defs/Properties/properties/acq__receiving_station")

### acq\_\_receiving\_station Type

merged type ([Receiving station](model-defs-properties-properties-receiving-station.md))

any of

* [Untitled string in Item](model-defs-properties-properties-receiving-station-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-receiving-station-anyof-1.md "check type definition")

## acq\_\_reception\_date



`acq__reception_date`

* is optional

* Type: merged type ([Reception date](model-defs-properties-properties-reception-date.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-reception-date.md "airs_model#/$defs/Properties/properties/acq__reception_date")

### acq\_\_reception\_date Type

merged type ([Reception date](model-defs-properties-properties-reception-date.md))

any of

* [Untitled string in Item](model-defs-properties-properties-reception-date-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-reception-date-anyof-1.md "check type definition")

## acq\_\_spectral\_mode



`acq__spectral_mode`

* is optional

* Type: merged type ([Spectral mode](model-defs-properties-properties-spectral-mode.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-spectral-mode.md "airs_model#/$defs/Properties/properties/acq__spectral_mode")

### acq\_\_spectral\_mode Type

merged type ([Spectral mode](model-defs-properties-properties-spectral-mode.md))

any of

* [Untitled string in Item](model-defs-properties-properties-spectral-mode-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-spectral-mode-anyof-1.md "check type definition")

## sar\_\_instrument\_mode



`sar__instrument_mode`

* is optional

* Type: merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md "airs_model#/$defs/Properties/properties/sar__instrument_mode")

### sar\_\_instrument\_mode Type

merged type ([The name of the sensor acquisition mode that is commonly used. This should be the short name, if available. For example, WV for "Wave mode" of Sentinel-1 and Envisat ASAR satellites.](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-name-of-the-sensor-acquisition-mode-that-is-commonly-used-this-should-be-the-short-name-if-available-for-example-wv-for-wave-mode-of-sentinel-1-and-envisat-asar-satellites-anyof-1.md "check type definition")

## sar\_\_frequency\_band



`sar__frequency_band`

* is optional

* Type: merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md "airs_model#/$defs/Properties/properties/sar__frequency_band")

### sar\_\_frequency\_band Type

merged type ([The common name for the frequency band to make it easier to search for bands across instruments. See section "Common Frequency Band Names" for a list of accepted names.](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-common-name-for-the-frequency-band-to-make-it-easier-to-search-for-bands-across-instruments-see-section-common-frequency-band-names-for-a-list-of-accepted-names-anyof-1.md "check type definition")

## sar\_\_center\_frequency



`sar__center_frequency`

* is optional

* Type: merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md "airs_model#/$defs/Properties/properties/sar__center_frequency")

### sar\_\_center\_frequency Type

merged type ([The center frequency of the instrument, in gigahertz (GHz).](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-center-frequency-of-the-instrument-in-gigahertz-ghz-anyof-1.md "check type definition")

## sar\_\_polarizations



`sar__polarizations`

* is optional

* Type: merged type ([Any combination of polarizations.](model-defs-properties-properties-any-combination-of-polarizations.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-any-combination-of-polarizations.md "airs_model#/$defs/Properties/properties/sar__polarizations")

### sar\_\_polarizations Type

merged type ([Any combination of polarizations.](model-defs-properties-properties-any-combination-of-polarizations.md))

any of

* [Untitled string in Item](model-defs-properties-properties-any-combination-of-polarizations-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-any-combination-of-polarizations-anyof-1.md "check type definition")

## sar\_\_product\_type



`sar__product_type`

* is optional

* Type: merged type ([The product type, for example SSC, MGD, or SGC](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md "airs_model#/$defs/Properties/properties/sar__product_type")

### sar\_\_product\_type Type

merged type ([The product type, for example SSC, MGD, or SGC](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc.md))

any of

* [Untitled string in Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-product-type-for-example-ssc-mgd-or-sgc-anyof-1.md "check type definition")

## sar\_\_resolution\_range



`sar__resolution_range`

* is optional

* Type: merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Properties/properties/sar__resolution_range")

### sar\_\_resolution\_range Type

merged type ([The range resolution, which is the maximum ability to distinguish two adjacent targets perpendicular to the flight path, in meters (m).](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-range-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-perpendicular-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

## sar\_\_resolution\_azimuth



`sar__resolution_azimuth`

* is optional

* Type: merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md "airs_model#/$defs/Properties/properties/sar__resolution_azimuth")

### sar\_\_resolution\_azimuth Type

merged type ([The azimuth resolution, which is the maximum ability to distinguish two adjacent targets parallel to the flight path, in meters (m).](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-azimuth-resolution-which-is-the-maximum-ability-to-distinguish-two-adjacent-targets-parallel-to-the-flight-path-in-meters-m-anyof-1.md "check type definition")

## sar\_\_pixel\_spacing\_range



`sar__pixel_spacing_range`

* is optional

* Type: merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Properties/properties/sar__pixel_spacing_range")

### sar\_\_pixel\_spacing\_range Type

merged type ([The range pixel spacing, which is the distance between adjacent pixels perpendicular to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-range-pixel-spacing-which-is-the-distance-between-adjacent-pixels-perpendicular-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

## sar\_\_pixel\_spacing\_azimuth



`sar__pixel_spacing_azimuth`

* is optional

* Type: merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md "airs_model#/$defs/Properties/properties/sar__pixel_spacing_azimuth")

### sar\_\_pixel\_spacing\_azimuth Type

merged type ([The azimuth pixel spacing, which is the distance between adjacent pixels parallel to the flight path, in meters (m). Strongly RECOMMENDED to be specified for products of type GRD.](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-azimuth-pixel-spacing-which-is-the-distance-between-adjacent-pixels-parallel-to-the-flight-path-in-meters-m-strongly-recommended-to-be-specified-for-products-of-type-grd-anyof-1.md "check type definition")

## sar\_\_looks\_range



`sar__looks_range`

* is optional

* Type: merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md "airs_model#/$defs/Properties/properties/sar__looks_range")

### sar\_\_looks\_range Type

merged type ([Number of range looks, which is the number of groups of signal samples (looks) perpendicular to the flight path.](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path.md))

any of

* [Untitled number in Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-number-of-range-looks-which-is-the-number-of-groups-of-signal-samples-looks-perpendicular-to-the-flight-path-anyof-1.md "check type definition")

## sar\_\_looks\_azimuth



`sar__looks_azimuth`

* is optional

* Type: merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md "airs_model#/$defs/Properties/properties/sar__looks_azimuth")

### sar\_\_looks\_azimuth Type

merged type ([Number of azimuth looks, which is the number of groups of signal samples (looks) parallel to the flight path.](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path.md))

any of

* [Untitled number in Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-number-of-azimuth-looks-which-is-the-number-of-groups-of-signal-samples-looks-parallel-to-the-flight-path-anyof-1.md "check type definition")

## sar\_\_looks\_equivalent\_number



`sar__looks_equivalent_number`

* is optional

* Type: merged type ([The equivalent number of looks (ENL).](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md "airs_model#/$defs/Properties/properties/sar__looks_equivalent_number")

### sar\_\_looks\_equivalent\_number Type

merged type ([The equivalent number of looks (ENL).](model-defs-properties-properties-the-equivalent-number-of-looks-enl.md))

any of

* [Untitled number in Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-equivalent-number-of-looks-enl-anyof-1.md "check type definition")

## sar\_\_observation\_direction



`sar__observation_direction`

* is optional

* Type: merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md "airs_model#/$defs/Properties/properties/sar__observation_direction")

### sar\_\_observation\_direction Type

merged type ([Antenna pointing direction relative to the flight trajectory of the satellite, either left or right.](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right.md))

any of

* [Untitled string in Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-antenna-pointing-direction-relative-to-the-flight-trajectory-of-the-satellite-either-left-or-right-anyof-1.md "check type definition")

## proj\_\_epsg



`proj__epsg`

* is optional

* Type: merged type ([EPSG code of the datasource.](model-defs-properties-properties-epsg-code-of-the-datasource.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-epsg-code-of-the-datasource.md "airs_model#/$defs/Properties/properties/proj__epsg")

### proj\_\_epsg Type

merged type ([EPSG code of the datasource.](model-defs-properties-properties-epsg-code-of-the-datasource.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-epsg-code-of-the-datasource-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-epsg-code-of-the-datasource-anyof-1.md "check type definition")

## proj\_\_wkt2



`proj__wkt2`

* is optional

* Type: merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md "airs_model#/$defs/Properties/properties/proj__wkt2")

### proj\_\_wkt2 Type

merged type ([PROJJSON object representing the Coordinate Reference System (CRS) that the proj:geometry and proj:bbox fields represent.](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent.md))

any of

* [Untitled string in Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-projjson-object-representing-the-coordinate-reference-system-crs-that-the-projgeometry-and-projbbox-fields-represent-anyof-1.md "check type definition")

## proj\_\_geometry



`proj__geometry`

* is optional

* Type: merged type ([Defines the footprint of this Item.](model-defs-properties-properties-defines-the-footprint-of-this-item.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-defines-the-footprint-of-this-item.md "airs_model#/$defs/Properties/properties/proj__geometry")

### proj\_\_geometry Type

merged type ([Defines the footprint of this Item.](model-defs-properties-properties-defines-the-footprint-of-this-item.md))

any of

* [Untitled undefined type in Item](model-defs-properties-properties-defines-the-footprint-of-this-item-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-defines-the-footprint-of-this-item-anyof-1.md "check type definition")

## proj\_\_bbox



`proj__bbox`

* is optional

* Type: merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md "airs_model#/$defs/Properties/properties/proj__bbox")

### proj\_\_bbox Type

merged type ([Bounding box of the Item in the asset CRS in 2 or 3 dimensions.](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions.md))

any of

* [Untitled array in Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-bounding-box-of-the-item-in-the-asset-crs-in-2-or-3-dimensions-anyof-1.md "check type definition")

## proj\_\_centroid



`proj__centroid`

* is optional

* Type: merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md "airs_model#/$defs/Properties/properties/proj__centroid")

### proj\_\_centroid Type

merged type ([Coordinates representing the centroid of the Item (in lat/long).](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong.md))

any of

* [Untitled undefined type in Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-coordinates-representing-the-centroid-of-the-item-in-latlong-anyof-1.md "check type definition")

## proj\_\_shape



`proj__shape`

* is optional

* Type: merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md "airs_model#/$defs/Properties/properties/proj__shape")

### proj\_\_shape Type

merged type ([Number of pixels in Y and X directions for the default grid.](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid.md))

any of

* [Untitled array in Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-number-of-pixels-in-y-and-x-directions-for-the-default-grid-anyof-1.md "check type definition")

## proj\_\_transform



`proj__transform`

* is optional

* Type: merged type ([The affine transformation coefficients for the default grid.](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md "airs_model#/$defs/Properties/properties/proj__transform")

### proj\_\_transform Type

merged type ([The affine transformation coefficients for the default grid.](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid.md))

any of

* [Untitled array in Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-affine-transformation-coefficients-for-the-default-grid-anyof-1.md "check type definition")

## generated\_\_has\_overview



`generated__has_overview`

* is optional

* Type: merged type ([Whether the item has an overview or not.](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md "airs_model#/$defs/Properties/properties/generated__has_overview")

### generated\_\_has\_overview Type

merged type ([Whether the item has an overview or not.](model-defs-properties-properties-whether-the-item-has-an-overview-or-not.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-an-overview-or-not-anyof-1.md "check type definition")

## generated\_\_has\_thumbnail



`generated__has_thumbnail`

* is optional

* Type: merged type ([Whether the item has a thumbnail or not.](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md "airs_model#/$defs/Properties/properties/generated__has_thumbnail")

### generated\_\_has\_thumbnail Type

merged type ([Whether the item has a thumbnail or not.](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-thumbnail-or-not-anyof-1.md "check type definition")

## generated\_\_has\_metadata



`generated__has_metadata`

* is optional

* Type: merged type ([Whether the item has a metadata file or not.](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md "airs_model#/$defs/Properties/properties/generated__has_metadata")

### generated\_\_has\_metadata Type

merged type ([Whether the item has a metadata file or not.](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-metadata-file-or-not-anyof-1.md "check type definition")

## generated\_\_has\_data



`generated__has_data`

* is optional

* Type: merged type ([Whether the item has a data file or not.](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md "airs_model#/$defs/Properties/properties/generated__has_data")

### generated\_\_has\_data Type

merged type ([Whether the item has a data file or not.](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-data-file-or-not-anyof-1.md "check type definition")

## generated\_\_has\_cog



`generated__has_cog`

* is optional

* Type: merged type ([Whether the item has a cog or not.](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md "airs_model#/$defs/Properties/properties/generated__has_cog")

### generated\_\_has\_cog Type

merged type ([Whether the item has a cog or not.](model-defs-properties-properties-whether-the-item-has-a-cog-or-not.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-cog-or-not-anyof-1.md "check type definition")

## generated\_\_has\_zarr



`generated__has_zarr`

* is optional

* Type: merged type ([Whether the item has a zarr or not.](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md "airs_model#/$defs/Properties/properties/generated__has_zarr")

### generated\_\_has\_zarr Type

merged type ([Whether the item has a zarr or not.](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not.md))

any of

* [Untitled boolean in Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-whether-the-item-has-a-zarr-or-not-anyof-1.md "check type definition")

## generated\_\_date\_keywords



`generated__date_keywords`

* is optional

* Type: merged type ([A list of keywords indicating clues on the date](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md "airs_model#/$defs/Properties/properties/generated__date_keywords")

### generated\_\_date\_keywords Type

merged type ([A list of keywords indicating clues on the date](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date.md))

any of

* [Untitled array in Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-a-list-of-keywords-indicating-clues-on-the-date-anyof-1.md "check type definition")

## generated\_\_day\_of\_week



`generated__day_of_week`

* is optional

* Type: merged type ([Day of week.](model-defs-properties-properties-day-of-week.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-day-of-week.md "airs_model#/$defs/Properties/properties/generated__day_of_week")

### generated\_\_day\_of\_week Type

merged type ([Day of week.](model-defs-properties-properties-day-of-week.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-day-of-week-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-day-of-week-anyof-1.md "check type definition")

## generated\_\_day\_of\_year



`generated__day_of_year`

* is optional

* Type: merged type ([Day of year.](model-defs-properties-properties-day-of-year.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-day-of-year.md "airs_model#/$defs/Properties/properties/generated__day_of_year")

### generated\_\_day\_of\_year Type

merged type ([Day of year.](model-defs-properties-properties-day-of-year.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-day-of-year-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-day-of-year-anyof-1.md "check type definition")

## generated\_\_hour\_of\_day



`generated__hour_of_day`

* is optional

* Type: merged type ([Hour of day.](model-defs-properties-properties-hour-of-day.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-hour-of-day.md "airs_model#/$defs/Properties/properties/generated__hour_of_day")

### generated\_\_hour\_of\_day Type

merged type ([Hour of day.](model-defs-properties-properties-hour-of-day.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-hour-of-day-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-hour-of-day-anyof-1.md "check type definition")

## generated\_\_minute\_of\_day



`generated__minute_of_day`

* is optional

* Type: merged type ([Minute of day.](model-defs-properties-properties-minute-of-day.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-minute-of-day.md "airs_model#/$defs/Properties/properties/generated__minute_of_day")

### generated\_\_minute\_of\_day Type

merged type ([Minute of day.](model-defs-properties-properties-minute-of-day.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-minute-of-day-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-minute-of-day-anyof-1.md "check type definition")

## generated\_\_month



`generated__month`

* is optional

* Type: merged type ([Month](model-defs-properties-properties-month.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-month.md "airs_model#/$defs/Properties/properties/generated__month")

### generated\_\_month Type

merged type ([Month](model-defs-properties-properties-month.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-month-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-month-anyof-1.md "check type definition")

## generated\_\_year



`generated__year`

* is optional

* Type: merged type ([Year](model-defs-properties-properties-year.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-year.md "airs_model#/$defs/Properties/properties/generated__year")

### generated\_\_year Type

merged type ([Year](model-defs-properties-properties-year.md))

any of

* [Untitled integer in Item](model-defs-properties-properties-year-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-year-anyof-1.md "check type definition")

## generated\_\_season



`generated__season`

* is optional

* Type: merged type ([Season](model-defs-properties-properties-season.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-season.md "airs_model#/$defs/Properties/properties/generated__season")

### generated\_\_season Type

merged type ([Season](model-defs-properties-properties-season.md))

any of

* [Untitled string in Item](model-defs-properties-properties-season-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-season-anyof-1.md "check type definition")

## generated\_\_tltrbrbl



`generated__tltrbrbl`

* is optional

* Type: merged type ([The coordinates of the top left, top right, bottom right, bottom left corners of the item.](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md "airs_model#/$defs/Properties/properties/generated__tltrbrbl")

### generated\_\_tltrbrbl Type

merged type ([The coordinates of the top left, top right, bottom right, bottom left corners of the item.](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item.md))

any of

* [Untitled array in Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-the-coordinates-of-the-top-left-top-right-bottom-right-bottom-left-corners-of-the-item-anyof-1.md "check type definition")

## generated\_\_band\_common\_names



`generated__band_common_names`

* is optional

* Type: merged type ([List of the band common names.](model-defs-properties-properties-list-of-the-band-common-names.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-list-of-the-band-common-names.md "airs_model#/$defs/Properties/properties/generated__band_common_names")

### generated\_\_band\_common\_names Type

merged type ([List of the band common names.](model-defs-properties-properties-list-of-the-band-common-names.md))

any of

* [Untitled array in Item](model-defs-properties-properties-list-of-the-band-common-names-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-list-of-the-band-common-names-anyof-1.md "check type definition")

## generated\_\_band\_names



`generated__band_names`

* is optional

* Type: merged type ([List of the band names.](model-defs-properties-properties-list-of-the-band-names.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-list-of-the-band-names.md "airs_model#/$defs/Properties/properties/generated__band_names")

### generated\_\_band\_names Type

merged type ([List of the band names.](model-defs-properties-properties-list-of-the-band-names.md))

any of

* [Untitled array in Item](model-defs-properties-properties-list-of-the-band-names-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-list-of-the-band-names-anyof-1.md "check type definition")

## generated\_\_geohash2



`generated__geohash2`

* is optional

* Type: merged type ([Geohash on the first two characters.](model-defs-properties-properties-geohash-on-the-first-two-characters.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-geohash-on-the-first-two-characters.md "airs_model#/$defs/Properties/properties/generated__geohash2")

### generated\_\_geohash2 Type

merged type ([Geohash on the first two characters.](model-defs-properties-properties-geohash-on-the-first-two-characters.md))

any of

* [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-two-characters-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-two-characters-anyof-1.md "check type definition")

## generated\_\_geohash3



`generated__geohash3`

* is optional

* Type: merged type ([Geohash on the first three characters.](model-defs-properties-properties-geohash-on-the-first-three-characters.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-geohash-on-the-first-three-characters.md "airs_model#/$defs/Properties/properties/generated__geohash3")

### generated\_\_geohash3 Type

merged type ([Geohash on the first three characters.](model-defs-properties-properties-geohash-on-the-first-three-characters.md))

any of

* [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-three-characters-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-three-characters-anyof-1.md "check type definition")

## generated\_\_geohash4



`generated__geohash4`

* is optional

* Type: merged type ([Geohash on the first four characters.](model-defs-properties-properties-geohash-on-the-first-four-characters.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-geohash-on-the-first-four-characters.md "airs_model#/$defs/Properties/properties/generated__geohash4")

### generated\_\_geohash4 Type

merged type ([Geohash on the first four characters.](model-defs-properties-properties-geohash-on-the-first-four-characters.md))

any of

* [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-four-characters-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-four-characters-anyof-1.md "check type definition")

## generated\_\_geohash5



`generated__geohash5`

* is optional

* Type: merged type ([Geohash on the first five characters.](model-defs-properties-properties-geohash-on-the-first-five-characters.md))

* cannot be null

* defined in: [Item](model-defs-properties-properties-geohash-on-the-first-five-characters.md "airs_model#/$defs/Properties/properties/generated__geohash5")

### generated\_\_geohash5 Type

merged type ([Geohash on the first five characters.](model-defs-properties-properties-geohash-on-the-first-five-characters.md))

any of

* [Untitled string in Item](model-defs-properties-properties-geohash-on-the-first-five-characters-anyof-0.md "check type definition")

* [Untitled null in Item](model-defs-properties-properties-geohash-on-the-first-five-characters-anyof-1.md "check type definition")

## Additional Properties

Additional properties are allowed and do not have to follow a specific schema
