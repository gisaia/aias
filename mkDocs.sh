#!/bin/sh -e

# Create target/generated-docs
mkdir -p target/generated-docs
rm -rf target/generated-docs/*

# Generate documentation
docker run -v `pwd`:/app  python:3 /bin/bash -c  "cd /app/; pip3 install pydantic ; python3 -m airs.core.models.utils > /app/docs/docs/model/model.schema.json"
# TODO: Fix the jsonschema2md command in a docker image
# jsonschema2md -d docs/docs/model/ -o docs/docs/model/

cat release/materials/README_head.md > docs/docs/model/README.md
cat docs/model/model.md >> docs/docs/model/README.md

# Copy documentation to target
cp docs/docs/* target/generated-docs/
