#!/bin/sh
export PYTHONPATH=/app/
python3 -m agate.cli.agate conf/agate.yaml $*
