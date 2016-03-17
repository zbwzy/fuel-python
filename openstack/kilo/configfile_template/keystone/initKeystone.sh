#!/bin/bash

export OS_TOKEN=<ADMIN_TOKEN>
###Use first keystone node to init
export OS_URL=http://<KEYSTONE_IP>:35357/v2.0

openstack service create --name keystone --description "OpenStack Identity" identity
openstack endpoint create --publicurl http://<KEYSTONE_VIP>:5000/v2.0 --internalurl http://<KEYSTONE_VIP>:5000/v2.0 --adminurl http://<KEYSTONE_VIP>:35357/v2.0 --region RegionOne identity

openstack project create --description "Admin Project" admin
openstack user create --password-prompt admin
openstack role create admin
openstack role add --project admin --user admin admin
openstack project create --description "Service Project" service
openstack role create user
echo 'end init keystone######'