#!/bin/sh
echo "start============="

ls -lt /tmp/sysconfig/network-scripts/ | grep ifcfg- | awk '{print "sed -i '/ETHTOOL_OPTS=/d' /tmp/sysconfig/network-scripts/" $9}'  


echo "done######"

