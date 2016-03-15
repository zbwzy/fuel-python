#!/bin/sh
export LC_ALL=C
export OS_NO_CACHE='true'
export OS_TENANT_NAME='admin'
export OS_PROJECT_NAME='admin'
export OS_USERNAME='admin'
export OS_PASSWORD='<KEYSTONE_ADMIN_PASSWORD>'
export OS_AUTH_URL='http://<KEYSTONE_VIP>:5000/v2.0/'
export OS_AUTH_STRATEGY='keystone'
export OS_REGION_NAME='RegionOne'
export CINDER_ENDPOINT_TYPE='internalURL'
export GLANCE_ENDPOINT_TYPE='internalURL'
export KEYSTONE_ENDPOINT_TYPE='internalURL'
export NOVA_ENDPOINT_TYPE='internalURL'
export NEUTRON_ENDPOINT_TYPE='internalURL'
export OS_ENDPOINT_TYPE='internalURL'
export OS_VOLUME_API_VERSION=2

#
echo 'init nova in keystone===='
keystone user-create --name=nova --pass=<KEYSTONE_NOVA_PASSWORD>
openstack role add --project service --user nova admin
openstack service create --name nova --description "OpenStack Compute" compute
openstack endpoint create \
--publicurl http://<NOVA_VIP>:8774/v2/%\(tenant_id\)s \
--internalurl http://<NOVA_VIP>:8774/v2/%\(tenant_id\)s \
--adminurl http://<NOVA_VIP>:8774/v2/%\(tenant_id\)s \
--region RegionOne \
compute

echo 'done to init nova in keystone####'
