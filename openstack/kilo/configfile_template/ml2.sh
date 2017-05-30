#!/bin/sh
if [ $# -ne 3 ]
then
echo "WARNING: please input three para of vlan range, vni range and ipaddr, sample: 'sh ml2.sh 2:4000 5000:10000 73.0.0.50'"
exit
fi

vlan=$1
vni=$2
ip=$3

echo "1. config mechanism_drivers"
sed -i s/"^mechanism_drivers.*"/"mechanism_drivers = huawei,openvswitch"/g /etc/neutron/plugins/ml2/ml2_conf.ini

echo "2. config network_vlan_ranges"
sed -i s/"^network_vlan_ranges.*"/"network_vlan_ranges = physnet1:${vlan}"/g /etc/neutron/plugins/ml2/ml2_conf.ini

echo "3. config vni_ranges"
sed -i s/"^vni_ranges.*"/"vni_ranges = ${vni}"/g /etc/neutron/plugins/ml2/ml2_conf.ini

echo "4. config local ip"
sed -i s/"^local_ip.*"/"local_ip = ${ip}"/g /etc/neutron/plugins/ml2/ml2_conf.ini

echo "5. config bridge_mappings"
sed -i s/"^#bridge_mappings.*"/"bridge_mappings = physnet1:br-ex"/g /etc/neutron/plugins/ml2/ml2_conf.ini

echo "6. done"