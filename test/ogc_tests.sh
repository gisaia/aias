#!/bin/bash

python3 test/ogc/app.py &
sleep 5
python3 test/ogc_tests.py
