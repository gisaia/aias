#!/usr/bin/env sh
set -o errexit

if test -f "$HOME/.pypirc"; then
    echo "$HOME/.pypirc found."
else
    echo "$HOME/.pypirc does not exists. Please create it and set the username/password".
    exit 1
fi

# AIRS
mkdir -p target/airs
rm -rf target/airs/*
mkdir -p target/airs/src/airs/core/models
cp -r airs/core/models/* target/airs/src/airs/core/models
cp -r release/materials/airs/* target/airs/
sed -i.bak 's/aias_version/\"'$1'\"/' target/airs/setup.py


cd target/airs

docker run \
        -e GROUP_ID="$(id -g)" \
        -e USER_ID="$(id -u)" \
        --mount dst=/opt/python,src="$PWD",type=bind \
        --rm \
        gisaia/python-3-alpine \
            setup.py sdist bdist_wheel


docker run --rm \
    -w /opt/python \
    -v $PWD:/opt/python \
    -v $HOME/.pypirc:/root/.pypirc \
    python:3 \
    /bin/bash -c  "pip install twine ; twine upload dist/*"


# AIAS COMMON
cd -

mkdir -p target/aias_common
rm -rf target/aias_common/*
mkdir -p target/aias_common/src/
cp -r aias_common target/aias_common/src/
cp -r release/materials/aias_common/* target/aias_common/
sed -i.bak 's/aias_version/\"'$1'\"/' target/aias_common/setup.py

cd target/aias_common

docker run \
        -e GROUP_ID="$(id -g)" \
        -e USER_ID="$(id -u)" \
        --mount dst=/opt/python,src="$PWD",type=bind \
        --rm \
        gisaia/python-3-alpine \
            setup.py sdist bdist_wheel


docker run --rm \
    -w /opt/python \
    -v $PWD:/opt/python \
    -v $HOME/.pypirc:/root/.pypirc \
    python:3 \
    /bin/bash -c  "pip install twine ; twine upload dist/*"
