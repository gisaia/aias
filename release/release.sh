#!/bin/bash
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1
echo "Build and releas the image with version ${VERSION}"

prepare_arlas_fam_wui (){
    cd file-explorer
    npm --no-git-tag-version version ${VERSION}
    cd ../
}

build_and_publish_docker (){
    IMAGE=$1
    echo "Building the image $IMAGE"
    docker build --platform "linux/amd64" -f Dockerfile-${IMAGE} -t gisaia/${IMAGE}:${VERSION} -t gisaia/${IMAGE}:latest .

    echo "Publishing the image $IMAGE"
    docker login
    docker push gisaia/${IMAGE}:latest
    docker push gisaia/${IMAGE}:${VERSION}
}

#---------------    FAM    ----------------

build_and_publish_docker fam

#---------------    FAM WUI   ----------------
prepare_arlas_fam_wui
build_and_publish_docker arlas-fam-wui

#---------------    APROC    ----------------
build_and_publish_docker aproc-proc

build_and_publish_docker aproc-service

#---------------    AGATE    ----------------

build_and_publish_docker agate

#---------------    AIRS    ----------------
# DOCKER
build_and_publish_docker airs


# PYTHON PIP
export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test
docker run -v `pwd`:/app  python:3 /bin/bash -c  "cd /app/; pip3 install pydantic ; python3 -m airs.core.models.utils > /app/docs/model/model.schema.json"
jsonschema2md -d docs/model/ -o docs/model/
./release/publish.sh $VERSION

# FILE EXPLORER
git add file-explorer/package.json
git add file-explorer/package-lock.json
# DOCUMENTATION
git add docs/
git commit -m "update docs for version "$VERSION
git push origin
git tag -a ${VERSION} -m "ARLAS Item Registration Services Model ${VERSION}"
git push origin ${VERSION}

