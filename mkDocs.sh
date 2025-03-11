#!/bin/sh -e

# Create target/generated-docs
mkdir -p target/generated-docs
rm -rf target/generated-docs/*

## Run AIAS stack
./test/start_stack.sh

## Get AIRS api json file
i=1; until curl -XGET http://localhost:8000/openapi.json -o docs/docs/airs/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Get FAM api json file
i=1; until curl -XGET http://localhost:8005/openapi.json -o docs/docs/fam/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Get APROC service api file
i=1; until curl -XGET http://localhost:8001/openapi.json -o docs/docs/aproc/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Get AGATE service api file
i=1; until curl -XGET http://localhost:8004/openapi.json -o docs/docs/agate/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done

## Stop the AIAS stack
./test/stop_stack.sh

# Copy documentation to target
cp -r docs/docs/* target/generated-docs/

docker run --rm -u `id -u`:`id -g` -v `pwd`:/data minlag/mermaid-cli -i /data/target/generated-docs/agate/agate-mermaid.md -o /data/target/generated-docs/agate/agate_doc.md
