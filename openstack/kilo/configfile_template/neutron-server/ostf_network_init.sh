#!/bin/bash

#configure env var

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<KEYSTONE_VIP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v2.0

echo 'start to init ostf network==========='

neutron net-create ext-net-flat --shared --provider:network_type flat \
--provider:physical_network physnet1 --router:external true

neutron subnet-create ext-net-flat --name ext-subnet --allocation-pool start=192.168.242.20,end=192.168.242.30 --disable-dhcp --gateway 192.168.242.2 192.168.242.0/24


#neutron net-create private-net
#create private net defaultly
neutron net-create net04

#neutron subnet-create private-net --name private-subnet  --gateway 192.168.10.1 192.168.10.0/24
neutron subnet-create net04 --name net04-subnet  --gateway 192.168.10.1 192.168.10.0/24


echo 'init ostf network done####'
