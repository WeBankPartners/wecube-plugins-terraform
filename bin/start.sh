#!/bin/bash

# start wecube plugins terraform
echo "terraform plugins starting "

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_PATH};

mkdir ../logs
PORT=`cat ../conf/application.conf | grep -v "^#" | grep serverport | awk -F "=" '{print $2}' | sed 's/ //g'`

python ../manage.py runserver 0.0.0.0:$PORT >> ../logs/service.log

echo "done"
