if  [ -z "$PIP_LOGIN"  ] ; then echo "Please set PIP_LOGIN environment variable"; exit -1; fi
if  [ -z "$PIP_PASSWORD"  ] ; then echo "Please set PIP_PASSWORD environment variable"; exit -1; fi
rm -r target
mkdir -p target/src/aeoprs/core/models
cp aeoprs/core/models/* target/src/aeoprs/core/models
cp publish/materials/* target/
cd target
sed -i.bak 's/aeoprsmodel_version/\"'$1'\"/' setup.py


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
