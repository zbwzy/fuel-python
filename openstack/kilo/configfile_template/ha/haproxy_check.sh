#!/bin/bash
A=`ps -C haproxy --no-header | wc -l`

if [ $A -eq 0 ];then
  echo "haproxy is down!"
  systemctl stop keepalived
  exit 1
else
  exit 0
fi
