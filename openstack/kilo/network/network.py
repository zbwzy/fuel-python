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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil

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
    NEUTRON_LB_CONF_FILE_PATH = "/etc/neutron/lbaas_agent.ini"
    NEUTRON_VPN_CONF_FILE_PATH = "/etc/neutron/neutron_vpnaas.conf"
    NEUTRON_METADATA_CONF_FILE_PATH = "/etc/neutron/metadata_agent.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Network.install start===='
        #Install Openstack network services
        yumCmd = "yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch openstack-neutron-lbaas openstack-neutron-fwaas openstack-neutron-vpn-agent -y"
        ShellCmdExecutor.execCmd(yumCmd)
#         Network.configConfFile()
        print 'Network.install done####'
        pass
    
    @staticmethod
    def configML2():
        if os.path.exists(Network.NEUTRON_ML2_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_ML2_CONF_FILE_PATH)
            pass
        if Network.isNeutronServerNode() :
            #Network node is also neutron-server node
            ml2_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ml2_conf.ini.merge')
            pass
        else :
            ml2_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'ml2_conf.ini') 
            pass
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/ml2_conf.ini' % ml2_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/ml2_conf.ini /etc/neutron/plugins/ml2/')
        
        localExIP = YAMLUtil.getExIP()
        FileUtil.replaceFileContent(Network.NEUTRON_ML2_CONF_FILE_PATH, '<INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS>', localExIP)
        
        if Network.isNeutronServerNode() :
            vlan_range = YAMLUtil.getVlanRange()
            FileUtil.replaceFileContent(Network.NEUTRON_ML2_CONF_FILE_PATH, '<VLAN_RANGE>', vlan_range)
            pass
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
        
        dnsmasqConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'dnsmasq-neutron.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/neutron' % dnsmasqConfFileTemplatePath)
        pass
    
    
    @staticmethod
    def configLBaaSAgent():
        if os.path.exists(Network.NEUTRON_LB_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_LB_CONF_FILE_PATH)
            pass
        
        neutron_lb_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'lbaas_agent.ini')
        print 'neutron_lb_template_conf_file_path=%s--' % neutron_lb_template_conf_file_path
        ShellCmdExecutor.execCmd('cat %s > /tmp/lbaas_agent.ini' % neutron_lb_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/lbaas_agent.ini /etc/neutron/')
        pass
    
    
    @staticmethod
    def configVPNaaSConf():
        if os.path.exists(Network.NEUTRON_VPN_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_VPN_CONF_FILE_PATH)
            pass
        
        neutron_vpn_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'neutron_vpnaas.conf')
        print 'neutron_vpn_template_conf_file_path=%s--' % neutron_vpn_template_conf_file_path
        ShellCmdExecutor.execCmd('cat %s > /tmp/neutron_vpnaas.conf' % neutron_vpn_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/neutron_vpnaas.conf /etc/neutron/')
        pass
    
    @staticmethod
    def configMetadataAgent():
        if os.path.exists(Network.NEUTRON_METADATA_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Network.NEUTRON_METADATA_CONF_FILE_PATH)
            pass
        
        neutron_metadata_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'metadata_agent.ini')
        ShellCmdExecutor.execCmd('cat %s > /tmp/metadata_agent.ini' % neutron_metadata_template_conf_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/metadata_agent.ini /etc/neutron/')
        
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        nova_vip = vipParamsDict["nova_vip"]
        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        
        network_node_params_dict = JSONUtility.getRoleParamsDict('network')
        metadata_secret = network_node_params_dict["metadata_secret"]
        
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<NOVA_VIP>', nova_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        FileUtil.replaceFileContent(Network.NEUTRON_METADATA_CONF_FILE_PATH, '<METADATA_SECRET>', metadata_secret)
        pass
    
    @staticmethod
    def configOVS():
        output, exitcode = ShellCmdExecutor.execCmd('systemctl enable openvswitch.service')
        output, exitcode = ShellCmdExecutor.execCmd('systemctl start openvswitch.service')
        time.sleep(3)
        #Add br-int bridge:
        ShellCmdExecutor.execCmd('ovs-vsctl add-br br-int')
        time.sleep(2)
        #Add a port to the external bridge that connects to the physical external network interface:
        #Replace INTERFACE_NAME with the actual interface name. For example, eth2 or ens256.
        
#         physical_external_network_interface = 'eth2'
#         networkParams = JSONUtility.getRoleParamsDict('network')
#         physical_external_network_interface = networkParams['physical_external_network_interface'].strip()
        
#         addExternalBridgeCmd = 'ovs-vsctl add-port br-ex %s' % physical_external_network_interface
        addExternalBridgeTemplateScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'addExternalBridge.sh')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % addExternalBridgeTemplateScriptPath)
