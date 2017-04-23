#!/bin/bash
export OS_USERNAME=admin
export OS_PASSWORD=<KEYSTONE_ADMIN_PASSWORD>
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v3
export OS_IDENTITY_API_VERSION=3


yum install qemu* -y
yum install lvm2 -y

systemctl enable lvm2-lvmetad.service
systemctl start lvm2-lvmetad.service

echo 'start to create empty file system=============='
echo `date`

#create 20GB empty file
/usr/bin/dd if=/dev/zero of=/home/test-disk bs=1M count=20480
#/usr/bin/dd if=/dev/zero of=/var/lib/cinder bs=1M count=20480
echo 'end to create empty file system#####'
echo `date`

sleep 5
chmod 777 /home/test-disk

/usr/sbin/losetup /dev/loop2 /home/test-disk
/usr/sbin/pvcreate /dev/loop2
/usr/sbin/vgcreate cinder-volumes /dev/loop2

systemctl restart lvm2-lvmetad.service
echo 'init cinder storage done####'