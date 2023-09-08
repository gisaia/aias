export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test
export AEOPROCESSES_CONFIGURATION_FILE=`pwd`/test/conf/aeoprocesses.yaml
export ROOT_DIRECTORY=`pwd`/test/inputs
# This script starts a es/minio stack, runs aeoprs, then launches the tests and finally stops the stack
gsutil -m cp -r "gs://gisaia-public/DIMAP" $ROOT_DIRECTORY
./test/start_stack.sh

# Waiting for elastic ready
code=""
code_OK="OK"
while [[ "$code" != *$code_OK* ]];do
    code="$(curl -IL --silent http://localhost:9200 | grep "^HTTP\/")"
    eval "sleep 5"
done
sleep 5
python3 test/service_tests.py

celery -A aeoprocesses.ingest.proc:app worker --concurrency=2 -n worker@%h --loglevel INFO &


python3 test/ingest_tests.py

# Stop the AEOPRS Service
kill $(pgrep Python)

# Stop ES and minio
docker-compose -f test/docker-compose-es-minio.yaml down

pkill -f "celery worker"
rm -rf $ROOT_DIRECTORY"/DIMAP"
