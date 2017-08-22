#!/bin/bash

export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3

openstack user create --domain default --password-prompt demo

openstack role create user

openstack role add --project demo --user demo user
echo 'end init keystone######'
