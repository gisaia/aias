#!/bin/sh
export PYTHONPATH=/app/
python3 -m airs.cli.airs conf/airs.yaml $*
