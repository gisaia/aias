#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f docker/Dockerfile-tests . -t pythontests

# Set env variable
. ./test/env.sh

docker ps

echo "run test/access_manager_tests"
export PYTHONPATH=python
docker run -e AIRS_S3_ACCESS_KEY_ID=airs -e AIRS_S3_SECRET_ACCESS_KEY=airssecret --rm -v `pwd`:/app/  --network compose_aias pythontests pytest -s "test/access_manager_tests.py"
