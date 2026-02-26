#!/usr/bin/env sh

rm ./test/env.sh
cp test/env_template.sh test/env.sh
cat test/env_fs.sh >> test/env.sh

if [ "$1" = "minio" ] 
then
    rm ./test/env.sh
    cp test/env_template.sh test/env.sh
    cat test/env_minio.sh >> test/env.sh
fi

if [ "$1" = "gs" ] 
then
    rm ./test/env.sh
    cp test/env_template.sh test/env.sh
    cat test/env_gs.sh >> test/env.sh
fi

# Set env variable
. ./test/env.sh
curl https://raw.githubusercontent.com/gisaia/ARLAS-server/refs/heads/master/arlas-commons/src/main/resources/roles.yaml -o conf/roles.yaml
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
