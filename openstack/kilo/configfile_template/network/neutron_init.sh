#!/bin/bash

echo 'start to init neutron db==========='
export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<LOCAL_IP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<LOCAL_IP>:35357/v2.0

keystone user-create --name=neutron --pass=123456 --email=<ADMIN_EMAIL>
keystone user-role-add --user=neutron --tenant=service --role=admin
keystone service-create --name=neutron --type=network --description="OpenStack Networking"
keystone endpoint-create --service-id=$(keystone service-list | awk '/ network / {print $2}') --publicurl=http://<NEUTRON_VIP>:9696 --adminurl=http://<NEUTRON_VIP>:9696 --internalurl=http://<NEUTRON_VIP>:9696

echo 'init neutron db done####'
