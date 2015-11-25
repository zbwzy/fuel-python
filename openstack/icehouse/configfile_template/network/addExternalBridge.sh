echo 'start to add external bridge==========='
#ovs-vsctl add-port br-ex <PHYSICAL_EXTERNAL_NETWORK_INTERFACE>


ovs-vsctl add-br br-int
ovs-vsctl add-br br-ex

ovs-vsctl add-br br-eth0
ovs-vsctl add-port br-eth0 eth0

#add eth0 ip to br-eth0

ifconfig eth0 0.0.0.0
ifconfig br-eth0 <LOCAL_IP>
echo 'add external bridge done####'



