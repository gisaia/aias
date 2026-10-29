## AIAS - ARLAS Item and Asset Services

AIAS groups a set of microservices in order to offer functions for ingestion, access and download of archives, STAC Items and Assets. AIAS and ARLAS makes a fully functional catalog.

Functions for ingestion:

- Register a STAC item with its assets : ARLAS Item Registration Services ([AIRS](airs/airs_doc.md))
- Asynchronously register one archive (`/processes/ingest`) or a directory containing archives (`/processes/directory_ingest`) : ARLAS Processing ([APROC](aproc/aproc_doc.md))
- List files and archives from a directory: File and Archive Management ([FAM](fam/fam_doc.md))
- Protect assets from an object store such as seaweedfs: ARLAS Asset Gateway ([AGATE](agate/agate_doc.md))

!!! note
    Some STAC synchronisation scrips are provided. See [STAC Synchronisation](#stac-synchronisation)

Functions for download:

- Asynchronously download one or several archives (`/processes/download`) : ARLAS Processing ([APROC](aproc/aproc_doc.md))

Functions for access:

- Access control on the assets with ARLAS Gateway for Assets ([AGATE](agate/agate_doc.md))
