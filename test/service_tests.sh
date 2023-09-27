./test/start_stack.sh
# Set env variable
source ./test/env.sh
python3 test/service_tests.py
python3 test/ingest_tests.py
#python3 test/ingest_heavyload_tests.py
./test/stop_stack.sh
