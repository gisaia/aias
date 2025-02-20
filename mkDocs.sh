#!/bin/sh -e

# Create target/generated-docs
mkdir -p target/generated-docs
rm -rf target/generated-docs/*

# Generate AIRS docs
mkdir -p docs/docs/api/airs
mkdir -p docs/docs/api/fam
mkdir -p docs/docs/api/aproc_service

## Run AIAS stack
./test/start_stack.sh

## Get AIRS api json file
i=1; until curl -XGET http://0.0.0.0:8000/openapi.json -o docs/docs/airs/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Get FAM api json file
i=1; until curl -XGET http://0.0.0.0:8005/openapi.json -o docs/docs/fam/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Fet APROC service api file
i=1; until curl -XGET http://0.0.0.0:8001/openapi.json -o docs/docs/aproc_service/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Stop the AIAS stack
./test/stop_stack.sh

# Copy documentation to target
cp -r docs/docs/* target/generated-docs/