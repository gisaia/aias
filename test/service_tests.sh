export PYTHONPATH=`pwd`
# This script starts a es/minio stack, runs aeoprs, then launches the tests and finally stops the stack

./test/start_stack.sh

# Wait a bit then launch the tests
sleep 5
python3 test/service_tests.py

# Stop the AEOPRS Service
kill $(pgrep Python)

# Stop ES and minio
docker-compose -f test/docker-compose-es-minio.yaml down
