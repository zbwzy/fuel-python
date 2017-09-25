#!/bin/sh
if [ $# -ne 2 ]
then
    echo "WARNING: please input two para of bond and vlan"
    exit
fi

bond=$1
vlan=$2
dot="."
bondv=${bond}${dot}${vlan}

path1="/etc/sysconfig/network-scripts/ifcfg-"
echo "1. remove port from bridge br-fw-admin"
ifconfig br-fw-admin down
brctl delif br-fw-admin ${bond}
brctl delbr br-fw-admin
rm -rf /etc/sysconfig/network-scripts/ifcfg-br-fw-admin
path3=${path1}${bond}
sed -i '/br-fw-admin/d' ${path3}

echo "2. delete bridge br-data and delete interface br-data"
path2=${path1}${bondv}
ifconfig br-data down
brctl delif br-data ${bondv}
brctl delbr br-data
rm -rf /etc/sysconfig/network-scripts/ifcfg-br-data
rm -rf ${path2}

echo "3. restart network"
systemctl restart network

echo "4. create ovs bridge br-ex and add bond to br-ex"
ovs-vsctl add-br br-ex
ovs-vsctl add-port br-ex ${bond}

echo "5. done"

