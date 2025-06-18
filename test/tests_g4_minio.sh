#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f docker/Dockerfile-tests . -t pythontests

# Set env variable
cp test/env_template.sh test/env.sh
cat test/env_minio.sh >> test/env.sh
. ./test/env.sh

docker network list

echo "run test.aproc_ingest_tests_minio"
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.aproc_ingest_tests_minio Tests.test_ingest_directory || docker logs aproc-processes
