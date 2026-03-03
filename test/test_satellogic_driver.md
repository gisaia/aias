# Satellogic Driver Local Test

Standalone test for the Satellogic ingest driver. Runs the driver pipeline against a synthetic product without external infrastructure (no Elasticsearch, MinIO, RabbitMQ, etc.).

## Setup

From the `aias/` directory:

```bash
python -m venv .venv
source .venv/bin/activate

pip install \
  setuptools google-cloud-storage smart_open boto3==1.39.11 aioboto3==15.1.0 memory-profiler \
  celery 'celery[redis]' elasticsearch jsonref pillow redis \
  click typer pydantic fastapi uvicorn envyaml \
  requests attrs ecs-logging PyJWT cryptography python-dateutil \
  fastapi-utilities pytz python-multipart \
  numpy shapely rasterio pyproj \
  pygeohash pytest pytest-asyncio psutil
```

`boto3` and `aioboto3` must be pinned to avoid compatibility issues with Python 3.11.

## Run

```bash
cd aias
source .venv/bin/activate
PYTHONPATH=python:$PYTHONPATH python -m pytest test/test_satellogic_driver.py -v
```

## Test Coverage

| Area | Tests | What's checked |
|------|-------|----------------|
| `supports()` | 4 | Valid product, empty dir, missing TOA, missing metadata |
| `identify_assets()` | 2 | 7 assets returned with correct roles; data asset has 4 bands |
| `to_item()` pipeline | 7 | Geometry/bbox, core properties, major/minor metadata, datetime, assets completeness |
| `transform_assets()` output | 2 | Overview and thumbnail match golden reference files (byte-for-byte) |

## Regenerating the Synthetic Product

If `create_test_product.py` is updated, regenerate the ZIP and golden reference files:

```bash
# 1. Regenerate the ZIP
python geo4earth-bmad-docs/providers-api-docs/satellogic/create_test_product.py \
  --synthetic \
  --product-id 20260101_120000_000_SN01_L1D_SR_MS_999999 \
  -o aias/test/inputs/images/SYNTHETIC_20260101_120000_000_SN01_L1D_SR_MS_999999.zip

# 2. Regenerate the golden reference files by running the pipeline
#    and copying the produced overview/thumbnail to:
#      test/inputs/images/expected_satellogic_overview.png
#      test/inputs/images/expected_satellogic_thumbnail.png
#    Then run the tests to confirm they pass.
```
