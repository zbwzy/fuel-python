#!/bin/bash

echo 'start to init rabbitmq cluster======'
echo 'ulimit -n 102400' > /etc/default/rabbitmq-server

#ps aux| grep rabbitmq | grep erlang| grep -v grep | awk '{print "kill -9 " $2}'  | bash

sleep 2
/usr/sbin/rabbitmq-server -detached
sleep 5
#rabbitmqctl change_password guest 123456
rabbitmqctl add_user <RABBIT_USER_ID> <RABBIT_PASS>
rabbitmqctl set_permissions -p / <RABBIT_USER_ID> ".*" ".*" ".*"

sleep 5
#rabbitmqctl set_policy ha_all "^" '{"ha-mode":"all"}'
rabbitmqctl set_policy ha-all '^(?!amq\.).*' '{"ha-mode": "all"}'

echo 'init rabbitmq cluster done######'