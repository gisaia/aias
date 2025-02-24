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

See [AIAS full documentation](https://docs.arlas.io/external_docs/aias/aias/)

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


## Tests

To run the tests (this will also start the stack):

```shell
./test/tests.sh
```

## Configuration

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
| ARLASEO_MAPPING_URL                                       |
| AIRS_COLLECTION_URL                                    |
| AIRS_PREFIX                                            |
| AIRS_LOGGER_LEVEL                                      |

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

### FAM Configuration

The following environment variables must be set to run FAM:

| Variable                                               |
| ------------------------------------------------------ |
|   INGESTED_FOLDER                                     |
|   FAM_LOGGER_LEVEL                                         |
|   FAM_PREFIX                                         |