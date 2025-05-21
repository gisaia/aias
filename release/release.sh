#!/bin/bash
set -o errexit
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1
echo "Build and release the image with version ${VERSION}"

send_chat_message(){
    MESSAGE=$1
    if [ -z "$GOOGLE_CHAT_RELEASE_CHANEL" ] ; then
        echo "Environment variable GOOGLE_CHAT_RELEASE_CHANEL is not defined ... skipping message publishing"
    else
        DATA='{"text":"'${MESSAGE}'"}'
        echo $DATA
        curl -X POST --header "Content-Type:application/json" $GOOGLE_CHAT_RELEASE_CHANEL -d "${DATA}"
    fi
}

cd angular/file-explorer
npm --no-git-tag-version version ${VERSION}
cd -

./release/build_docker_images.sh $VERSION
./release/publish_docker_images.sh $VERSION


# Clean target folder
rm -rf target
export PYTHONPATH=`pwd`:`pwd`/python/extensions:`pwd`/test

# Generate documentation
#./mkDocs.sh

# PYTHON PIP
./release/publish.sh $VERSION

# FILE EXPLORER
git add angular/file-explorer/package.json
git add angular/file-explorer/package-lock.json
# DOCUMENTATION
git add docs/
git commit -m "update docs for version "$VERSION
git push origin
git tag -a ${VERSION} -m "ARLAS Item Registration Services Model ${VERSION}"
git push origin ${VERSION}

send_chat_message "Release of AIAS, version ${VERSION}"
