#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f docker/Dockerfile-tests . -t pythontests

# Set env variable
. ./test/env.sh

docker ps

echo "run test/access_manager_tests"
export PYTHONPATH=python
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests pytest -s "test/access_manager_tests.py::test_get_rasterio_session[gs://gisaia-public/test-aias/ast/AST_L1B_00307242024224227_20240729075840_2355295.VNIR_Swath.ImageData3N.tfw]"
