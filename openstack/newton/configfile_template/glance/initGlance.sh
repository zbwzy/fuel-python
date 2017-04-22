#!/bin/sh
export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3

#
echo 'init glance in keystone===='
openstack service create --name glance \
--description "OpenStack Image" image

openstack endpoint create --region RegionOne \
image public http://<GLANCE_VIP>:9292

openstack endpoint create --region RegionOne \
image internal http://<GLANCE_VIP>:9292

openstack endpoint create --region RegionOne \
image admin http://<GLANCE_VIP>:9292


echo 'done to init glance in keystone####'