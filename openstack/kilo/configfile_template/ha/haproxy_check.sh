#!/bin/bash
#count=`ps -ef|grep -v grep|grep haproxy|wc -l`
count=`netstat -nlp|grep -i haproxy|wc -l`
if [ $count -gt 1 ]; then
exit 0
else
systemctl stop keepalived
exit 1
fi
