#!/bin/sh
export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3

#
echo 'init neutron in keystone===='

openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking" network

openstack endpoint create --region RegionOne \
network public http://<NEUTRON_VIP>:9696

openstack endpoint create --region RegionOne \
network internal http://<NEUTRON_VIP>:9696

openstack endpoint create --region RegionOne \
network admin http://<NEUTRON_VIP>:9696



echo 'done to init neutron in keystone####'