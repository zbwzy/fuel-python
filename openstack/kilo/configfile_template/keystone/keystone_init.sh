#!/bin/bash

echo 'start to init keystone db====='

## configure env var
#export OS_SERVICE_TOKEN=123456
#export OS_SERVICE_ENDPOINT=http://<KEYSTONE_VIP>:35357/v2.0

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<LOCAL_IP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<LOCAL_IP>:35357/v2.0

## create an admin user
keystone user-create --name=admin --pass=123456 --email=<ADMIN_EMAIL>
keystone role-create --name=admin
keystone role-create --name=_member_
keystone tenant-create --name=admin --description="Admin Tenant"
keystone user-role-add --user=admin --tenant=admin --role=admin
keystone user-role-add --user=admin --role=_member_ --tenant=admin

## create a normal user -- demo
keystone user-create --name=demo --pass=123456 --email=demo@abc.com
keystone tenant-create --name=demo --description="Demo Tenant"
keystone user-role-add --user=demo --role=_member_ --tenant=demo


##	create service tenant
keystone tenant-create --name=service --description="Service Tenant"

##	create keystone users,services & endpoint
keystone service-create --name=keystone --type=identity --description="OpenStack Identity"
keystone endpoint-create --service-id=$(keystone service-list | awk '/ identity / {print $2}') --publicurl=http://<KEYSTONE_VIP>:5000/v2.0 --internalurl=http://<KEYSTONE_VIP>:5000/v2.0 --adminurl=http://<KEYSTONE_VIP>:35357/v2.0

###########################OSTF
#ostf data init
echo 'ostf data init:role create========'
mysql -uroot -p123456 -e "INSERT INTO keystone.role (id, name, extra) VALUES ('9fe2ff9ee4384b1894a90878d3e92bab', '__member__', '{}')"
echo 'role create done#####'
###########################

echo 'init keystone db done####'
