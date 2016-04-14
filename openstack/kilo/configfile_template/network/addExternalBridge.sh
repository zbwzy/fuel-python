echo 'start to add external bridge==========='
#############
systemctl restart openvswitch.service

sleep 2

#ovs-vsctl add-br br-int
#ovs-vsctl add-br br-ex
#
#ovs-vsctl add-br br-eth0
#ovs-vsctl add-port br-eth0 eth0
#
##add eth0 ip to br-eth0
#
#ifconfig eth0 0.0.0.0
#ifconfig br-eth0 <LOCAL_IP>

#############
#Add the external bridge:
ovs-vsctl add-br br-ex
#Add a port to the external bridge that connects to the physical external network interface
#Replace INTERFACE_NAME with the actual interface name. For example, eth2 or ens256.

ovs-vsctl add-port br-ex <PHYSICAL_EXTERNAL_NETWORK_INTERFACE>



echo 'add external bridge done####'



