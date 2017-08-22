#!/bin/bash

export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3


openstack project create --domain default --description "Service Project" service

openstack project create --domain default --description "Demo Project" demo
echo 'end init keystone######'