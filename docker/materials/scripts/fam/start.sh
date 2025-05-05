#!/bin/sh
export PYTHONPATH=/app/
python3 -m fam.cli.fam conf/fam.yaml $*
