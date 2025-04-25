#!/bin/bash
set -o errexit
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1

publish_docker (){
    IMAGE=$1
    echo "Publishing the image $IMAGE"
    docker login
    docker push gisaia/${IMAGE}:latest
    docker push gisaia/${IMAGE}:${VERSION}
}

publish_docker fam
publish_docker aproc-proc
publish_docker aproc-service
publish_docker agate
publish_docker airs
publish_docker stac-geodes
publish_docker arlas-fam-wui

