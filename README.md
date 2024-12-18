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