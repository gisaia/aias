#!/bin/bash
IMAGE=aeoprs
[ -z "$1" ] && echo "Please provide the version" && exit 1;
VERSION=$1
echo "Build and releas the image with version ${VERSION}"

echo "Building the image ..."
docker build -t gisaia/${IMAGE}:${VERSION} -t gisaia/${IMAGE}:latest .

echo "Publishing the image ..."
docker login
docker push gisaia/${IMAGE}:latest
docker push gisaia/${IMAGE}:${VERSION}

python3 aeoprs/core/models/utils.py > docs/model/model.schema.json
jsonschema2md -d docs/model/ -o docs/model/
./publish/publish.sh $VERSION

git add docs/
git commit -m "update docs for version "$VERSION
git push origin
git tag -a ${VERSION} -m "ARLAS Earth Observation Product Registration Services ${VERSION}"
git push origin ${VERSION}
