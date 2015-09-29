'''
Created on Aug 27, 2015

@author: zhangbai
'''
from common.shell.ShellCmdExecutor import ShellCmdExecutor

class Prerequisites(object):
    '''
    classdocs
    '''
    SYS_CTL_FILE_PATH = "/etc/sysctl.conf"
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def configSysCtlConfFile():
        #Use sysctl conf file template to replace original conf file
        '''
1.modify sysctl.conf
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
        '''
        
        #reload sys configuration
        ShellCmdExecutor.execCmd("sysctl -p")
        pass
    
    @staticmethod
    def install():
        print 'Prerequisites.install start====='
        Prerequisites.configSysCtlConfFile()
        print 'Prerequisites.install done####'
        pass
    
class HAProxy(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        ShellCmdExecutor.execCmd("yum install haproxy -y")
        pass
    
        
class Network(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Network.install start===='
        #Install Openstack network services
        yumCmd = "yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch"
        ShellCmdExecutor.execCmd(yumCmd)
        
        Network.configConfFile()
        #On Controller node, do Nova.configAfterNetworkNodeConfiguration(), Nova.restart()
        
        Network.configML2()
        Network.startOVS()
        Network.addNetworkBridgeCard2OVS()
        
        # create soft link: from ml2_conf.ini to plugin.ini
        ShellCmdExecutor.execCmd("ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini")
        
        # create neutron-openvswitch-agent
        ShellCmdExecutor.execCmd("cp /etc/init.d/neutron-openvswitch-agent /etc/init.d/neutron-openvswitch-agent.orig")
        ShellCmdExecutor.execCmd("sed -i 's,plugins/openvswitch/ovs_neutron_plugin.ini,plugin.ini,g' /etc/init.d/neutron-openvswitch-agent")
       
        Network.startNeutron()
        print 'Network.install done####'
        pass
    
    @staticmethod
    def startNeutron():
        ShellCmdExecutor.execCmd("service neutron-openvswitch-agent start")
        ShellCmdExecutor.execCmd("service neutron-l3-agent start")
        ShellCmdExecutor.execCmd("service neutron-dhcp-agent start")
        ShellCmdExecutor.execCmd("service neutron-metadata-agent start")
        
        ShellCmdExecutor.execCmd("chkconfig neutron-openvswitch-agent on")
        ShellCmdExecutor.execCmd("chkconfig neutron-l3-agent on")
        ShellCmdExecutor.execCmd("chkconfig neutron-dhcp-agent on")
        ShellCmdExecutor.execCmd("chkconfig neutron-metadata-agent on")
        pass
    
    @staticmethod
    def stopNeutron():
        ShellCmdExecutor.execCmd("service neutron-openvswitch-agent stop")
        ShellCmdExecutor.execCmd("service neutron-l3-agent stop")
        ShellCmdExecutor.execCmd("service neutron-dhcp-agent stop")
        ShellCmdExecutor.execCmd("service neutron-metadata-agent stop")
        pass
    
    @staticmethod
    def configConfFile():
        #Use conf file template to replace conf file 
        '''
1.configure /etc/neutron/neutron.conf

[DEFAULT]
auth_strategy = keystone

rpc_backend = neutron.openstack.common.rpc.impl_kombu
rabbit_host = controller
rabbit_password = 123456
core_plugin=ml2
service_plugins=router

[keystone_authtoken]
auth_uri=http://controller:5000
auth_host=controller
auth_protocal=http
auth_port=35357
admin_tenant_name=service
admin_user=neutron
admin_password=123456

2.config l3_agent.ini:

[DEFAULT]
interface_driver=neutron.agent.linux.interface.OVSInterfaceDriver
use_namespaces=true
external_network_bridge =  (The value is null, qg-xxx interface can be loaded to br-int automatically)

3.configure DHCP Agent,modify dhcp_agent.ini:

[DEFAULT]
interface_driver=neutron.agent.linux.interface.OVSInterfaceDriver
dhcp_driver=neutron.agent.linux.dhcp.Dnsmasq
use_namespaces=true

4.configure metadata agent: modify metadata_agent.ini:

[DEFAULT]
auth_url=http://controller:5000/v2.0
auth_region=regionOne
admin_tenant_name=service
admin_user=neutron
admin_password=123456
nova_metadata_ip=192.168.XX.XX    # controller node ip
metadata_proxy_shared_secret=123456    #The same with nova.conf

        '''
        pass
    
    @staticmethod
    def configML2():
        '''
1. on Network Node: configure ML2 on Network node:
modify /etc/neutron/plugins/ml2/ml2_conf.ini

[ml2]
type_driver=gre,flat
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
local_ip = 192.168.XXX.XXX  # network node ip address
tunnel_type = gre
enable_tunneling = True
bridge_mappings=physnet1:br-eth0

        '''
        pass
    
    @staticmethod
    def startOVS():
        #start openvswitch:set chkconfig
        ShellCmdExecutor.execCmd("service openvswitch start")
        ShellCmdExecutor.execCmd("chkconfig openvswitch on")
        pass
    
    @staticmethod
    def addNetworkBridgeCard2OVS():
        '''
1.add network-bridge and network-card to OVS

# ovs-vsctl add-br br-int
# ovs-vsctl add-br br-ex

# ovs-vsctl add-br br-eth0
# ovs-vsctl add-port br-eth0 eth0

###  add eth0 ip addr to br-eth0
# ifconfig eth0 0.0.0.0
#ifconfig br-eth0  xxx.xxx.xxx.xxx    ----eth0 ip address
        '''
        ShellCmdExecutor.execCmd("ovs-vsctl add-br br-int")
        ShellCmdExecutor.execCmd("ovs-vsctl add-br br-ex")
        ShellCmdExecutor.execCmd("ovs-vsctl add-br br-eth0")
        ShellCmdExecutor.execCmd("ovs-vsctl add-port br-eth0 eth0")
        ShellCmdExecutor.execCmd("ifconfig eth0 0.0.0.0")
        eth0IPAddr = Network.getEth0IPAddr()
        ShellCmdExecutor.execCmd("ifconfig br-eth0 %s" % eth0IPAddr)
        pass
    
    @staticmethod
    def getEth0IPAddr():
        print 'To be implemented===='
        pass
    pass

class FWaaS(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        '''
Install FWaaS services:
1)    on Controller, Network node: modify neutron.conf
#### service_plugins add fwaas
service_plugins=router,firewall

2)    modify fwaas.ini conf file: /etc/neutron/fwaas_driver.ini

[fwaas]
driver = neutron.services.firewall.drivers.linux.iptables_fwaas.IptablesFwaasDriver
enabled = True

        '''
        #####restart neutron-l3-agent @network node
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-l3-agent restart")
        
        pass
    

class LoadBalance(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod()
    def install():
        '''
1)    on Neutron-Controller and Network: neutron.conf

[DEFAULT]
service_plugins= router,firewall,lbaas

2)    on lbaas.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
ovs_use_veth = True
device_driver = neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver
    '''
        ShellCmdExecutor.execCmd("yum install haproxy -y")
        ShellCmdExecutor.execCmd("groupadd nogroup")
        ShellCmdExecutor.execCmd("useradd -g nogroup nobody")
        
        #restart neutron-lbaas-agent
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-lbaas-agent restart")
        ShellCmdExecutor.execCmd("chkconfig neutron-lbaas-agent on")
        pass
    
    @staticmethod()
    def start():
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-lbaas-agent start")
        pass
    
    @staticmethod()
    def restart():
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-lbaas-agent restart")
        pass
    

if __name__ == '__main__':
    print 'openstack-icehouse:network start============'
    Network.install()
    print 'openstack-icehouse:network done#######'
    pass

