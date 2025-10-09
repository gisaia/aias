#!/usr/bin/env sh
set -o errexit

if [ "$#" -lt 2 ]; then
    echo "You must provide at least the version as first argument and a list of images (e.g. agate)."
    echo "Usage: ./test/build_and_push_on_kind.sh <version> <image1> [ <image2> ...]"
    exit 1
fi
VERSION=$1

shift
IMAGES=$@

for image in $IMAGES; do
    echo "Build and push image $image with version $VERSION on kind"
    docker build -f docker/Dockerfile-$image -t gisaia/$image:$VERSION . ; kind load docker-image gisaia/$image:$VERSION --name arlas-kind-cluster
done
