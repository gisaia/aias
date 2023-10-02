# Set env variable
source ./test/env.sh
# Copy heavy data for test from gcp bucket
if [ -d "${ROOT_DIRECTORY}/DIMAP" ]; then
    echo "${ROOT_DIRECTORY}/DIMAP exists, files are not downloaded."
else
    gsutil -m cp -r "gs://gisaia-public/DIMAP" $ROOT_DIRECTORY
fi

rm -rf ./outbox
mkdir outbox

# Start  minio
docker-compose -f docker-compose.yaml up  -d minio
#Waiting for minio service up and running
code=""
code_OK="OK"
 while [[ "$code" != *$code_OK* ]];do
    code="$(curl -IL --silent http://localhost:9000/minio/health/live | grep "^HTTP\/")"
    eval "sleep 5"
done

# Start  create buckets, elastic rabbitmq redis airs, aproc
docker-compose -f docker-compose.yaml up --build -d createbuckets elasticsearch rabbitmq smtp4dev redis aproc-processes airs-server aproc-server
# Waiting for elastic ready
code=""
code_OK="OK"
while [[ "$code" != *$code_OK* ]];do
    code="$(curl -IL --silent http://localhost:9200 | grep "^HTTP\/")"
    eval "sleep 5"
done
