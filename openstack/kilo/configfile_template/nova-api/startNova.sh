#!/bin/bash

#systemctl enable openstack-nova-api.service
#systemctl enable openstack-nova-cert.service
#systemctl enable openstack-nova-consoleauth.service
#systemctl enable openstack-nova-scheduler.service
#systemctl enable openstack-nova-conductor.service
#systemctl enable openstack-nova-novncproxy.service

echo 'restart nova controller========='
systemctl restart openstack-nova-api.service
systemctl restart openstack-nova-cert.service
systemctl restart openstack-nova-consoleauth.service
systemctl restart openstack-nova-scheduler.service
systemctl restart openstack-nova-conductor.service
systemctl restart openstack-nova-novncproxy.service
echo 'done to restart nova controller========='