#!/bin/bash

echo 'start to init heat db==========='

keystone user-create --name heat --pass <HEAT_MYSQL_PASSWORD>

keystone user-role-add --user heat --tenant service --role admin
keystone role-create --name heat_stack_owner
keystone user-role-add --user demo --tenant demo --role heat_stack_owner
keystone role-create --name heat_stack_user

keystone service-create --name heat --type orchestration \
--description "Orchestration"


keystone service-create --name heat-cfn --type cloudformation \
--description "Orchestration"

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ orchestration / {print $2}') \
--publicurl http://<HEAT_VIP>:8004/v1/%\(tenant_id\)s \
--internalurl http://<HEAT_VIP>:8004/v1/%\(tenant_id\)s \
--adminurl http://<HEAT_VIP>:8004/v1/%\(tenant_id\)s \
--region regionOne

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ cloudformation / {print $2}') \
--publicurl http://<HEAT_VIP>:8000/v1 \
--internalurl http://<HEAT_VIP>:8000/v1 \
--adminurl http://<HEAT_VIP>:8000/v1 \
--region regionOne


su -s /bin/sh -c "heat-manage db_sync" heat

echo 'init heat db done####'
