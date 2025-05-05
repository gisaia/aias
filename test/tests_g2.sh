#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f Dockerfile-tests . -t pythontests
./test/start_stack.sh

# Set env variable
. ./test/env.sh

docker network list

echo "run test.airs_tests"
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.airs_tests

echo "run test.agate_tests"
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.agate_tests

echo "run test.fam_tests"
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.fam_tests

echo "run test.aproc_ingest_tests"
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.aproc_ingest_tests


# docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m  test.aproc_ingest_heavyload_tests
./test/stop_stack.sh
