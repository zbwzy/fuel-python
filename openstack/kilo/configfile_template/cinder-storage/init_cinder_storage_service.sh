#!/bin/bash

echo 'init_cinder_storage_service======================='

yum install lvm2 -y

/etc/init.d/lvm2-lvmetad restart

#chkconfig  lvm2-lvmetad on


echo 'start to init =============='
echo `date`

#dd if=/dev/zero of=/home/test-disk bs=1M count=20480 #create 20G empty file
#echo 'end to create empty file system#####'
#echo `date`

losetup /dev/loop2 /home/test-disk   #modify test-disk to loop device loop1/loop2
pvcreate /dev/loop2                  #create lvm physical volume
vgcreate cinder-volumes /dev/loop2   #create lvm physical volume group:cinder-volumes, use the same name



#yum install openstack-cinder targetcli python-oslo-db MySQL-python -y



/etc/init.d/tgtd restart
chkconfig tgtd on

service openstack-cinder-volume restart

echo `date`
echo 'end init cinder-volume####'

echo 'init_cinder_storage_service done####'
