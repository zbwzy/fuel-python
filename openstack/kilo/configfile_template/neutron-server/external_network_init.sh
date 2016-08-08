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

echo 'start to init ostf network==========='

#flat mode
#neutron net-create ext-net-flat --shared --provider:network_type flat \
#--provider:physical_network physnet1 --router:external true

#neutron subnet-create ext-net-flat --name ext-subnet --allocation-pool start=192.168.242.20,end=192.168.242.30 --disable-dhcp --gateway 192.168.242.2 192.168.242.0/24

#vlan mode
neutron net-create external-vlan --provider:network_type vlan --provider:physical_network physnet1 --router:external
neutron subnet-create --name external-vlan-subnet --allocation-pool start=<START_IP>,end=<END_IP> --disable-dhcp --gateway <EX_GATEWAY> external-vlan <EX_CIDR>


neutron router-gateway-set  testrouter1 external-vlan

neutron router-interface-add testrouter1 net04-subnet


echo 'init ostf network done####'

