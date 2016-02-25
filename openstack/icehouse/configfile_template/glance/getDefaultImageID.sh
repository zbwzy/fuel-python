#!/bin/bash

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<KEYSTONE_VIP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v2.0

glance image-list | awk '{print $2}' | sed -n '4p'