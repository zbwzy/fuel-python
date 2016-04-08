#!/bin/bash

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


yum install qemu* -y
yum install lvm2 -y

systemctl enable lvm2-lvmetad.service
systemctl start lvm2-lvmetad.service

echo 'start to create empty file system=============='
echo `date`

#create 20GB empty file
dd if=/dev/zero of=/home/test-disk bs=1M count=20480
echo 'end to create empty file system#####'
echo `date`

losetup /dev/loop2 /home/test-disk
pvcreate /dev/loop2
vgcreate cinder-volumes /dev/loop2

chmod 777 /home/test-disk

echo 'init cinder storage done####'