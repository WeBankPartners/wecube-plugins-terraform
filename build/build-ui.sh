#!/bin/bash
set -e -x
npm -v
if [ $? -eq 0 ]
then
    cd $1/ui
    npm install
    npm run plugin
else
    docker run --rm -v $1:/app/terraform --name terraform-node-build node:12.13.1 /bin/bash /app/terraform/build/build-ui-docker.sh
fi