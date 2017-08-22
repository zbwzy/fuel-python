#!/bin/bash

#configure env var

export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3

echo 'start to init cinder db==========='

keystone user-create --name=cinder --pass=<CINDER_MYSQL_PASSWORD>

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
