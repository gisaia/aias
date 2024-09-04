# AIAS - ARLAS Item and Asset Services

AIAS groups a set of microservices in order to offer functions for ingestion, access and download of archives, STAC Items and Assets. AIAS and ARLAS makes a fully functional catalog.

Functions for ingestion:
- Register a STAC item with its assets : ARLAS Item Registration Services (AIRS)
- Asynchronously register one archive (`/processes/ingest`) or a directory containing archives (`/processes/directory_ingest`) : ARLAS Processing (APROC)
- List files and archives from a directory: File and Archive Management (FAM)


Functions for download:
- Asynchronously download one or several archives (`/processes/download`) : ARLAS Processing (APROC)

Functions for access:
- Access control on the assets with ARLAS Gateway for Assets (AGATE)

## Running the stack

To start a standalone stack for testing:
```shell
./test/start_stack.sh
```
At least 8Go of RAM is needed.

This stack relies on the docker compose configuration files. The available endpoints are:
- [AIRS](http://localhost:8000/docs)
- [APROC](http://localhost:8001/docs)
- [AGATE](http://localhost:8004/docs)
- [FAM](http://localhost:8005/docs)
- [minio](http://localhost:9001/browser)
- [elasticsearch](http://localhost:8200)
- [rabbitmq](http://localhost:15672/)
- redis on port 6379
- [SMTP4DEV](http://localhost:3000/) for email testing

Health checks are available for all non-third party services:
- [AIRS](http://localhost:8000/arlas/airs/healthcheck)
- [APROC](http://localhost:8001/arlas/aproc/healthcheck)
- [AGATE](http://localhost:8004/arlas/agate/healthcheck)
- [FAM](http://localhost:8005/arlas/fam/healthcheck)


# ARLAS Item Registration Services

ARLAS Item Registration Services offers registration services for Spatio-temporal assets. It manages Items as well as Assets (e.g. raster files, cogs, etc.). The service exposes the STAC-T methods (https://github.com/stac-api-extensions/transaction) as well as a set of methods for handling the assets.

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

Namespaces are prefixes in the key names of the JSON. The `:` is used for seperating the namespace and the field name. Since ARLAS does not support the `:` in field names, the character is replaced by `__` for storage and indexation. 

For more details, see the [model documentation](docs/model/model.md)

## Prerequisites

- minio
- elasticsearch
- docker

See [here](https://hub.docker.com/r/gisaia/airs/tags) for the available versions of airs.

### AIRS Configuration

The following environment variables must be set to run AIRS:

| Variable                                               |
| ------------------------------------------------------ |
| AIRS_HOST  |
| AIRS_PORT  |
| AIRS_CORS_ORIGINS  |
| AIRS_CORS_METHODS  |
| AIRS_CORS_HEADERS  |
| AIRS_ARLAS_COLLECTION_NAME                             |
| AIRS_ARLAS_URL                                         |
| AIRS_INDEX_ENDPOINT_URL                                |
| AIRS_INDEX_COLLECTION_PREFIX                           |
| AIRS_INDEX_LOGIN                                       |
| AIRS_INDEX_PWD                                       |
| AIRS_S3_BUCKET                                         |
| AIRS_S3_ACCESS_KEY_ID                                  |
| AIRS_S3_SECRET_ACCESS_KEY                              |
| AIRS_S3_REGION                                         |
| AIRS_S3_TIER                                           |
| AIRS_S3_PLATFORM                                       |
| AIRS_S3_ASSET_HTTP_ENDPOINT_URL                        |
| AIRS_S3_ENDPOINT_URL                                   |
| AIRS_MAPPING_URL                                       |
| AIRS_COLLECTION_URL                                    |
| AIRS_PREFIX                                            |
| AIRS_LOGGER_LEVEL                                      |


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
    "http://127.0.0.1:8000/arlas/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a/assets/classification?content_type=image/tiff" \
    -F file=@test/inputs/ESA_WorldCover_10m_2021_v200_N15E000_Map.tif
```
Result:
```json
{"msg":"Object has been uploaded to bucket successfully"}
```

#### Check that the asset exists

```shell
curl -I \
    "http://127.0.0.1:8000/arlas/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a/assets/classification" 
```
Result:

```shell
HTTP/1.1 204 No Content
```

#### Add an item

```shell
curl -X POST \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8000/arlas/airs/collections/digitalearth.africa/items" \
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
#### Check the item exists

```shell
curl -X GET \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8000/arlas/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a"
```

Result: same as previous call (registration).

#### Delete the item and its assets

```shell
curl -X DELETE \
    -H "Content-Type: application/json" \
    "http://127.0.0.1:8000/arlas/airs/collections/digitalearth.africa/items/077cb463-1f68-5532-aa8b-8df0b510231a"
```

## ARLAS Processes (APROC)

ARLAS Processes (APROC) exposes an OGC API Processes compliant API.

List of processes:
- `ingest` : it ingests an archive.
- `directory_ingest` : it ingests archives found in a directory.
- `download` : it ingests an archive.

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

A driver must implement the abstract class [Driver](extensions/aproc/proc/ingest/drivers/driver.py).

>>> IMPORTANT: The name of the class within the module __must be__ `Driver`.

The following drivers are available in the `extensions` directory:
- ast_dem
- digitalglobe
- dimap
- geoeye
- rapideye
- spot5
- terrasarx
- geotif and jpeg2000

The drivers are configured in [drivers.yaml](conf/drivers.yaml)


## Prerequisites

- python 3.10
- AIRS
- celery backend (redis)
- celery brocker (rabbitmq)
- docker

See [here](https://hub.docker.com/r/gisaia/aproc-service/tags) for the available versions of aproc-service and [here](https://hub.docker.com/r/gisaia/aproc-proc/tags) for the available versions of aproc-processes

### APROC Configuration

The following environment variables must be set to run aproc-service and aproc-proc:

| Variable                                               |
| ------------------------------------------------------ |
| APROC_ENDPOINT_FROM_APROC                              |
| APROC_CONFIGURATION_FILE                               |
| APROC_HOST                                             |
| APROC_PORT                                             |
| CELERY_BROKER_URL                                      |
| CELERY_RESULT_BACKEND                                  |
| AIRS_ENDPOINT                                          |
| APROC_PREFIX                                           |
| APROC_LOGGER_LEVEL                                     |
| ARLAS_URL_SEARCH  |
| APROC_CORS_ORIGINS  |
| APROC_CORS_METHODS  |
| APROC_CORS_HEADERS  |
| AIRS_INDEX_COLLECTION_PREFIX  |
| ARLAS_SMTP_ACTIVATED  |
| ARLAS_SMTP_HOST  |
| ARLAS_SMTP_PORT  |
| ARLAS_SMTP_USERNAME  |
| ARLAS_SMTP_PASSWORD  |
| ARLAS_SMTP_FROM  |
| APROC_DOWNLOAD_ADMIN_EMAILS  |
| APROC_DOWNLOAD_OUTBOX_DIR  |
| APROC_DOWNLOAD_CONTENT_USER  |
| APROC_DOWNLOAD_SUBJECT_USER  |
| APROC_DOWNLOAD_CONTENT_ERROR  |
| APROC_DOWNLOAD_SUBJECT_ERROR  |
| APROC_DOWNLOAD_CONTENT_ADMIN  |
| APROC_DOWNLOAD_SUBJECT_ADMIN  |
| APROC_EMAIL_PATH_PREFIX_ADD  |
| APROC_PATH_TO_WINDOWS  |
| APROC_DOWNLOAD_REQUEST_SUBJECT_USER  |
| APROC_DOWNLOAD_REQUEST_CONTENT_USER  |
| APROC_DOWNLOAD_REQUEST_SUBJECT_ADMIN  |
| APROC_DOWNLOAD_REQUEST_CONTENT_ADMIN  |
| APROC_INDEX_ENDPOINT_URL  |
| APROC_INDEX_NAME  |
| APROC_INDEX_LOGIN  |
| APROC_INDEX_PWD  |
| APROC_RESOURCE_ID_HASH_STARTS_AT  |

### Using `ingest` and `directory_ingest`

#### Add an archive

```shell
curl -X 'POST' \
  'http://localhost:8001/arlas/aproc/processes/ingest/execution' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"inputs": {"collection": "digitalearth.africa", "catalog": "spot6", "url": "/inputs/DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A/", "annotations":""}, "outputs": null, "response": "raw", "subscriber": null}'
```

Result:
```json
{
  "processID": "ingest",
  "type": "process",
  "jobID": "c3300fd2-aed6-4887-b2e9-d5db8ce02ced",
  "status": "accepted",
  "message": "",
  "created": 1698153197,
  "started": null,
  "finished": null,
  "updated": 1698153197,
  "progress": null,
  "links": null,
  "resourceID": "inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A-"
}
```

#### Add archives contained in a directory

```shell
curl -X 'POST' \
  'http://localhost:8001/arlas/aproc/processes/directory_ingest/execution' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"inputs": {"collection": "digitalearth.africa", "catalog": "dimap", "directory": "DIMAP"}, "outputs": null, "response": "raw", "subscriber": null}'
```
Result:
```json
{
  "processID": "directory_ingest",
  "type": "process",
  "jobID": "d288ff3e-e880-43d3-880e-f2725f5f55b2",
  "status": "accepted",
  "message": "",
  "created": 1698153396,
  "started": null,
  "finished": null,
  "updated": 1698153396,
  "progress": null,
  "links": null,
  "resourceID": "DIMAP"
}
```

### Download process

The `download` and `directory_download` relies on a driver mecanism. A driver must implement the abstract class [Driver](extensions/aproc/proc/download/drivers/driver.py). Available drivers are
- dimap
- tif_file

### Using `download`
```shell

curl -X 'POST' \
  'http://localhost:8001/arlas/aproc/processes/download/execution' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"inputs": {"requests": [{"collection": "digitalearth.africa", "item_id": "inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A"}], "crop_wkt": "", "target_projection": "epsg:4326", "target_format": "Geotiff"}}'
```
Result:
```json
{
  "processID": "download",
  "type": "process",
  "jobID": "40154302-4ca7-468c-854d-c09b245e3e64",
  "status": "accepted",
  "message": "",
  "created": 1698154319,
  "started": null,
  "finished": null,
  "updated": 1698154319,
  "progress": null,
  "links": null,
  "resourceID": "db6bd405d357b8f6420bfe6797bbbec1e6430afe"
}
```

### Getting the status

To get the status of one running process (job):
```shell
curl -X 'GET' \
  'http://localhost:8001/arlas/aproc/jobs/40154302-4ca7-468c-854d-c09b245e3e64' \
  -H 'accept: application/json'
```
Result:
```json
{
  "processID": "download",
  "type": "process",
  "jobID": "40154302-4ca7-468c-854d-c09b245e3e64",
  "status": "successful",
  "message": "{'download_location': '/outbox/anonymous/inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A/inputs_DIMAP_PROD_SPOT6_001_VOL_SPOT6_001_A_IMG_SPOT6_MS_001_A.Geotiff'}",
  "created": 1698154319,
  "started": 1698154319,
  "finished": 1698154440,
  "updated": 1698154440,
  "progress": null,
  "links": null,
  "resourceID": "db6bd405d357b8f6420bfe6797bbbec1e6430afe"
}
```


To get the status of the process for one resource (item id for an ingest):
```shell
curl -X 'GET' \
  'http://localhost:8001/arlas/aproc/jobs/resources/inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A' \
  -H 'accept: application/json'
```
Result:
```json
[
  {
    "processID": "ingest",
    "type": "process",
    "jobID": "efd65a52-78c3-4fbd-9f2b-40bb726de1ca",
    "status": "failed",
    "message": "",
    "created": 1698153257,
    "started": 1698153257,
    "finished": 1698153257,
    "updated": 1698153257,
    "progress": null,
    "links": null,
    "resourceID": "inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A"
  },
  ...
  {
    "processID": "ingest",
    "type": "process",
    "jobID": "d79ae63b-79dd-4a6c-a93a-ee2924575d1e",
    "status": "successful",
    "message": "{'item_location': 'http://airs-server:8000/arlas/airs/collections/digitalearth.africa/items/inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A'}",
    "created": 1698153397,
    "started": 1698153397,
    "finished": 1698153397,
    "updated": 1698153397,
    "progress": null,
    "links": null,
    "resourceID": "inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A"
  }
]
```

To get the status of the most recent processes for ingest and which are running:

```shell
curl -X 'GET' \
  'http://localhost:8001/arlas/aproc/jobs?offset=0&limit=10&process_id=ingest&status=running' \
  -H 'accept: application/json'
```
Result:
```json
{
    "status_list": [
        {
            "processID": "ingest",
            "type": "process",
            "jobID": "c8c79f8e-51c9-4a99-96e2-527cc365cb1d",
            "status": "successful",
            "message": "{'item_location': 'http://airs-server:8000/arlas/airs/collections/digitalearth.africa/items/SENTINEL2A_20230604-105902-526_L2A_T31TCJ_D'}",
            "created": 1698400307,
            "started": 1698400320,
            "finished": 1698400327,
            "updated": 1698400327,
            "resourceID": "SENTINEL2A_20230604-105902-526_L2A_T31TCJ_D"
        },
        ...
    ],
    "total": 41
}
```


## AGATE

AGATE is ARLAS Asset Gateway. It is a service for protecting assets from an object store such as minio. It must be used as a forward authorisation service.

| Variable                                               |
| ------------------------------------------------------ |
|   ARLAS_URL_SEARCH                                     |
|   AGATE_PREFIX                                         |
|   AGATE_HOST                                           |
|   AGATE_PORT                                   |
|   AGATE_ENDPOINT                                       |
|   AGATE_URL_HEADER                                     |
|   AGATE_URL_HEADER_PREFIX                              |
|   AGATE_LOGGER_LEVEL                                   |
|   AGATE_CORS_ORIGINS                                   |
|   AGATE_CORS_METHODS                                   |
|   AGATE_CORS_HEADERS                                   |


## FAM

FAM is ARLAS File and Archive Management service. The endpoint lists files in a directory and can list contained archives.


| Variable                                               |
| ------------------------------------------------------ |
|   INGESTED_FOLDER                                     |
|   FAM_LOGGER_LEVEL                                         |
|   FAM_PREFIX                                         |

Example for listing __files__ in `DIMAP`:

```shell
curl -X 'POST' \
  'http://localhost:8005/arlas/fam/files' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "path": "DIMAP",
  "size": 10
}'
```
Returns
```json
[
  {
    "name": ".DS_Store",
    "path": "DIMAP/.DS_Store",
    "is_dir": false,
    "last_modification_date": "2023-09-29T19:14:05.037229",
    "creation_date": "2023-09-29T19:14:05.037771"
  },
  {
    "name": "PROD_SPOT6_001",
    "path": "DIMAP/PROD_SPOT6_001",
    "is_dir": true,
    "last_modification_date": "2023-09-29T19:14:05.082518",
    "creation_date": "2023-09-29T19:14:05.082518"
  }
]
```


Example for listing __archives__ in `DIMAP`:

```shell
curl -X 'POST' \
  'http://localhost:8005/arlas/fam/archives' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "path": "DIMAP",
  "size": 10
}'
```
Returns
```json
[
  {
    "name": "IMG_SPOT6_MS_001_A",
    "path": "DIMAP/PROD_SPOT6_001/VOL_SPOT6_001_A/IMG_SPOT6_MS_001_A",
    "is_dir": true,
    "last_modification_date": "2023-09-29T19:15:20.930201",
    "creation_date": "2023-09-29T19:15:20.930201",
    "id": "inputs-DIMAP-PROD_SPOT6_001-VOL_SPOT6_001_A-IMG_SPOT6_MS_001_A",
    "driver_name": "dimap"
  }
]
```

# Tests

To run the tests (this will also start the stack):

```shell
./test/tests.sh 
```
