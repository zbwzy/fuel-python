#!/bin/bash

echo 'start to init nova db==========='
su -s /bin/sh -c "nova-manage db sync" nova 

#create nova user & role
keystone user-create --name=nova --pass=123456 --email=<ADMIN_EMAIL>
keystone user-role-add --user=nova --tenant=service --role=admin

#set Keystone: create nova service & endpoint
keystone service-create --name=nova --type=compute --description="OpenStack Compute"

keystone endpoint-create --service-id=$(keystone service-list | awk '/ compute / {print $2}') --publicurl=http://<NOVA_API_VIP>:8774/v2/%\(tenant_id\)s  --internalurl=http://<NOVA_API_VIP>:8774/v2/%\(tenant_id\)s --adminurl=http://<NOVA_API_VIP>:8774/v2/%\(tenant_id\)s 


echo 'init nova db done####'
