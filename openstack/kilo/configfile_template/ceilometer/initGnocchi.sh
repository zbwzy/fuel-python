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
echo 'init gnocchi in keystone===='

openstack role add --project service --user gnocchi admin

openstack service create --name gnocchi --description "OpenStack Metric Service" metric

openstack endpoint create --publicurl http://<GNOCCHI_VIP>:8041 --internalurl http://<GNOCCHI_VIP>:8041 --adminurl http://<GNOCCHI_VIP>:8041 --region RegionOne metric


echo 'done to init gnocchi in keystone####'