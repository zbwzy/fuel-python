#!/bin/sh
export OS_TOKEN=<ADMIN_TOKEN>
export OS_URL=http://<KEYSTONE_VIP>:35357/v2.0

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
echo 'init cinder in keystone===='

openstack role add --project service --user cinder admin

openstack service create --name cinder --description "OpenStack Block Storage" volume

openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2

#openstack endpoint create \
#--publicurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
#--internalurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
#--adminurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
#--region RegionOne \
#volume

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ volume / {print $2}') \
--publicurl http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s \
--internalurl http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s \
--adminurl http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s \
--region RegionOne

keystone endpoint-create \
--service-id $(keystone service-list | awk '/ volumev2 / {print $2}') \
--publicurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
--internalurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
--adminurl http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s \
--region RegionOne

echo 'done to init cinder in keystone####'