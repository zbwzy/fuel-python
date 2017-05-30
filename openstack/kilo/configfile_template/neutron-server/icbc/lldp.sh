#!/bin/sh
if [ $# -ne 1 ]
then
    echo "WARNING: please input a para of physical interface"
    exit
fi

intf=$1

echo "1. install lldpad"
yum install lldpad -y

echo "2. start lldpad"
lldpad -d

echo "3. config lldp"
lldptool set-lldp -i ${intf} adminStatus=rxtx 
lldptool -T -i ${intf} -V  sysName enableTx=yes
lldptool -T -i ${intf} -V  portDesc enableTx=yes
lldptool -T -i ${intf} -V  sysDesc enableTx=yes
lldptool -T -i ${intf} -V sysCap enableTx=yes
lldptool -T -i ${intf} -V mngAddr enableTx=yes

echo "4. done"

