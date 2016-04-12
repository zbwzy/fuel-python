#!/bin/bash

echo 'ulimit -n 102400' > /etc/default/rabbitmq-server

/usr/sbin/rabbitmqctl stop_app

sleep 3

/usr/sbin/rabbitmqctl join_cluster rabbit@<RABBITMQ_MASTER>

/usr/sbin/rabbitmqctl start_app

sleep 2

/usr/sbin/rabbitmqctl set_policy ha-all '^(?!amq\.).*' '{"ha-mode": "all"}'

sleep 2
/usr/sbin/rabbitmqctl add_user <RABBIT_USER_ID> <RABBIT_PASS>

sleep 2

/usr/sbin/rabbitmqctl set_permissions -p / <RABBIT_USER_ID> '.*' '.*' '.*'

