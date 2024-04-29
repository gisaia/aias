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

# Start  minio
docker compose -f docker-compose.yaml up -d --remove-orphans --build --wait

docker compose -f docker-compose.yaml -f docker-compose-tests.yaml up --build --wait
