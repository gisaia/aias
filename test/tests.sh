./test/start_stack.sh
# Set env variable
source ./test/env.sh
python3 test/airs_tests.py
python3 test/aproc_ingest_tests.py
python3 test/aproc_download_tests.py
#python3 test/aproc_ingest_heavyload_tests.py
./test/stop_stack.sh