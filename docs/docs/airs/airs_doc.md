# ARLAS Item Registration Services (AIRS)

ARLAS Item Registration Services offers registration services for Spatio-temporal assets. It manages Items as well as Assets (e.g. raster files, cogs, etc.). 

The service exposes the STAC-T methods [github.com/stac-api-extensions/transaction](https://github.com/stac-api-extensions/transaction) as well as a set of methods for handling the assets.

By default, the service manages the assets. When an item is registered, the service checks that the managed asset exists: the asset must be added before the item. Deleting an item is cascaded on the managed assets. An asset can be unmanaged by setting `asset.airs:managed=False` (or `asset.airs__managed=False`).

## AIRS Data model

The AIRS Model is based on the STAC specifications. It supports the following extensions:

- view
- storage
- eo
- processing
- dc3 (ARLAS Datacube Builder)
- cube
- sar
- proj

Also, metadata are enriched by the service and placed in the `generated` namespace.

Namespaces are prefixes in the key names of the JSON. The `:` is used for separating the namespace and the field name. 

!!! warning
    Since ARLAS does not support the `:` in field names, the character is replaced by `__` for storage and indexation.

For more details, see the [AIRS API documentation](airs_api.md)


## Using AIRS

In the following examples, we will:

- add an asset
- check that it exists
- add an item
- get the item
- delete the item and its asset

### Prerequisites

- minio
- elasticsearch
- docker

See [here](https://hub.docker.com/r/gisaia/airs/tags){:target="_blank"} for the available versions of airs.

!!! note
    The service is deployed on `ARLAS_ENDPOINT` 


### Add an asset

```shell
curl -X POST \
    "${ARLAS_ENDPOINT}/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a/assets/classification?content_type=image/tiff" \
    -F file=@test/inputs/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif
```
Result:
```json
{"msg":"Object has been uploaded to bucket successfully"}
```

### Check that the asset exists

```shell
curl -I \
    "${ARLAS_ENDPOINT}/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a/assets/classification"
```
Result:

```shell
HTTP/1.1 204 No Content
```

### Add an item

```shell
curl -X POST \
    -H "Content-Type: application/json" \
    "${ARLAS_ENDPOINT}/airs/collections/digitalearth.africa/items" \
    -d @test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json
```

Result:
```json
{
   "collection":"digitalearth.africa",
   "catalog":"snow",
   "id":"077cb463-1f68-5532-aa8b-8df0b510231a",
   "geometry":{...},
   "bbox": ...,
   "assets":{
      "classification":{...},
      "arlas_eo_item":{...}
   },
   "properties":{
      "datetime":1640908800.0,
      "start_datetime":1609459200.0,
      "end_datetime":1640908800.0,
      "eo:bands":[
         {
            "name":"classification"
         }
      ],
      "proj:epsg":4326,
      "proj:shape":[
         36000.0,
         36000.0
      ],
      "generated:day_of_week":4,
      "generated:day_of_year":365,
      "generated:hour_of_day":1,
      "generated:minute_of_day":60,
      ...
   }
}
```
### Check the item exists

```shell
curl -X GET \
    -H "Content-Type: application/json" \
    "${ARLAS_ENDPOINT}/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a"
```

Result: same as previous call (registration).

### Delete the item and its assets

```shell
curl -X DELETE \
    -H "Content-Type: application/json" \
    "${ARLAS_ENDPOINT}/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a"
```