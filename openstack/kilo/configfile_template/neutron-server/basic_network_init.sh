#!/bin/bash

#configure env var
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

echo 'start to init basic network==========='

neutron net-create basic-net --provider:network_type vlan --provider:physical_network physnet1 --shared

neutron subnet-create --name basic-subnet --allocation-pool start=<START_IP>,end=<END_IP> --enable-dhcp --gateway <BASIC_GATEWAY> basic-net <BASIC_CIDR>

echo 'init basic network done####'

