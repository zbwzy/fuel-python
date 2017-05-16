#!/bin/sh
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


gnocchi archive-policy create -d granularity:2m,points:30 -d granularity:5m,points:36 -d granularity:10m,points:36 -d granularity:15m,points:24 -d granularity:1h,points:24 -d granularity:1d,points:360 low
gnocchi archive-policy create -d granularity:60s,points:60 -d granularity:1h,points:168 -d granularity:1d,points:365 medium
gnocchi archive-policy create -d granularity:1s,points:86400 -d granularity:1m,points:43200 -d granularity:1h,points:8760 high
gnocchi archive-policy-rule create -a low -m "*" default