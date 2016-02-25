'''
Created on Dec 18, 2015

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

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil   
    

class VXLANConfig(object):
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
    def start():
        ShellCmdExecutor.execCmd('service neutron-server start')
        ShellCmdExecutor.execCmd('chkconfig neutron-server on')
        pass
    
    @staticmethod
    def isNeutronServerRole():
        if os.path.exists('/opt/is_neutron_server_role') :
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isNeutronAgentRole(): #network node
        if os.path.exists('/opt/is_neutron_agent_role'):
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isNovaComputeRole():
        if os.path.exists('/opt/is_nova_compute_role'):
            return True
        else :
            return False
        pass
    
    @staticmethod
    def reConfigureML2():
        #support vxlan network mode
        network_mode = JSONUtility.getValue('neutron_network_mode')
        network_mode = network_mode.strip()
        
        if network_mode == 'vxlan' :
            FileUtil.replaceFileContent(VXLANConfig.NEUTRON_ML2_CONF_FILE_PATH, 'type_drivers = flat,gre', 'type_drivers = vxlan,flat,gre')
            FileUtil.replaceFileContent(VXLANConfig.NEUTRON_ML2_CONF_FILE_PATH, 'tenant_network_types = gre', 'tenant_network_types = vxlan,gre')
            FileUtil.replaceFileContent(VXLANConfig.NEUTRON_ML2_CONF_FILE_PATH, '#vni_ranges = 1:1000', 'vni_ranges = 1:1000')
            FileUtil.replaceFileContent(VXLANConfig.NEUTRON_ML2_CONF_FILE_PATH, 'tunnel_types = gre', 'tunnel_types = vxlan')
            pass
        pass
    
    @staticmethod
    def restart():
        #support vxlan network mode
        if VXLANConfig.isNeutronServerRole() :
            ShellCmdExecutor.execCmd('/etc/init.d/neutron-server restart')
            pass
        
        if VXLANConfig.isNovaComputeRole() or VXLANConfig.isNeutronAgentRole():
            ShellCmdExecutor.execCmd('/etc/init.d/neutron-openvswitch-agent restart')
            pass
        pass
    pass

if __name__ == '__main__':
    print 'openstack-icehouse:configure vxlan start============'
    VXLAN_TAG_FILE = '/opt/vxlan_configured'
    if os.path.exists(VXLAN_TAG_FILE) :
        print 'vxlan configured####'
        print 'exit===='
        pass
    else :
#         VXLANConfig.reConfigureML2()
#         VXLANConfig.restart()
        
        os.system('touch %s' % VXLAN_TAG_FILE)
    print 'openstack-icehouse:configure vxlan done#######'
    pass

