#!/bin/sh
echo "start============="

cd /etc/sysconfig/network-scripts/; ls -lt /etc/sysconfig/network-scripts/ | grep ifcfg- | awk '{print "sed -i '/ETHTOOL_OPTS=/d' " $9}' | bash



echo "done######"

