#!/usr/bin/env sh
# Set env variable
. ./test/env.sh
# Copy heavy data for test from gcp bucket
if [ -d "${ROOT_DIRECTORY}/DIMAP" ]; then
    echo "${ROOT_DIRECTORY}/DIMAP exists, files are not downloaded."
else
    gsutil -m cp -r "gs://gisaia-public/DIMAP" $ROOT_DIRECTORY
fi

rm -rf ./outbox
mkdir outbox
chmod -R 777 outbox
# Start  minio

export BUCKET_NAME=$AIRS_S3_BUCKET
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-create-bucket.yaml up minio createbuckets -d --build --wait || true
export BUCKET_NAME=$DOWNLOAD_S3_BUCKET
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-create-bucket.yaml up minio createbuckets -d --build --wait || true
export BUCKET_NAME=archives
docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-create-bucket.yaml up minio createbuckets -d --build --wait || true

docker compose -f docker/compose/docker-compose.yaml -f docker/compose/docker-compose-tests.yaml up --build --wait || true
