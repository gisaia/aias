source ./test/env.sh

# Stop the AEOPRS Service
kill $(pgrep Python)

# Stop ES and minio
docker-compose -f test/docker-compose-es-minio.yaml down

pkill -f "celery worker"
rm -rf $ROOT_DIRECTORY"/DIMAP"
