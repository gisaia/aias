## APROC Configuration

The APROC Configuration is done in the following files:

- [`conf/aproc.yaml`](#aproc-configuration-reference-documentation) for configuring the APROC framework, the drivers registrations and the storage access manager.
- [`conf/drivers.yaml`](#aproc-ingestion-drivers-reference-documentation) for configuring the ingestion process
- [`conf/download.yaml`](#aproc-download-drivers-reference-documentation) for configuring the download process
- [`conf/enrich.yaml`](#aproc-enrich-drivers-reference-documentation) for configuring the enrichment process
- [`conf/dc3build.yaml`](#aproc-datacube-build-drivers-reference-documentation) for configuring the datacube building process

## Framework Configuration

The [`conf/aproc.yaml`](#aproc-configuration-reference-documentation) set the configuration of the APROC framework for:
- framework's dependencies on celery and AIRS
- the registration of the process drivers
- the storages access management

Example of configuration for the framework dependencies:

```yaml
# The message queue used for dispatching the tasks
celery_broker_url: pyamqp://guest:guest@127.0.0.1:5672// 
# The backend database for storing the tasks
celery_result_backend: redis://127.0.0.1:6379/0
# ARLAS Item Registration Service (AIRS) endpoint
airs_endpoint: http://127.0.0.1:8000/arlas/airs
```

The APROC driver registration section lists the Processes drivers and their respective configuration files, e.g.:

```yaml
processes:
  -
    name: ingest
    class_name: extensions.aproc.proc.ingest.ingest_process
    configuration:
      drivers: conf/drivers.yaml
```

### Storage access configuration

The access manager configuration specifies which storages can be accessed and how. The example below declares 3 storages: one local, one on google object storage and one on S3:

```yaml
access_manager:
  tmp_dir: /tmp/
  storages:
    -
      type: file
      writable_paths:
        - /tmp
        - /outbox
      readable_paths:
        - /inputs
    -
      type: gs
      bucket: gisaia-public
    -
      type: s3
      bucket: arlas
      endpoint: "https://s3.my.cloud.provider.com"
      region: eu-1
      api_key:
        access_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        secret_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Four types of storage are available:
- [`file`](#aias_common.configuration.FileStorageConfiguration): local file storage
- [`gs`](#aias_common.configuration.GoogleStorageConfiguration): google cloud object storage
- [`s3`](#aias_common.configuration.S3StorageConfiguration): S3 compliant object storage
- [`http`](#aias_common.configuration.HttpStorageConfiguration): HTTP/HTTPS storage

## Ingest drivers

The [`conf/drivers.yaml`](#aproc-ingestion-drivers-reference-documentation) configuration file references the ingest drivers. The example below register one DIMAP driver. Ingestion can be done only in a directory contained in a referenced storage (see [Storage access configuration](#storage-access-configuration)). The driver that supports the archive and that has the smallest priority number is used for ingestion.

```yaml
# The directory that can be explored for ingestion
inputs_directory: gs://gisaia-public/inputs
# The maximum number of archive that can be ingested in one request (the request will create as many jobs as archives found)
max_number_of_archive_for_ingest: 1000000
# The APROC endpoint for submission of sub requests
aproc_endpoint: $APROC_ENDPOINT_FROM_APROC|http://localhost:8001
resource_id_hash_starts_at: $APROC_RESOURCE_ID_HASH_STARTS_AT|1

drivers:
  -
    name: dimap
    class_name: extensions.aproc.proc.ingest.drivers.impl.dimap
    assets_dir: /tmp/aproc/dimap
    configuration:
    priority: 1
```
## Download drivers
The [`conf/download.yaml`](#aproc-download-drivers-reference-documentation) configuration file lists the drivers for exporting archives. When a download request is received, the archive is transformed and placed in the outbox directory, which can be on the local file storage or on a S3 bucket. ARLAS Server is used to check whether the user requesting the download is allowed to access the archive. If SMTP is configured, then emails are sent to the administrator and to the users requesting the downloads. Download requests are logged in an ARLAS Collection so that the administrator gets a clear view of what is downloaded.

Just like the ingest drivers, download driver registration must set a priority. The driver that supports the item download request and that has the smallest priority is used for the download.

## Enrich drivers

The [`conf/enrich.yaml`](#aproc-enrich-drivers-reference-documentation) configuring file registers the enrichment drivers. An enrichment driver adds an asset to an existing item.

## dc3build drivers

- [`conf/dc3build.yaml`](#aproc-datacube-build-drivers-reference-documentation) configuration file references the drivers for building a datacube based on a list of items.


## Reference documentation

### APROC Configuration reference documentation

::: aproc.settings

### AccessManager Configuration reference documentation

::: aias_common.configuration

### APROC Ingestion drivers reference documentation

::: aproc.ingest

### APROC Download drivers reference documentation

::: aproc.download

### APROC enrich drivers reference documentation

::: aproc.enrich

### APROC datacube build drivers reference documentation

::: aproc.dc3build
