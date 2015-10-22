# fuel-python
1).This project deployment dir:
/etc/puppet

2).Use real env:
In conf/openstack_env.conf:
OPENSTACK_CONF_BASE_DIR = /etc/puppet/openstack_conf

3).Before execute this project:
init openstack params, and the parameters are put into /etc/puppet/openstack_conf/openstack_params.json like below:
{
    "mysql_vip": "192.168.11.128",
    "rabbit_host": "192.168.11.128",
    "keystone_vip": "192.168.11.100",
    "keystone_ips": "192.168.11.128,192.168.11.129",
    "glance_vip" : "192.168.11.100",
    "glance_ips": "192.168.11.128,192.168.11.129",
    "nova_vip" : "192.168.11.100",
    "nova_ips": "192.168.11.128,192.168.11.129",
    "glance_vip_interface" : "eth0",
    "keystone_vip_interface" : "eth0",
    "nova_vip_interface" : "eth0"
    
}



