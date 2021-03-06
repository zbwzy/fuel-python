'''
Created on Sept 26, 2015

@author: zhangbai
'''

'''
usage:

python network.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time

reload(sys)
sys.setdefaultencoding('utf8')

debug = False

if debug == True :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

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
        if os.path.exists('/etc/sysctl.conf') :
            ShellCmdExecutor.execCmd("rm -rf /etc/sysctl.conf")
            pass
        
        sysctl_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'sysctl.conf')
        ShellCmdExecutor.execCmd('cat %s > /tmp/sysctl.conf' % sysctl_template_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/sysctl.conf /etc/')
        #reload sys configuration
        output, exitcode = ShellCmdExecutor.execCmd("sysctl -p")
        print 'configSysCtlConfFile.output=%s--' % output
        pass
    
    @staticmethod
    def install():
        print 'Prerequisites.install start====='
        Prerequisites.configSysCtlConfFile()
        print 'Prerequisites.install done####'
        pass
    

class Network(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    NEUTRON_L3_CONF_FILE_PATH = "/etc/neutron/l3_agent.ini"
    NEUTRON_DHCP_CONF_FILE_PATH = "/etc/neutron/dhcp_agent.ini"
    NEUTRON_METADATA_CONF_FILE_PATH = "/etc/neutron/metadata_agent.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Network.install start===='
        Prerequisites.install()
        #Install Openstack network services
        yumCmd = "yum install openstack-neutron \
        openstack-neutron-ml2 openstack-neutron-openvswitch \
        python-neutronclient which -y"
        
        ShellCmdExecutor.execCmd(yumCmd)
        
        Network.configConfFile()
        
        print 'Network.install done####'
        pass
    
    @staticmethod
    def configML2():
        if os.path.exists(Network.NEUTRON_ML2_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_ML2_CONF_FILE_PATH)
            pass
        
        ml2_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'ml2_conf.ini') 
        ShellCmdExecutor.execCmd('cat %s > /tmp/ml2_conf.ini' % ml2_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/ml2_conf.ini /etc/neutron/plugins/ml2/')
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        FileUtil.replaceFileContent(Network.NEUTRON_ML2_CONF_FILE_PATH, '<INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS>', localIP)
        pass
    
    @staticmethod
    def configL3Agent():
        if os.path.exists(Network.NEUTRON_L3_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_L3_CONF_FILE_PATH)
            pass
        
        neutron_l3_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'l3_agent.ini')
        print 'neutron_l3_template_conf_file_path=%s--' % neutron_l3_template_conf_file_path
        ShellCmdExecutor.execCmd('cat %s > /tmp/l3_agent.ini' % neutron_l3_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/l3_agent.ini /etc/neutron/')
        pass
    
    @staticmethod
    def configDHCPAgent():
        if os.path.exists(Network.NEUTRON_DHCP_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_DHCP_CONF_FILE_PATH)
            pass
        
        neutron_dhcp_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'dhcp_agent.ini')
        print 'neutron_dhcp_template_conf_file_path=%s--' % neutron_dhcp_template_conf_file_path
        ShellCmdExecutor.execCmd('cat %s > /tmp/dhcp_agent.ini' % neutron_dhcp_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/dhcp_agent.ini /etc/neutron/')
        pass
    
    @staticmethod
    def configMetadataAgent():
        if os.path.exists(Network.NEUTRON_METADATA_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_METADATA_CONF_FILE_PATH)
            pass
        
        neutron_metadata_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'metadata_agent.ini')
        ShellCmdExecutor.execCmd('cat %s > /tmp/metadata_agent.ini' % neutron_metadata_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/metadata_agent.ini /etc/neutron/')
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        nova_vip = JSONUtility.getValue("nova_vip")
        #REFACTOR LATER
        neutron_admin_password = '123456'
        
        metadata_secret = JSONUtility.getValue("metadata_secret")
        
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<NOVA_VIP>', nova_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<NEUTRON_PASS>', neutron_admin_password)
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<METADATA_SECRET>', metadata_secret)
        pass
    
    @staticmethod
    def configOVS():
        output, exitcode = ShellCmdExecutor.execCmd('service openvswitch restart')
        print 'start openvswitch, output=%s' % output
        time.sleep(3)
        #Add the external bridge:
        ShellCmdExecutor.execCmd('ovs-vsctl add-br br-ex')
        time.sleep(2)
        #Add a port to the external bridge that connects to the physical external network interface:
        #Replace INTERFACE_NAME with the actual interface name. For example, eth2 or ens256.
        #REFACTOR LATER
        physical_external_network_interface = 'eth2'
#         addExternalBridgeCmd = 'ovs-vsctl add-port br-ex %s' % physical_external_network_interface
        addExternalBridgeTemplateScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'addExternalBridge.sh')
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % addExternalBridgeTemplateScriptPath)
        FileUtil.replaceFileContent('/opt/addExternalBridge.sh', 
                                    '<PHYSICAL_EXTERNAL_NETWORK_INTERFACE>', 
                                    physical_external_network_interface)
#         output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
#         localIP = output.strip()
#         FileUtil.replaceFileContent('/opt/addExternalBridge.sh', 
#                                     '<LOCAL_IP>', 
#                                     localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/addExternalBridge.sh')
        pass
    
    @staticmethod
    def finalizeInstallation():
        ShellCmdExecutor.execCmd('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
        ShellCmdExecutor.execCmd('sed -i \'s,plugins/openvswitch/ovs_neutron_plugin.ini,plugin.ini,g\' /etc/init.d/neutron-openvswitch-agent')
        ShellCmdExecutor.execCmd('cp /etc/init.d/neutron-openvswitch-agent /etc/init.d/neutron-openvswitch-agent.orig')
        
        ShellCmdExecutor.execCmd('chown -R neutron:neutron /etc/neutron')
        Network.startNeutron()
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
    def restartNeutron():
        ShellCmdExecutor.execCmd("service neutron-openvswitch-agent restart")
        ShellCmdExecutor.execCmd("service neutron-l3-agent restart")
        ShellCmdExecutor.execCmd("service neutron-dhcp-agent restart")
        ShellCmdExecutor.execCmd("service neutron-metadata-agent restart")
    
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
        #configure neutron.conf on network node
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
        #configure /etc/neutron/neutron.conf
        if os.path.exists(Network.NEUTRON_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_CONF_FILE_PATH)
            pass
        
        neutron_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'neutron.conf')
        ShellCmdExecutor.execCmd("cat %s > /tmp/neutron.conf" % neutron_template_conf_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/neutron.conf /etc/neutron/")
        
#         rabbit_host = JSONUtility.getValue("rabbit_host")
#         rabbit_vip = JSONUtility.getValue("rabbit_vip")
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        #REFACTOR LATER
        neutron_admin_password = '123456'
        
#         FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_HOST>', rabbit_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<NEUTRON_PASS>', neutron_admin_password)
        #configure agent
        Network.configML2()
        Network.configL3Agent()
        Network.configDHCPAgent()
        Network.configMetadataAgent()
        Network.configOVS()
        #######
        
        ShellCmdExecutor.execCmd('chown -R neutron:neutron %s' % Network.NEUTRON_CONF_FILE_PATH)
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
    
    @staticmethod
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
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-lbaas-agent start")
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-lbaas-agent restart")
        pass
    

if __name__ == '__main__':
    print 'openstack-icehouse:network start============'
    INSTALL_TAG_FILE = '/opt/network_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'network installed####'
        print 'exit===='
        pass
    else :
        Network.install()
        Network.configConfFile()
        
    print 'openstack-icehouse:network done#######'
    pass

