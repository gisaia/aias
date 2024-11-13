#!/usr/bin/env sh
set -o errexit
docker build -f Dockerfile-tests . -t pythontests
./test/start_stack.sh

# Set env variable
. ./test/env.sh
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.airs_tests
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.aproc_ingest_tests
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.aproc_download_tests
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.aproc_enrich_tests
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.agate_tests
docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m test.fam_tests
# docker run --rm -v `pwd`:/app/  --network aias_aias pythontests python3 -m  test.aproc_ingest_heavyload_tests
./test/stop_stack.sh
