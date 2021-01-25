#!/bin/bash

# start wecube plugins terraform
echo "terraform plugins starting "
pidfile=bin/terraform.pid
logfile=logs/err.log

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${SCRIPT_PATH};

mkdir ../logs
cd ..
echo "gunicorn starting process. wating ... "
gunicorn  -c gunicorn.conf wecube_plugins_terraform.wsgi:application -t 900 --pid $pidfile --error-logfile $logfile --log-level info

echo "done"
