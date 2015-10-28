#!/bin/bash

echo 'start to init cinder db==========='

keystone user-create --name=cinder --pass=<MYSQL_PASSWORD>

keystone user-role-add --user=cinder --tenant=service --role=admin

keystone service-create --name cinder --type volume --description "OpenStack Block Storage"

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
