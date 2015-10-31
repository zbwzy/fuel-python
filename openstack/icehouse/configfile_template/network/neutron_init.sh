#!/bin/bash

echo 'start to init neutron db==========='
keystone user-create --name=neutron --pass=123456 --email=<ADMIN_EMAIL>
keystone user-role-add --user=neutron --tenant=service --role=admin
keystone service-create --name=neutron --type=network --description="OpenStack Networking"
keystone endpoint-create --service-id=$(keystone service-list | awk '/ network / {print $2}') --publicurl=http://<NEUTRON_SERVER_VIP>:9696 --adminurl=http://<NEUTRON_SERVER_VIP>:9696 --internalurl=http://<NEUTRON_SERVER_VIP>:9696

echo 'init neutron db done####'
