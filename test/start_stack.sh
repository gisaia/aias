#!/usr/bin/env sh

rm ./test/env.sh
cp test/env_template.sh test/env.sh
cat test/env_fs.sh >> test/env.sh

if [ "$1" = "seaweedfs" ]
then
    rm ./test/env.sh
    cp test/env_template.sh test/env.sh
    cat test/env_seaweedfs.sh >> test/env.sh
    echo "Starting with seaweedFS configuration"
elif [ "$1" = "gs" ]
then
    rm ./test/env.sh
    cp test/env_template.sh test/env.sh
    cat test/env_gs.sh >> test/env.sh
    echo "Starting with Google Storage configuration"
else
    echo "Starting with default file system configuration"
fi

# Set env variable
. ./test/env.sh
curl https://raw.githubusercontent.com/gisaia/ARLAS-server/refs/heads/master/arlas-commons/src/main/resources/roles.yaml -o conf/roles.yaml
rm -rf ./outbox
mkdir outbox
chmod -R 777 outbox

echo "Creating buckets for seaweedFS"
export BUCKET_NAME=$AIRS_S3_BUCKET
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-create-bucket.yaml up seaweedfs createbuckets -d --build --wait || true
export BUCKET_NAME=$DOWNLOAD_S3_BUCKET
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-create-bucket.yaml up seaweedfs createbuckets -d --build --wait || true
export BUCKET_NAME=archives
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-create-bucket.yaml up seaweedfs createbuckets -d --build --wait || true

docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-tests.yaml up --build --wait || true
