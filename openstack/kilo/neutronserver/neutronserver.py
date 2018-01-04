'''
Created on Sept 27, 2015

@author: zhangbai
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
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil  
from common.yaml.YAMLUtil import YAMLUtil
from openstack.kilo.ssh.SSH import SSH 
from openstack.common.serverSequence import ServerSequence

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
    def prepare():
        Network.Prepare()
        
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
    

class Network(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def Prepare():
        Network.stopIPTables()
        Network.stopNetworkManager()
        pass
    
    @staticmethod
    def stopIPTables():
        stopCmd = "service iptables stop"
        ShellCmdExecutor.execCmd(stopCmd)
        pass
    
    @staticmethod
    def stopNetworkManager():
        stopCmd = "service NetworkManager stop"
        chkconfigOffCmd = "chkconfig NetworkManager off"
        
        ShellCmdExecutor.execCmd(stopCmd)
        ShellCmdExecutor.execCmd(chkconfigOffCmd)
        pass
    

class NeutronServer(object):
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
        print 'NeutronServer.install start===='
        #Install Openstack network services
        yumCmd = "yum install OpenIPMI openstack-neutron openstack-neutron-ml2 python-neutronclient which openstack-neutron-lbaas openstack-neutron-fwaas openstack-neutron-vpnaas -y"
        ShellCmdExecutor.execCmd(yumCmd)
        print 'NeutronServer.install done####'
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd('systemctl enable neutron-server.service')
        ShellCmdExecutor.execCmd('systemctl start neutron-server.service')
        
        ShellCmdExecutor.execCmd("systemctl enable ipmi.service")
        ShellCmdExecutor.execCmd("systemctl start ipmi.service")
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('systemctl restart neutron-server.service')
        pass
    
    @staticmethod
    def configConfFile():
        NeutronServer.configNeutronConfFile()
        
        NeutronServer.configML2()
        
        NeutronServer.configLBaaSAgent()
        
        ShellCmdExecutor.execCmd('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
        pass
    
    @staticmethod
    def importNeutronDBSchema():
        ######
        importNeutronDBSchemaCmd = 'su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf \
        --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron'
        output, exitcode = ShellCmdExecutor.execCmd(importNeutronDBSchemaCmd)
        print 'importNeutronSchemaOutput=%s--' % output
        
        importFwaasCmd = 'neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --service fwaas upgrade head'
        importLbaasCmd = 'neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --service lbaas upgrade head'
        importVpnCmd = 'neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --service vpnaas upgrade head'
        
        ShellCmdExecutor.execCmd(importFwaasCmd)
        ShellCmdExecutor.execCmd(importLbaasCmd)
        ShellCmdExecutor.execCmd(importVpnCmd)
        ########
    
    @staticmethod
    def upgradeLBDBSchema():
        upgradeCmd = 'neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --service lbaas upgrade head'
        output, exitcode = ShellCmdExecutor.execCmd(upgradeCmd)
        print 'upgradeCmdOutput=%s--' % output
        pass
        
        
    @staticmethod
    def configNeutronConfFile():
        '''
        NEUTRON_DBPASS
        MYSQL_VIP
        RABBIT_HOSTS
        RABBIT_PASSWORD
        KEYSTONE_VIP
        KEYSTONE_NEUTRON_PASSWORD
        '''
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]
        neutron_dbpass = JSONUtility.getValue("neutron_dbpass")
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        
        keystone_vip = vipParamsDict["keystone_vip"]
        nova_vip = vipParamsDict["nova_vip"]
        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        keystone_nova_password = JSONUtility.getValue("keystone_nova_password")
        
        localIP = YAMLUtil.getManagementIP() 
        print 'mysql_vip=%s' % mysql_vip
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'nova_vip=%s' % nova_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        if NeutronServer.isNetworkNode() :
            neutron_server_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'neutron.conf.merge')
            pass
        else :
            neutron_server_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'neutron.conf')
            pass
        
        print 'neutron_server_conf_template_file_path=%s' % neutron_server_conf_template_file_path
        
        neutronConfDir = '/etc/neutron'
        if not os.path.exists(neutronConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % neutronConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % neutronConfDir)
        
        neutron_conf_file_path = os.path.join(neutronConfDir, 'neutron.conf')
        if os.path.exists(neutron_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % neutron_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/neutron.conf" % neutron_server_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/neutron.conf /etc/neutron/")
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<LOCAL_MANAGEMENT_VIP>', localIP)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
#         FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<NOVA_VIP>', nova_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<NEUTRON_DBPASS>', neutron_dbpass)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<KEYSTONE_NOVA_PASSWORD>', keystone_nova_password)
        
#         FileUtil.replaceFileContent(neutron_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("chmod 644 %s" % neutron_conf_file_path)
        ShellCmdExecutor.execCmd("chown -R neutron:neutron /etc/neutron/")
        pass
    
    @staticmethod
    def configML2():
        if os.path.exists(NeutronServer.NEUTRON_ML2_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd('rm -rf %s' % NeutronServer.NEUTRON_ML2_CONF_FILE_PATH)
            pass
        
        NEUTRON_ML2_CONF_DIR = '/etc/neutron/plugins/ml2/'
        if not os.path.exists(NEUTRON_ML2_CONF_DIR) :
            os.system("mkdir -p %s" % NEUTRON_ML2_CONF_DIR)
            pass
        
        if NeutronServer.isNetworkNode() :
            neutron_server_ml2_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ml2_conf.ini.merge')
            pass
        else :
            neutron_server_ml2_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ml2_conf.ini')
            pass
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/ml2_conf.ini' % neutron_server_ml2_template_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/ml2_conf.ini /etc/neutron/plugins/ml2/')
        
#         ShellCmdExecutor.execCmd('cp -r %s %s' % (neutron_server_ml2_template_file_path, NEUTRON_ML2_CONF_DIR))
        
        vlan_range = YAMLUtil.getVlanRange()
        FileUtil.replaceFileContent(NeutronServer.NEUTRON_ML2_CONF_FILE_PATH, '<VLAN_RANGE>', vlan_range)
        
        if NeutronServer.isNetworkNode() :
            #The string INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS should be replaced by business ip
            localIP = YAMLUtil.getExIP()
            FileUtil.replaceFileContent(NeutronServer.NEUTRON_ML2_CONF_FILE_PATH, '<INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS>', localIP)
            pass
        pass
    
    @staticmethod
    def configLBaaSAgent():
        NEUTRON_LB_CONF_FILE_PATH1 = '/etc/neutron/neutron_lbaas.conf'
        if os.path.exists(NEUTRON_LB_CONF_FILE_PATH1) :
            ShellCmdExecutor.execCmd("rm -rf %s" % NEUTRON_LB_CONF_FILE_PATH1)
            pass
        
        neutron_lb_template_conf_file_path1 = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'neutron_lbaas.conf')
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (neutron_lb_template_conf_file_path1, '/etc/neutron/'))
        pass
    
    @staticmethod
    def getServerIndex():
        local_management_ip = YAMLUtil.getManagementIP() 
        neutron_params_dict = JSONUtility.getRoleParamsDict('neutron-server')
        neutron_server_ip_list = neutron_params_dict["mgmt_ips"]
        index = ServerSequence.getIndex(neutron_server_ip_list, local_management_ip)
        return index
    
    @staticmethod
    def getPredefinedNetworks():
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        predefinedNetworksDict = dataMap['quantum_settings']['predefined_networks']
        return predefinedNetworksDict
    
    @staticmethod
    def getFloatingRange():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        floatingRange = predefinedNetworksDict['net04_ext']['L3']['floating']
        print 'floatingRange=%s--' % floatingRange
        if floatingRange == '' or floatingRange == None :
            floatingRange = '192.168.242.20:192.168.242.100'
            pass
        
        return floatingRange
    
    
    @staticmethod
    def getNet04ExtL3Gateway():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        gateway = predefinedNetworksDict['net04_ext']['L3']['gateway']
        print 'net04_ext_l3_gateway=%s--' % gateway
        if gateway == '' or gateway == None :
            gateway = '192.168.242.1'
            pass
        
        return gateway
    
    @staticmethod
    def getNet04ExtL3VlanID():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        vlan_id = predefinedNetworksDict['net04_ext']['L3']['vlan_id']
        print 'net04_ext_l3_vlanid=%s--' % vlan_id
        if vlan_id == '' or vlan_id == None :
            vlan_id = '100'
            pass
        
        return vlan_id
    
    @staticmethod
    def getNet04L3Gateway():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        gateway = predefinedNetworksDict['net04']['L3']['gateway']
        print 'net04_l3_gateway=%s--' % gateway
        if gateway == '' or gateway == None :
            gateway = '192.168.10.1'
            pass
        
        return gateway
    
    @staticmethod
    def getNet04L3Subnet():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        subnet = predefinedNetworksDict['net04']['L3']['subnet']
        print 'net04_l3_subnet=%s--' % subnet
        if subnet == '' or subnet == None :
            subnet = '192.168.10.0/24'
            pass
        
        return subnet
    
    @staticmethod
    def getBasicNetRange():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        ipRange = predefinedNetworksDict['basic_net']['L3']['range']
        print 'basicNetworkRange=%s--' % ipRange
        if ipRange == '' or ipRange == None :
            ipRange = '192.168.242.20:192.168.242.100'
            pass
        
        return ipRange
    
    
    @staticmethod
    def getBasicNetworkL3Gateway():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        gateway = predefinedNetworksDict['basic_net']['L3']['gateway']
        print 'basic_network_l3_gateway=%s--' % gateway
        if gateway == '' or gateway == None :
            gateway = '192.168.242.1'
            pass
        
        return gateway
    
    @staticmethod
    def getBasicNetworkL3VlanID():
        predefinedNetworksDict = NeutronServer.getPredefinedNetworks()
        vlan_id = predefinedNetworksDict['basic_net']['L3']['vlan_id']
        print 'basic_network_l3_vlanid=%s--' % vlan_id
        if vlan_id == '' or vlan_id == None :
            vlan_id = '101'
            pass
        
        return vlan_id
    
    @staticmethod
    def isNetworkNode():
        networkNodeMgmtIPList = YAMLUtil.getRoleManagementIPList('neutron-agent')
        localMgmtIP = YAMLUtil.getManagementIP()
        print 'networkNodeMgmtIPList=%s--' % networkNodeMgmtIPList
        print 'localMgmtIP=%s--' % localMgmtIP
        if localMgmtIP in networkNodeMgmtIPList :
            return True
        else :
            return False
        pass
    
    @staticmethod
    def implement_lldp():
        print 'implement_lldp========'
        role = 'neutron-agent'
        key = 'neutron_network_mode'
        network_mode = YAMLUtil.getValue(role, key)
        
#         if network_mode == 'vlan' :
        ShellCmdExecutor.execCmd('yum install lldpad -y')
        ShellCmdExecutor.execCmd('lldpad -d')
        
        mgmt_interface_names = YAMLUtil.getInterfacesByBridge('br-mgmt')
        for interface_name in mgmt_interface_names:
            
            cmd1 = 'lldptool set-lldp -i {interface_name} adminStatus=rxtx'.format(interface_name=interface_name)
            cmd2 = 'lldptool -T -i {interface_name} -V  sysName enableTx=yes'.format(interface_name=interface_name)
            cmd3 = 'lldptool -T -i {interface_name} -V  portDesc enableTx=yes'.format(interface_name=interface_name)
            cmd4 = 'lldptool -T -i {interface_name} -V  sysDesc enableTx=yes'.format(interface_name=interface_name)
            cmd5 = 'lldptool -T -i {interface_name} -V sysCap enableTx=yes'.format(interface_name=interface_name)
            cmd6 = 'lldptool -T -i {interface_name} -V mngAddr enableTx=yes'.format(interface_name=interface_name)
            ShellCmdExecutor.execCmd(cmd1)
            ShellCmdExecutor.execCmd(cmd2)
            ShellCmdExecutor.execCmd(cmd3)
            ShellCmdExecutor.execCmd(cmd4)
            ShellCmdExecutor.execCmd(cmd5)
            ShellCmdExecutor.execCmd(cmd6)
        print 'implement_lldp#########'
        pass
    
    
    
    
    


if __name__ == '__main__':
    ###TEST
#     print 'floating_range=%s--' % NeutronServer.getFloatingRange()
#     print 'net04_ext_l3_gateway=%s--' % NeutronServer.getNet04ExtL3Gateway()
#     print NeutronServer.getNet04L3Gateway()
#     print NeutronServer.getNet04L3Subnet()
#     
#     ips = NeutronServer.getFloatingRange().split(':')
#     print 'splitted_ips=%s--' % ips
#     print 'start_ip=%s--' % ips[0]
#     print 'end_ip=%s--' % ips[1]
#     
#     print '.'.join(ips[1].split('.')[0:3]) + '.0/24'
#     exit()
    #####TEST
    print 'openstack-kilo:neutron-server start============'
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/neutronserver_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'neutron-server installed####'
        print 'exit===='
        pass
    else :
        NeutronServer.install()
        
        NeutronServer.configConfFile()
        #ICBC patch
        from openstack.kilo.common.net import Net
        Net.patch()
        ############
        
        #patch
        from openstack.kilo.common.patch import Patch
        Patch.patchOsloDbApi()
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'openstack-kilo:neutron-server done#######'
    pass

