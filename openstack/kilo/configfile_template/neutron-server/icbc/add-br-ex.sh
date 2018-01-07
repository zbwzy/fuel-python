#!/bin/sh
echo "start to add ovs-bridge br-ex===="
ovs-vsctl add-br br-ex
ovs-vsctl add-port br-ex bond0
echo "add br-ex ovs bridge done"

