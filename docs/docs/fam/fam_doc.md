# ARLAS File and Archive Management (FAM)

FAM is ARLAS File and Archive Management service. The endpoint lists files in a directory and can list contained archives.


For more details, see the [FAM API documentation](fam_api.md)

## Using FAM

In the following examples, we will:

- list files in `DIMAP`
- list archives in `DIMAP`

!!! note
    The service is deployed on `ARLAS_ENDPOINT`

### Listing __files__ in `DIMAP`

```shell
curl -X 'POST' \
  '${ARLAS_ENDPOINT}/fam/files' \
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

### Listing __archives__ in `DIMAP`:

```shell
curl -X 'POST' \
  '${ARLAS_ENDPOINT}/fam/archives' \
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