#!/bin/bash

PYTHON_VER=$(python -V 2>&1)

if [[ ${PYTHON_VER} != *"2.7"* ]]; then
    PYTHON="/usr/bin/python2.7"
else
    PYTHON=$(which python)
fi

# FLASK SETUP
if [[ ! -e flask ]]; then
    echo "===Setting up flask environment==="
    virtualenv --python=${PYTHON} flask
    flask/bin/pip install flask
    flask/bin/pip install -U flask-cors
fi

# APACHE SETUP
WWW="/var/www/html/planesolari"
if [[ ! -d ${WWW} ]]; then
    echo "===Setting up web front-end==="
    mkdir ${WWW}
    chmod 755 ${WWW}

    mkdir ${WWW}/src
    chmod 755 ${WWW}/src
    cp Flapper/src/jquery.flapper.js ${WWW}/src

    cp -r Flapper/css ${WWW}
    chmod 755 ${WWW}/css
    cp Flapper/transform/dist/jquery.transform-0.9.3.min.js ${WWW}/src
fi

echo "===Updating plane-solari files==="
cp src/html/* ${WWW}
cp src/js/* ${WWW}/src
