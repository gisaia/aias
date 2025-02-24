# ARLAS Processes (APROC)

ARLAS Processes (APROC) exposes an OGC API Processes compliant API.

List of processes:

- `ingest` : it ingests an archive.
- `directory_ingest` : it ingests archives found in a directory.
- `download` : it ingests an archive.
- `enrich` : it enriches an item (like adding a cog).

## Ingest process

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

A driver must implement the abstract class [Driver](https://github.com/gisaia/aias/blob/develop/extensions/aproc/proc/ingest/drivers/ingest_driver.py){:target="_blank"}.

!!! warning
    The name of the class within the module __must be__ `Driver`.

The following drivers are available in the `extensions` directory:

- ast_dem
- digitalglobe
- dimap
- geoeye
- rapideye
- spot5
- terrasarx
- geotif and jpeg2000

The drivers are configured in [drivers.yaml](https://github.com/gisaia/aias/blob/develop/conf/drivers.yaml){:target="_blank"}

## Enrich process
The `enrich` process takes a list of tuple collection/item id. The process runs the following step for each item:

- say whether it supports a given archive or not
- create the asset for the given item (done by the driver)
- upload the asset
- update the item

A driver must implement the abstract class [Driver](https://github.com/gisaia/aias/blob/develop/extensions/aproc/proc/enrich/drivers/enrich_driver.py){:target="_blank"}.
The following drivers are available in the `extensions` directory:

- `safe` for sentinel 2 products

The drivers are configured in [enrich_drivers.yaml](https://github.com/gisaia/aias/blob/develop/conf/enrich_drivers.yaml){:target="_blank"}

## Using APROC

### Prerequisites

- python 3.10
- AIRS
- celery backend (redis)
- celery brocker (rabbitmq)
- docker

See [here](https://hub.docker.com/r/gisaia/aproc-service/tags){:target="_blank"} for the available versions of aproc-service and [here](https://hub.docker.com/r/gisaia/aproc-proc/tags){:target="_blank"} for the available versions of aproc-processes

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

The `download` and `directory_download` relies on a driver mechanism. A driver must implement the abstract class [Driver](https://github.com/gisaia/aias/blob/develop/extensions/aproc/proc/download/drivers/download_driver.py){:target="_blank"}. 

Available drivers are

- dimap
- tif_file

#### Using `download`
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

#### Getting the status

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