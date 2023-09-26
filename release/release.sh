#!/bin/bash
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1
echo "Build and releas the image with version ${VERSION}"

build_and_publish_docker (){
    IMAGE=$1
    echo "Building the image ..."
    docker build -f Dockerfile-${IMAGE} -t gisaia/${IMAGE}:${VERSION} -t gisaia/${IMAGE}:latest .

    echo "Publishing the image ..."
    docker login
    docker push gisaia/${IMAGE}:latest
    docker push gisaia/${IMAGE}:${VERSION}
}


#---------------    APROC    ----------------
build_and_publish_docker aproc-proc

build_and_publish_docker aproc-service

#---------------    AIRS    ----------------
# DOCKER
build_and_publish_docker airs
exit

# PYTHON PIP
export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test
python3 airs/core/models/utils.py > docs/model/model.schema.json
jsonschema2md -d docs/model/ -o docs/model/
./publish/publish.sh $VERSION

# DOCUMENTATION
git add docs/
git commit -m "update docs for version "$VERSION
git push origin
git tag -a ${VERSION} -m "ARLAS Item Registration Services Model ${VERSION}"
git push origin ${VERSION}

