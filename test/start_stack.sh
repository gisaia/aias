source ./test/env.sh

# This script starts a es/minio stack, runs aeoprs, then launches the tests and finally stops the stack
gsutil -m cp -r "gs://gisaia-public/DIMAP" $ROOT_DIRECTORY

# Start  minio
docker-compose -f test/docker-compose-es-minio.yaml up  -d minio
#Waiting for minio service up and running
code=""
code_OK="OK"
 while [[ "$code" != *$code_OK* ]];do
    code="$(curl -IL --silent http://localhost:9000/minio/health/live | grep "^HTTP\/")"
    eval "sleep 5"
done
# Start  create buckets
docker-compose -f test/docker-compose-es-minio.yaml up -d createbuckets
# Start  elastic rabbitmq redis
docker-compose -f test/docker-compose-es-minio.yaml up -d

python3 aeoprs.py test/conf/aeoprs.yaml &

# Waiting for elastic ready
code=""
code_OK="OK"
while [[ "$code" != *$code_OK* ]];do
    code="$(curl -IL --silent http://localhost:9200 | grep "^HTTP\/")"
    eval "sleep 5"
done
celery -A aeoprocesses.ingest.proc:app worker --concurrency=2 -n worker@%h --loglevel INFO &
sleep 5
