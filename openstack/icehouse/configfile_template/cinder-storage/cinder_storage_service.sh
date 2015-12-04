#!/bin/bash

export OS_SERVICE_TOKEN=123456
export OS_SERVICE_ENDPOINT=http://<KEYSTONE_VIP>:35357/v2.0

export OS_USERNAME=admin
export OS_PASSWORD=123456
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://<KEYSTONE_VIP>:35357/v2.0


yum install lvm2 -y

/etc/init.d/lvm2-lvmetad restart

chkconfig  lvm2-lvmetad on


echo 'start to create empty file system=============='
echo `date`

dd if=/dev/zero of=/home/test-disk bs=1M count=20480 #创建一个20G空文件(字型调整)
echo 'end to create empty file system#####'
echo `date`

losetup /dev/loop2 /home/test-disk                   #将其转化为loop设备 loop1/loop2都行
pvcreate /dev/loop2                                  #创建lvm的物理卷
vgcreate cinder-volumes /dev/loop2                   #创建lvm物理卷组 cinder-volumes 名字不变



#yum install openstack-cinder targetcli python-oslo-db MySQL-python -y


#cinder.conf文件中,iscsi_helper = lioadm写成iscsi_helper=tgtadm

#/etc/init.d/tgtd restart
#chkconfig tgtd on


echo 'init cinder storage done####'
