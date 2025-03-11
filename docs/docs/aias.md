## AIAS - ARLAS Item and Asset Services

AIAS groups a set of microservices in order to offer functions for ingestion, access and download of archives, STAC Items and Assets. AIAS and ARLAS makes a fully functional catalog.

Functions for ingestion:

- Register a STAC item with its assets : ARLAS Item Registration Services ([AIRS](airs/airs_doc.md))
- Asynchronously register one archive (`/processes/ingest`) or a directory containing archives (`/processes/directory_ingest`) : ARLAS Processing ([APROC](aproc/aproc_doc.md))
- List files and archives from a directory: File and Archive Management ([FAM](fam/fam_doc.md))

!!! note
    Some STAC synchronisation scrips are provided. See [STAC Synchronisation](#stac-synchronisation)

Functions for download:

- Asynchronously download one or several archives (`/processes/download`) : ARLAS Processing ([APROC](aproc/aproc_doc.md))

Functions for access:

- Access control on the assets with ARLAS Gateway for Assets ([AGATE](#agate))


### AGATE

AGATE is ARLAS Asset Gateway. It is a service for protecting assets from an object store such as minio.
It must be used as a forward authorisation service.


## STAC Synchronisation

The following synchronisations are available:

- [GEODES](https://geodes.cnes.fr/){:target="_blank"}


### GEODES

To ingest products from the GEODES catalogue into AIRS, the process needs to access the AIRS service. The simplest way is to run the docker container within the same network as AIRS. Below is an example:

```shell
docker run --rm \
  -v `pwd`:/app/  \
  --network arlas-net gisaia/stac-geodes:latest \
  add https://geodes-portal.cnes.fr/api/stac http://airs-server:8000/airs geodes S2L1C \
  --data-type PEPS_S2_L1C \
  --data-type MUSCATE_SENTINEL2_SENTINEL2_L2A \
  --data-type MUSCATE_Snow_SENTINEL2_L2B-SNOW \
  --data-type MUSCATE_WaterQual_SENTINEL2_L2B-WATER \
  --data-type MUSCATE_SENTINEL2_SENTINEL2_L3A \
  --product-level L1C \
  --max 1000
```

To get some help, simply run `docker run --rm --network arlas-net gisaia/stac-geodes:latest add https://geodes-portal.cnes.fr/api/stac --help`
