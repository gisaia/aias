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

# Get Pydantic Settings models
cp python/agate/settings.py target/generated-docs/agate/settings.py
mkdir -p target/generated-docs/aias_common
cp python/aias_common/access/configuration.py target/generated-docs/aias_common/configuration.py
cp python/airs/core/settings.py target/generated-docs/airs/settings.py
cp python/aproc/core/settings.py target/generated-docs/aproc/settings.py
cp python/fam/core/settings.py target/generated-docs/fam/settings.py
cp python/extensions/aproc/proc/ingest/settings.py target/generated-docs/aproc/ingest.py
cp python/extensions/aproc/proc/download/settings.py target/generated-docs/aproc/download.py
cp python/extensions/aproc/proc/enrich/settings.py target/generated-docs/aproc/enrich.py
cp python/extensions/aproc/proc/dc3build/settings.py target/generated-docs/aproc/dc3build.py

pip3.10 install lazydocs

export PYTHONPATH=python

pip3.10 install -r python/aias_common/requirements.aias_common.txt
lazydocs \
    aias_common.access.manager \
    aias_common.access.configuration \
    aias_common.access.storages.abstract \
    aias_common.access.storages.file \
    aias_common.access.storages.gs \
    aias_common.access.storages.http \
    aias_common.access.storages.https \
    aias_common.access.storages.utils \
    --output-path target/aias_common/pydoc/ \
    --overview-file modules.md


lazydocs \
    airs.core.models.model \
    airs.core.models.mapper \
    --output-path target/airs/pydoc/ \
    --overview-file modules.md

docker run --rm -u `id -u`:`id -g` -v `pwd`:/data minlag/mermaid-cli -i /data/target/generated-docs/agate/agate-mermaid.md -o /data/target/generated-docs/agate/agate_doc.md
