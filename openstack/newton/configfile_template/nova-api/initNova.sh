#!/bin/sh

export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3

#
echo 'init nova in keystone===='
openstack role add --project service --user nova admin
openstack service create --name nova --description "OpenStack Compute" compute

openstack endpoint create --region RegionOne \
compute public http://<NOVA_VIP>:8774/v2.1/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
compute internal http://<NOVA_VIP>:8774/v2.1/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
compute admin http://<NOVA_VIP>:8774/v2.1/%\(tenant_id\)s

echo 'done to init nova in keystone####'
