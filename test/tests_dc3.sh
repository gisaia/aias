#!/usr/bin/env sh
set -o errexit
echo "build docker image for tests"
docker build -f docker/Dockerfile-tests . -t pythontests

# Set env variable
. ./test/env.sh

echo "run test.aproc_dc3build_tests"
docker run --rm -v `pwd`:/app/ -e AIRS_S3_ACCESS_KEY_ID -e AIRS_S3_SECRET_ACCESS_KEY -e DOWNLOAD_S3_ACCESS_KEY_ID -e DOWNLOAD_S3_SECRET_ACCESS_KEY  --network compose_aias pythontests python3 -m test.aproc_dc3build_tests -v
