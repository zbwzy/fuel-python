'''
Created on Aug 26, 2015

@author: zhangbai
'''
from openstack.icehouse.common.Utils import ShellCmdExecutor

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    pass

class Nova(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/nova/nova.conf"
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Nova.install on compute node start========'
        yumCmd = "yum install openstack-nova-compute -y"
        ShellCmdExecutor.execCmd(yumCmd)
        Nova.configConfFile()
        Nova.start()
        
        Nova.configAfterNetworkNodeConfiguration()
        print 'Nova.install on compute node done####'
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("service libvirtd start")
        ShellCmdExecutor.execCmd("service messagebus start")
        ShellCmdExecutor.execCmd("chkconfig libvirtd on")
        ShellCmdExecutor.execCmd("chkconfig messagebus on")
        ShellCmdExecutor.execCmd("service openstack-nova-compute start")
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-compute on")
        pass
    
    @staticmethod
    def configConfFile():
        #Use conf file template to replace the IP
        '''
[database]
connection=mysql://nova:123456@controller/nova

[DEFAULT]
auth_strategy=keystone
rpc_backend=rabbit
rabbit_host=controller
rabbit_password=123456
my_ip=<COMPUTE_IP>
vnc_enabled=true
vncserver_listen=0.0.0.0
vncserver_proxyclient_address=<COMPUTE_IP>
novncproxy_base_url=http://<CONTROLLER_IP>:6080/vnc_auto.html
glance_host=<CONTROLLER_IP>

[keystone_authtoken]
auth_uri=http://controller:5000
auth_host=<CONTROLLER_IP>
auth_protocol=http
auth_port=35357
admin_tenant_name=service
admin_user=nova
admin_password=123456


[libvirt]
virt_type=qemu
        '''
        pass
    
    @staticmethod
    def configAfterNetworkNodeConfiguration():
        '''
##modify sysctl config file :/etc/sysctl.conf
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
        '''
        #reload confinguration
        ShellCmdExecutor.execCmd("sysctl -p")
        ShellCmdExecutor.execCmd("chkconfig neutron-dhcp-agent on")
        
        #Install neutron's second layer Agent
        ShellCmdExecutor.execCmd("yum install openstack-neutron-ml2 openstack-neutron-openvswitch")
        
        '''
on Compute Node: neutron.conf

[DEFAULT]
auth_strategy=keystone
rpc_backend=neutron.openstack.common.rpc.impl_kombu
rabbit_host=controller
rabbit_password=123456
core_plugin=ml2
service_plugins=router

[keystone_authtoken]
auth_uri=http://controller:5000
auth_host=controller
auth_protocol=http
auth_port=35357
admin_tenant_name=service
admin_user=neutron
admin_password=123456
        '''
        
        '''
        4)  on Compute Node: modify ML2,/etc/neutron/plugins/ml2/ml2_conf.ini

[ml2]
type_drivers=gre,flat
tenant_network_types=gre,flat
mechanism_drivers=openvswitch

[ml2_type_flat]
flat_networks = physnet1

[ml2_type_gre]
tunnel_id_ranges =1:1000

[securitygroup]
firewall_driver=neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver
enable_security_group=true

[ovs]
local_ip = 192.168.242.131    ###compute node local ip
tunnel_type = gre
enable_tunneling = True
bridge_mappings=physnet1:br-eth0
        '''
        #start openvswitch and set chkconfig
        ShellCmdExecutor.execCmd("service openvswitch start")
        ShellCmdExecutor.execCmd("chkconfig openvswitch on")
        
        '''
        6)    add network-bridge and network-card to openvswitch


# ovs-vsctl add-br br-etho
# ovs-vsctl add-port br-eth0 eth0
###add eth0 ip addr to br-eth0
# ifconfig eth0 0.0.0.0
#ifconfig br-eth0  xxx.xxx.xxx.xxx    ---eth0 ip address
        '''
        #add network-bridge and network-card to openvswitch
        ShellCmdExecutor.execCmd("ovs-vsctl add-br br-int")
        ShellCmdExecutor.execCmd("ovs-vsctl add-br br-eth0")
        #add eth0 ip addr to br-eth0
        ShellCmdExecutor.execCmd("ifconfig eth0 0.0.0.0")
        ShellCmdExecutor.execCmd("ifconfig br-eth0  %s" % Nova.getEth0IPAddr())
        
        '''
        7)    on Compute Node: modify nova.conf: configue neutron to support network

[DEFAULT]
network_api_class=nova.network.neutronv2.api.API
neutron_url=http://controller:9696
neutron_auth_strategy=keystone
neutron_admin_tenant_name=service
neutron_admin_username=neutron
neutron_admin_password=123456
neutron_admin_auth_url=http://controller:35357/v2.0
linuxnet_interface_driver=nova.network.linux_net.LinuxOVSInterfaceDriver
firewall_driver=nova.virt.firewall.NoopFirewallDriver
security_group_api=neutron

8)    modify nova.conf to support VMs creations if vif_plug fails
vif_plugging_is_fatal=false
vif_plugging_timeout=0
        '''
        
        # create soft link: from ml2_conf.ini to plugin.ini
        ShellCmdExecutor.execCmd("ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini")
        
        #create neutron-openvswitch-agent services
        ShellCmdExecutor.execCmd("cp /etc/init.d/neutron-openvswitch-agent /etc/init.d/neutron-openvswitch-agent.orig")
        ShellCmdExecutor.execCmd("sed -i 's,plugins/openvswitch/ovs_neutron_plugin.ini,plugin.ini,g' /etc/init.d/neutron-openvswitch-agent")
        
        #start neutron-openvswitch and set chkconfig
        ShellCmdExecutor.execCmd("service neutron-openvswitch-agent start")
        ShellCmdExecutor.execCmd("chkconfig neutron-openvswitch-agent on")
        pass
    
    
    @staticmethod
    def getEth0IPAddr():
        print 'To be implemented...'
        pass
    pass


if __name__ == '__main__':
    print 'hello openstack-icehouse:compute============'
    Nova.install()
    print '#######'
    pass

