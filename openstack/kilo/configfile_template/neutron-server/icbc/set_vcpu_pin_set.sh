#!/bin/bash


value=$1

sed -i 's/#vcpu_pin_set=<VCPU_PIN_SET>/vcpu_pin_set='${value}'/g' /etc/nova/nova.conf


echo "done######"

