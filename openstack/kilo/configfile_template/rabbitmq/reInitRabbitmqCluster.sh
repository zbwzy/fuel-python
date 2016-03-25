#!/bin/bash

echo 'ulimit -n 102400' > /etc/default/rabbitmq-server

rabbitmqctl stop_app

sleep 3

rabbitmqctl join_cluster rabbit@<RABBITMQ_MASTER>

rabbitmqctl start_app

sleep 2

rabbitmqctl set_policy ha-all '^(?!amq\.).*' '{"ha-mode": "all"}'

sleep 2
rabbitmqctl add_user <RABBIT_USER_ID> <RABBIT_PASS>

sleep 2

rabbitmqctl  set_permissions -p / <RABBIT_USER_ID> '.*' '.*' '.*'

