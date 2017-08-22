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

openstack user create --domain default --password-prompt cinder

echo 'done to init cinder in keystone####'