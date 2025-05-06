#!/usr/bin/env sh
set -o errexit

PYTHONPATH=`pwd`/python
python3.10 -m stac.geodes_sync show  https://geodes-portal.cnes.fr/api/stac/items  --data-type  MUSCATE_SENTINEL2_SENTINEL2_L2A --max 10
