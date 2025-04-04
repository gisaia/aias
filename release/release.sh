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
    docker build --build-arg version=${VERSION} --platform "linux/amd64" -f Dockerfile-${IMAGE} -t gisaia/${IMAGE}:${VERSION} -t gisaia/${IMAGE}:latest .

    echo "Publishing the image $IMAGE"
    docker login
    docker push gisaia/${IMAGE}:latest
    docker push gisaia/${IMAGE}:${VERSION}
}

send_chat_message(){
    MESSAGE=$1
    if [ -z "$GOOGLE_CHAT_RELEASE_CHANEL" ] ; then
        echo "Environement variable GOOGLE_CHAT_RELEASE_CHANEL is not definied ... skipping message publishing"
    else
        DATA='{"text":"'${MESSAGE}'"}'
        echo $DATA
        curl -X POST --header "Content-Type:application/json" $GOOGLE_CHAT_RELEASE_CHANEL -d "${DATA}"
    fi
}


#---------------    FAM    ----------------

build_and_publish_docker fam

#---------------    APROC    ----------------
build_and_publish_docker aproc-proc

build_and_publish_docker aproc-service

#---------------    AGATE    ----------------

build_and_publish_docker agate

#---------------    AIRS    ----------------
# DOCKER
build_and_publish_docker airs

#---------------    GEODES    ----------------
# DOCKER
build_and_publish_docker stac-geodes

#---------------    FAM WUI   ----------------
prepare_arlas_fam_wui
build_and_publish_docker arlas-fam-wui

# Clean target folder
rm -r target
export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test

# Generate documentation
./mkDocs.sh
# PYTHON PIP
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

send_chat_message "Release of AIAS, version ${VERSION}"
