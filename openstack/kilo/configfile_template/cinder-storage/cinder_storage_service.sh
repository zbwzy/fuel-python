#!/bin/bash
export OS_TOKEN=<ADMIN_TOKEN>
export OS_URL=http://<KEYSTONE_VIP>:35357/v2.0

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
#/usr/bin/dd if=/dev/zero of=/home/test-disk bs=1M count=20480
/usr/bin/dd if=/dev/zero of=/var/lib/cinder bs=1M count=20480
echo 'end to create empty file system#####'
echo `date`

sleep 5
chmod 777 /var/lib/cinder

/usr/sbin/losetup /dev/loop2 /var/lib/cinder
/usr/sbin/pvcreate /dev/loop2
/usr/sbin/vgcreate cinder-volumes /dev/loop2

systemctl restart lvm2-lvmetad.service
echo 'init cinder storage done####'