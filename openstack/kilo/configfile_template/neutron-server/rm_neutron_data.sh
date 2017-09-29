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

echo 'start to delete neutron init data==========='
echo '1.delete router from internal subnet==========='
neutron router-interface-delete testrouter1 net04-subnet
sleep 2

echo '2.delete router from external net==========='
neutron router-gateway-clear testrouter1 external-vlan-subnet
neutron router-gateway-clear testrouter1 external-vlan
sleep 2

echo '3.delete port==========='
neutron port-list | grep subnet_id | awk '{print "neutron port-delete " $2}' | bash

echo '4.delete net==========='
neutron subnet-list | grep net | awk '{print "neutron subnet-delete " $2}' | bash
neutron net-delete external-vlan
neutron net-delete net04

echo '5.delete router==========='
neutron router-delete testrouter1


echo 'done delete neutron init data#####'


