#!/bin/sh
export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3

#
echo 'init cinder in keystone===='

openstack role add --project service --user cinder admin

openstack service create --name cinder \
--description "OpenStack Block Storage" volume

openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2

openstack service create --name cinderv2 \
--description "OpenStack Block Storage" volumev2


openstack endpoint create --region RegionOne \
volume public http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
volume internal http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
volume admin http://<CINDER_VIP>:8776/v1/%\(tenant_id\)s


openstack endpoint create --region RegionOne \
volumev2 public http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
volumev2 internal http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s

openstack endpoint create --region RegionOne \
volumev2 admin http://<CINDER_VIP>:8776/v2/%\(tenant_id\)s



echo 'done to init cinder in keystone####'