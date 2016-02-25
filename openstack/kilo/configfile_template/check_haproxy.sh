#!/bin/bash
A=`ps -C haproxy --no-header | wc -l`
if [ $A -eq 0 ];then
  echo "haproxy is down!"
  service haproxy start
  sleep 2
  if [ `ps -C haproxy --no-header | wc -l ` -eq 0 ];then
    service keepalived stop #transfer the VIP to another node
  fi
fi
