#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f Dockerfile-tests . -t pythontests
./test/start_stack.sh

# Set env variable
. ./test/env.sh

docker network list

echo "run test.aproc_download_tests"
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.aproc_download_tests

echo "run test.aproc_enrich_tests"
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.aproc_enrich_tests

echo "run test.aproc_dc3build_tests"
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.aproc_dc3build_tests

# docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m  test.aproc_ingest_heavyload_tests
./test/stop_stack.sh
