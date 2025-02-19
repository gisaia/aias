#!/bin/sh -e

# Create target/generated-docs
mkdir -p target/generated-docs
rm -rf target/generated-docs/*

# Generate AIRS docs
## Get AIRS api json file
mkdir -p docs/docs/api
docker run -d --name airs -e AIRS_HOST="0.0.0.0" -p 8000:8000 gisaia/airs
i=1; until curl -XGET http://0.0.0.0:8000/openapi.json -o docs/docs/api/openapi.json; do if [ $i -lt 60 ]; then sleep 1; else break; fi; i=$(($i + 1)); done
docker stop airs
docker rm airs

## Generate AIRS docs as docs/docs/api/reference.md file
docker run --rm \
    --mount dst=/input/api.json,src="$PWD/docs/docs/api/openapi.json",type=bind,ro \
    --mount dst=/input/env.json,src="$PWD/conf/doc/widdershins.json",type=bind,ro \
    --mount dst=/output,src="$PWD/docs/docs/api",type=bind \
	gisaia/widdershins:4.0.1
rm docs/docs/api/openapi.json

# Copy documentation to target
cp -r docs/docs/* target/generated-docs/