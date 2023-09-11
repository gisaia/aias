# ARLAS Item Registration Services

ARLAS Item Registration Services offers registration services for Spatio-temporal assets. It manages Items as well as Assets (e.g. raster files, cogs, etc.).

ARLAS Processes (aproc) aim at offering asynchronous services, among them ingestion services.

AIRS can run without ARLAS Processes, while the later relies on the first.

## AIRS Data model

The AIRS Model is based on the STAC specifications. It supports the folling extensions:
- view
- storage
- eo
- processing
- dc3 (ARLAS Datacube Builder)
- cube
- sar
- proj

Also, metadata are enriched by the service and placed in the `generated` namespace.

Namespaces are prefixes in the key names of the JSON. The `:` is used for seperating the namespace and the field name. Since ARLAS does not support the `:` in field names, the character is replaced by `__` for storage and indexation. 

For more details, see the [model documentation](docs/model/model.md)

## ARLAS Item Registration Services

The services exposes the STAC-T methods (https://github.com/stac-api-extensions/transaction) as well as a set of methods for handling the assets.

STAC-T methods:

| Path                                                   | Content-Type Header | Body                                   | Success Status | Description                                                       |
| ------------------------------------------------------ | ------------------- | -------------------------------------- | -------------- | ----------------------------------------------------------------- |
| `POST /collections/{collectionID}/items`               | `application/json`  | partial Item or partial ItemCollection | 201, 202       | Adds a new item to a collection.                                  |
| `PUT /collections/{collectionId}/items/{featureId}`    | `application/json`  | partial Item                           | 200, 202, 204  | Updates an existing item by ID using a complete item description. |
| `PATCH /collections/{collectionId}/items/{featureId}`  | `application/json`  | partial Item                           | 200, 202, 204  | Updates an existing item by ID using a partial item description.  |
| `DELETE /collections/{collectionID}/items/{featureId}` | n/a                 | n/a                                    | 200, 202, 204  | Deletes an existing item by ID.                                   |

Also, a convenient method is provided to get the item:

| Path                                                   | Content-Type Header | Body                                   | Success Status | Description                                                       |
| ------------------------------------------------------ | ------------------- | -------------------------------------- | -------------- | ----------------------------------------------------------------- |
| `GET /collections/{collectionId}/items/{featureId}`    | `application/json`  |                            | 200, 404  | Returns the item if exists, 404 otherwise.                                         |

Asset methods:

| Path                                                   | Content-Type Header | Body                                   | Success Status | Description                                                       |
| ------------------------------------------------------ | ------------------- | -------------------------------------- | -------------- | ----------------------------------------------------------------- |
| `POST /collections/{collectionID}/items/{featureId}/assets/{asset_name}`      | `application/json`  | Asset file | 200       | Adds a new asset to the data store.                                         |
| `HEAD /collections/{collectionID}/items/{featureId}/assets/{asset_name}`      | `application/json`  |   | 200       | Returns 200 if exists                                                                |
| `DELETE /collections/{collectionID}/items/{featureId}/assets/{asset_name}`      | `application/json`  |  | 200       | Deletes the asset from the data store.                                              |

By default, the service manages the assets. When an item is registered, the service checks that the managed asset exists. This means that the asset must be added before the item. Deleting an item is cascaded on the managed assets. An assest can be unmanged by setting `asset.airs:managed=False` (or `asset.airs__managed=False`)

### Running AIRS

AIRS requires
- python 3.10
- an elasticsearch
- an object store (S3, GS or minio)
- docker and docker compose to run a test stack

#### With your own elasticsearch and minio

To configure AIRS, edit `conf/airs.yaml`. An example is provided in `test/conf/airs.yaml`. Then start the service:

```shell
export PYTHONPATH=`pwd`
python3 airs.py conf/airs.yaml &
```

For more details about the command line, run `python3 airs.py --help` :

```shell                
Usage: airs.py CONFIGURATION_FILE [HOST] [PORT]

  Start the ARLAS Earth Observation Product Registration Service.

Arguments:
  CONFIGURATION_FILE  Configuration file  [required]
  [HOST]              host  [default: 127.0.0.1]
  [PORT]              port  [default: 8000]

  --help                          Show this message and exit.
```

Once the service is up & running, you can browse the service documentation at [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/)

### With docker

Instead of launching the service with python, you can launch it with docker:

```shell                
docker run -d --name airs -p 8000:8000 -e XXX:VVV ... -e XXX:VVV gisaia/airs:latest
```

with `XXX:VVV` the environment variable that you want to specify. The table below lists the variable that you can set:

| Variable                                               |
| ------------------------------------------------------ |
| AIRS_ARLAS_COLLECTION_NAME                          |
| AIRS_ARLAS_URL                                      |
| AIRS_INDEX_ENDPOINT_URL                             |
| AIRS_INDEX_COLLECTION_PREFIX                        |
| AIRS_INDEX_LOGIN                                    |
| AIRS_S3_BUCKET                                      |
| AIRS_S3_ACCESS_KEY_ID                               |
| AIRS_S3_SECRET_ACCESS_KEY                           |
| AIRS_S3_REGION                                      |
| AIRS_S3_TIER                                        |
| AIRS_S3_PLATFORM                                    |
| AIRS_S3_ASSET_HTTP_ENDPOINT_URL                     |
| AIRS_S3_ENDPOINT_URL                                |
| AIRS_MAPPING_URL                                    |
| AIRS_COLLECTION_URL                                 |


#### Stack for tests

If you do not have elasticsearch and minio running, you can start a test stack:
```shell
./test/start_stack.sh 
```

### Using AIRS

In the following examples, we will:
- add an asset
- check that it exists
- add an item
- get the item
- delete the item and its asset

#### Add an asset

```shell
curl -X POST \
    "http://127.0.0.1:8000/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a/assets/classification?content_type=image/tiff" \
    -F file=@test/inputs/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif
```
Result:
```json
{"msg":"Object has been uploaded to bucket successfully"}
```

#### Check that the asset exists

```shell
curl -I \
    "http://127.0.0.1:8000/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a/assets/classification" 
```
Result:

```shell
HTTP/1.1 204 No Content
```

#### Add an item

```shell
curl -X POST \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8000/collections/digitalearth.africa/items" \
    -d @test/inputs/077cb463-1f68-5532-aa8b-8df0b510231a.json
```

Result:
```json
{
   "collection":"digitalearth.africa",
   "catalog":"theia-snow",
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
#### Check the item exists

```shell
curl -X GET \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8000/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a"
```

Result: same as previous call (registration).

#### Delete the item and its assets

```shell
curl -X DELETE \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8000/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a"
```


## ARLAS Processes (aproc)

### How ARLAS Processes work

ARLAS Processes (aproc) exposes an OGC API Processes compliant API (to be implemented).

List of processes:
- `ingest` : it ingest an archive.

### Ingest process

The `ingest` process takes a url pointing at an archive. The process runs the following steps:
- identify the driver for ingestion
- identify the assets to fetch (done by the driver)
- fetch the assets (e.g. copy/download)  (done by the driver)
- transform the assets if necessary (e.g. create cog)  (done by the driver)
- upload the assets
- register the item in AIRS

As mentioned, the process is "driver" based. Each data source must have a compliant driver in order to be ingested in AIRS. A driver has to
- say whether it supports a given archive or not
- identify the archive's assets to be fetched
- fetch the assets
- transform the assets
- create an AIRS Item

A [driver](aproc/ingest/drivers/driver.py) must implement the following methods:

```python
    @staticmethod
    def init(configuration:dict) -> None:

    @staticmethod
    def supports(url:str)->bool:

    def identify_assets(self, url:str)->list[Asset]:

    def fetch_assets(self, url:str, resources:list[Asset])->list[Asset]:

    def transform_assets(self, url:str, resources:list[Asset])->list[Asset]:

    def to_item(self, url:str, resources:list[Asset])->Item:
```

The following drivers are available in the `extensions` directory:
- [theia](extensions/aproc/ingest/drivers/impl/theia.py)

### Running ARLAS Processes (aproc)

ARLAS Processes requires
- python 3.10
- AIRS
- celery backend (redis)
- celery brocker (rabbitmq)
- docker and docker compose for running the tests

The following environment variables must be set to run the celery workers and the service:

| Variable                                               |
| ------------------------------------------------------ |
| APROC_CONFIGURATION_FILE                        |


For starting the service or a celery worker, you need to set two environment variables:

```sh
export PYTHONPATH=pwd:pwd/extensions:pwd/test
export APROC_CONFIGURATION_FILE=pwd/test/conf/aproc.yaml
```

For starting the celery worker:
```sh
celery -A aproc.ingest.proc:app worker --concurrency=2 -n worker@%h --loglevel INFO
```

TODO : implement and document the OGC Processes api

#### Ingest synchronously

Ingestion can be launched synchronously with the ingest command line:

```shell
python3 aproc/ingest/cli.py test/conf/aproc.yaml "https://catalogue.theia-land.fr/arlas/explore/theia/_search?f=metadata.core.identity.identifier%3Aeq%3ASENTINEL2A_20230604-105902-526_L2A_T31TCJ_D&righthand=false&pretty=false&flat=false&size=1" 
```
Note: AIRS must be running.

## Tests

To run the unit tests:

```shell
./test/unit_tests.sh 
```

To run the service tests:
gdal 3.7.X must be available
```shell
./test/service_tests.sh 
```
