#!/bin/bash

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<KEYSTONE_VIP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v2.0

echo 'start to import image to glance==========='

glance image-create --name='cirros image' --is-public=true \
--container-format=bare --disk-format=qcow2 < /etc/puppet/modules/glance/files/cirros-0.3.1-x86_64-disk.img

sleep 12
echo 'import image done####'
