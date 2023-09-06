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

export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test
export AEOPROCESSES_CONFIGURATION_FILE=`pwd`/test/conf/aeoprocesses.yaml
python3 aeoprs.py test/conf/aeoprs.yaml &
