#!/bin/sh
#echo "1. install lldpad"
#yum install lldpad -y

BOND_DEVICE="bond0"
BOND_SLAVES=`ip -o link show |grep "master bond0"|cut -d ':' -f2`

function start()
{ 
 lldpad -d;
 for i in $BOND_SLAVES;
 do
	lldptool set-lldp -i ${i} adminStatus=rxtx 
        lldptool -T -i ${i} -V  sysName enableTx=yes
        lldptool -T -i ${i} -V  portDesc enableTx=yes
        lldptool -T -i ${i} -V  sysDesc enableTx=yes
        lldptool -T -i ${i} -V sysCap enableTx=yes
        lldptool -T -i ${i} -V mngAddr enableTx=yes
 done
 }

function stop()
{ 
	pass
 }

case "$1" in
 start)
 start;
	;;
 stop)
 stop;
 ;;
 *)
	echo $"useage: $0 (start)"
	exit 2
 
esac
