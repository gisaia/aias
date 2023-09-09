./test/start_stack.sh
python3 test/service_tests.py
python3 test/ingest_tests.py
#python3 test/ingest_heavyload_tests.py
./test/stop_stack.sh
