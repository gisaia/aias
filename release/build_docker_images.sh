#!/bin/bash
set -o errexit
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1

build_docker (){
    IMAGE=$1
    # Use only signed images
    export DOCKER_CONTENT_TRUST=1
    echo "Building the image $IMAGE"
    docker build --build-arg version=${VERSION} --platform "linux/amd64" -f docker/Dockerfile-${IMAGE} -t gisaia/${IMAGE}:${VERSION} -t gisaia/${IMAGE}:latest .
    
}

# build_docker agate
# build_docker fam
# build_docker aproc-proc
# build_docker aproc-service
# build_docker airs
# build_docker stac-geodes
 build_docker arlas-fam-wui
