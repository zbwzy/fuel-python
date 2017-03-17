#!/bin/bash

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<LOCAL_IP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<LOCAL_IP>:35357/v2.0

echo 'start to init ceilometer==========='

keystone user-create --name ceilometer --pass 123456

keystone user-role-add --user ceilometer --tenant service --role admin

keystone service-create --name ceilometer --type metering \
--description "Telemetry"

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ metering / {print $2}') \
--publicurl http://<CEILOMETER_VIP>:8777 \
--internalurl http://<CEILOMETER_VIP>:8777 \
--adminurl http://<CEILOMETER_VIP>:8777 \
--region regionOne


echo 'init ceilometer done####'
