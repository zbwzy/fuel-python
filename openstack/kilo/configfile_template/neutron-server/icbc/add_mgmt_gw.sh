#!/bin/bash

echo "start to add mgmt gateway============"

gw=$1

sed -i s/^GATEWAY/#GATEWAY/g /etc/sysconfig/network-scripts/ifcfg-br-mgmt

echo GATEWAY=$gw >> /etc/sysconfig/network-scripts/ifcfg-br-mgmt

echo "done to add mgmt gateway#######"