#!/bin/sh
echo "prepare rpc.py adapted to Huawei AC====="
mv /usr/lib/python2.7/site-packages/neutron/plugins/ml2/rpc.py /home
mv /usr/lib/python2.7/site-packages/neutron/plugins/ml2/rpc.py.huawei /usr/lib/python2.7/site-packages/neutron/plugins/ml2/rpc.py
echo "prepare rpc.py adapted to Huawei AC####"

echo "start to add ovs-bridge br-ex===="
ovs-vsctl add-br br-ex
ovs-vsctl add-port br-ex bond0
echo "add br-ex ovs bridge done"

