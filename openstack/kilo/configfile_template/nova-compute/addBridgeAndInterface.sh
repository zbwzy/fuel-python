ovs-vsctl add-br br-int

ovs-vsctl add-br br-eth0
ovs-vsctl add-port br-eth0 eth0

#add eth0 ip to br-eth0上

ifconfig eth0 0.0.0.0
ifconfig br-eth0 <LOCAL_IP>