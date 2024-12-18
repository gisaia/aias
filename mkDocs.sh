#!/bin/sh -e

# Create target/generated-docs
mkdir -p target/generated-docs
rm -rf target/generated-docs/*

# Generate model schema json file
docker run -v `pwd`:/app  python:3 /bin/bash -c  "cd /app/; pip3 install pydantic ; python3 -m airs.core.models.utils > /app/docs/docs/model/model.schema.json"
# Generate model documentation
docker run --rm -v `pwd`:/schema gisaia/jsonschema2md:latest -d /schema/docs/docs/model/ -o /schema/docs/docs/model/ -x -

# Overwrite generated model README
cat release/materials/README_head.md > docs/docs/model/README.md
cat docs/docs/model/model.md >> docs/docs/model/README.md

# Copy documentation to target
cp docs/docs/* target/generated-docs/
