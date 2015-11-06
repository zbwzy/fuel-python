#!/bin/bash

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<LOCAL_IP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<LOCAL_IP>:35357/v2.0

echo 'start to init glance db==========='

su -s /bin/sh -c "glance-manage db_sync" glance

keystone user-create --name=glance --pass=123456  --email=<ADMIN_EMAIL>
keystone user-role-add --user=glance --tenant=service --role=admin 

keystone service-create --name=glance --type=image --description="OpenStack Image Service" 
keystone endpoint-create --service-id=$(keystone service-list | awk '/ image / {print $2}') --publicurl=http://<GLANCE_VIP>:9292  --internalurl=http://<GLANCE_VIP>:9292  --adminurl=http://<GLANCE_VIP>:9292


echo 'init glance db done####'
