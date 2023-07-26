# Start ES and minio
docker-compose -f test/docker-compose-es-minio.yaml up -d


# Wait a bit then launch the AEOPRS Service
sleep 5
export PYTHONPATH=`pwd`
python3 aeoprs.py test/conf/aeoprs.yaml &
