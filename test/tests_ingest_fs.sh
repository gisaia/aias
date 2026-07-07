#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f docker/Dockerfile-tests . -t pythontests

# Set env variable
. ./test/env.sh

docker network list

echo "run test.aproc_ingest_tests"
docker run --name somewhere  --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.aproc_ingest_tests

echo "run test.aproc_ingest_tests_filesystem"
docker run --name somewhere --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.aproc_ingest_tests_filesystem