#         FileUtil.replaceFileContent('/opt/openstack_conf/scripts/addExternalBridge.sh', 
#                                     '<PHYSICAL_EXTERNAL_NETWORK_INTERFACE>', 
#                                     physical_external_network_interface)
#         localIP = YAMLUtil.getManagementIP() 
#         FileUtil.replaceFileContent('/opt/addExternalBridge.sh', 
#                                     '<LOCAL_IP>', 
#                                     localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/addExternalBridge.sh')
        pass
    
    @staticmethod
    def start():
        Network.startNeutron()
        pass
    
    @staticmethod
    def finalizeInstallation():
        ShellCmdExecutor.execCmd('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
        ShellCmdExecutor.execCmd('cp /usr/lib/systemd/system/neutron-openvswitch-agent.service /usr/lib/systemd/system/neutron-openvswitch-agent.service.orig')
        ShellCmdExecutor.execCmd('sed -i \'s,plugins/openvswitch/ovs_neutron_plugin.ini,plugin.ini,g\' /usr/lib/systemd/system/neutron-openvswitch-agent.service')
        
        ShellCmdExecutor.execCmd('chown -R neutron:neutron /etc/neutron')
        Network.startNeutron()
        
        ##add br-ex to business net
        from openstack.kilo.common.net import Net
        interfaceName = Net.getInterfaceNameByBridge('br-data')
        ifNameWithoutVlanTag = interfaceName.split('.')[0]
        addPortCmd = 'ovs-vsctl add-port br-ex %s' % ifNameWithoutVlanTag
        ShellCmdExecutor.execCmd(addPortCmd)
        pass
    
    @staticmethod
    def startNeutron():
        ShellCmdExecutor.execCmd("systemctl enable neutron-openvswitch-agent.service")
        ShellCmdExecutor.execCmd("systemctl enable neutron-l3-agent.service")
        ShellCmdExecutor.execCmd("systemctl enable neutron-dhcp-agent.service")
        ShellCmdExecutor.execCmd("systemctl enable neutron-metadata-agent.service")
        ShellCmdExecutor.execCmd("systemctl enable neutron-ovs-cleanup.service")
        
        ShellCmdExecutor.execCmd("systemctl start neutron-openvswitch-agent.service")
        ShellCmdExecutor.execCmd("systemctl start neutron-l3-agent.service")
        ShellCmdExecutor.execCmd("systemctl start neutron-dhcp-agent.service")
        ShellCmdExecutor.execCmd("systemctl start neutron-metadata-agent.service")
        
        #start bridges
        ShellCmdExecutor.execCmd('ifconfig br-ex up')
        ShellCmdExecutor.execCmd('ifconfig br-int up')
        ShellCmdExecutor.execCmd('ifconfig br-tun up')
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
        
        if Network.isNeutronServerNode() :
            #Network node is also neutron-server node
            neutron_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'neutron.conf.merge')
            pass
        else :
            neutron_template_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'neutron.conf')
            pass
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/neutron.conf" % neutron_template_conf_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/neutron.conf /etc/neutron/")
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
#         rabbit_userid = rabbit_params_dict("rabbit_userid")
        rabbit_password = rabbit_params_dict["rabbit_password"]
        
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_HOSTS>', rabbit_hosts)
#         FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        
        if Network.isNeutronServerNode() :
            nova_vip = vipParamsDict["nova_vip"]
            localIP = YAMLUtil.getManagementIP()
            neutron_dbpass = JSONUtility.getValue("neutron_dbpass")
            mysql_vip = vipParamsDict["mysql_vip"]
            keystone_nova_password = JSONUtility.getValue("keystone_nova_password")
            
            FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<NOVA_VIP>', nova_vip)
            FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<LOCAL_MANAGEMENT_VIP>', localIP)
            FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<NEUTRON_DBPASS>', neutron_dbpass)
            FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<MYSQL_VIP>', mysql_vip)
            FileUtil.replaceFileContent(Network.NEUTRON_CONF_FILE_PATH, '<KEYSTONE_NOVA_PASSWORD>', keystone_nova_password)
            pass
        
        #configure agent
        Network.configML2()
        Network.configL3Agent()
        Network.configDHCPAgent()
        Network.configLBaaSAgent()
        Network.configVPNaaSConf()
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
    
    @staticmethod
    def isNeutronServerNode():
        neutronServerNodeMgmtIPList = YAMLUtil.getRoleManagementIPList('neutron-server')
        localMgmtIP = YAMLUtil.getManagementIP()
        print 'neutronServerNodeMgmtIPList=%s--' % neutronServerNodeMgmtIPList
        print 'localMgmtIP=%s--' % localMgmtIP
        if localMgmtIP in neutronServerNodeMgmtIPList :
            return True
        else :
            return False
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
    print 'openstack-kilo:network============'
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/network_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'network installed####'
        print 'exit===='
        pass
    else :
        Network.install()
        Network.configConfFile()
        #patch
        from openstack.kilo.common.patch import Patch
        Patch.patchOsloDbApi()
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        
        os.system('touch %s' % INSTALL_TAG_FILE)
        pass
    print 'openstack-kilo:network done#######'
    pass

