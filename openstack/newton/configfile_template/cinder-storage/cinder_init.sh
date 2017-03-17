#!/bin/bash

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<LOCAL_IP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<LOCAL_IP>:35357/v2.0

echo 'start to init cinder db==========='

keystone user-create --name=cinder --pass=<MYSQL_PASSWORD>

keystone user-role-add --user=cinder --tenant=service --role=admin

keystone service-create --name cinder --type volume --description "OpenStack Block Storage"
keystone service-create --name cinderv2 --type volumev2 --description "OpenStack Block Storage"

keystone endpoint-create \
  --service-id $(keystone service-list | awk '/ volume / {print $2}') \
  --publicurl http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s \
  --internalurl http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s \
  --adminurl http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s \
  --region regionOne

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ volumev2 / {print $2}') \
--publicurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
--internalurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
--adminurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
--region regionOne

su -s /bin/sh -c "cinder-manage db sync" cinder

echo 'init cinder db done####'
