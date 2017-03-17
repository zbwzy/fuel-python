#!/bin/bash

echo 'start to init rabbitmq cluster======'

#ps aux| grep rabbitmq | grep erlang| grep -v grep | awk '{print "kill -9 " $2}'  | bash

sleep 2
/usr/sbin/rabbitmqctl set_policy ha-all '^(?!amq\.).*' '{"ha-mode": "all"}'

sleep 2
/usr/sbin/rabbitmqctl add_user <RABBIT_USER_ID> <RABBIT_PASS>

sleep 2
/usr/sbin/rabbitmqctl set_permissions -p / <RABBIT_USER_ID> '.*' '.*' '.*'

echo 'init rabbitmq cluster done######'