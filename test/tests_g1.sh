#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f docker/Dockerfile-tests . -t pythontests

# Set env variable
. ./test/env.sh

echo "run test.aproc_download_tests"
docker run --rm -v `pwd`:/app/  --network compose_aias pythontests python3 -m test.aproc_download_tests

./test/stop_stack.sh
