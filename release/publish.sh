if  [ -z "$PIP_LOGIN"  ] ; then echo "Please set PIP_LOGIN environment variable"; exit -1; fi
if  [ -z "$PIP_PASSWORD"  ] ; then echo "Please set PIP_PASSWORD environment variable"; exit -1; fi
rm -r target
mkdir -p target/src/airs/core/models
cp -r airs/core/models/* target/src/airs/core/models
cp -r  publish/materials/* target/
sed -i.bak 's/airsmodel_version/\"'$1'\"/' target/setup.py

cat target/README_head.md > target/README.md
cat docs/model/model.md >> target/README.md

cd target
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
    python:3 \
    /bin/bash -c  "pip install twine ; twine upload dist/* -u ${PIP_LOGIN} -p ${PIP_PASSWORD}"
