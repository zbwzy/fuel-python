#!/bin/bash

systemctl restart openstack-nova-api.service
systemctl restart openstack-nova-cert.service
systemctl restart openstack-nova-consoleauth.service
systemctl restart openstack-nova-scheduler.service
systemctl restart openstack-nova-conductor.service
systemctl restart openstack-nova-novncproxy.service