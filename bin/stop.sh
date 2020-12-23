#!/bin/bash

# wecube plugins terraform stop

echo "wecube plugins terraform will stop"
PID=`ps -ef | grep python | grep -v grep | awk -F " " '{print $2}'`

echo "wating ..."
kill -9 $PID
echo "done"

