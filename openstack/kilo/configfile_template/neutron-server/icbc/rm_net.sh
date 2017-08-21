#!/bin/sh
if [ $# -ne 3 ]
then
    echo "WARNING: please input THREE parameters of bond vlanid bridge"
    exit
fi

bond=$1
vlan=$2
bridge=$3
dot="."
bondv=${bond}${dot}${vlan}

path1="/etc/sysconfig/network-scripts/ifcfg-"
path2=${path1}${bridge}
echo "1. remove port from bridge ${bridge}"
brctl delif ${bridge} ${bond}
path2=${path1}${bridge}
path3=${path1}${bondv}

echo "2. delete bridge ${bridge} "
ifconfig ${bridge} down
brctl delif ${bridge} ${bondv}
brctl delbr ${bridge} 
rm -rf ${path2}
rm -rf ${path3}

echo "3. restart network"
systemctl restart network

systemctl restart keepalived


echo "4. done"

