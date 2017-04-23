'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python cinder.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time

debug = False
if debug == True :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass

OPENSTACK_VERSION_TAG = 'newton'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

    
if __name__ == '__main__':
    print 'hello openstack-icehouse:confiugre nova after neutron============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    TAG_FILE = '/opt/configureNovaAfterNeutron'
    if os.path.exists(TAG_FILE) :
        print 'After neutron, nova configured####'
        print 'exit===='
        pass
    else :
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        neutron_vip = vipParamsDict["neutron_vip"]
        
        APIsAndDrivers = '''
network_api_class = nova.network.neutronv2.api.API
security_group_api = neutron
linuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver
firewall_driver = nova.virt.firewall.NoopFirewallDriver
'''
        APIsAndDrivers = APIsAndDrivers.strip()
        
        AccessParameters = '''
[neutron]
url = http://<NEUTRON_VIP>:9696
auth_strategy = keystone
admin_auth_url = http://<KEYSTONE_VIP>:35357/v2.0
admin_tenant_name = service
admin_username = neutron
admin_password = <NEUTRON_PASS>
        '''
        
        AccessParameters = AccessParameters.strip()
        AccessParameters = AccessParameters.replace('<NEUTRON_VIP>', neutron_vip)
        AccessParameters = AccessParameters.replace('<KEYSTONE_VIP>', keystone_vip)
        
        neutron_pass = '123456'
        AccessParameters = AccessParameters.replace('<NEUTRON_PASS>', neutron_pass)
        
        NOVA_API_CONF_FILE_PATH = '/etc/nova/nova.conf'
        
        FileUtil.replaceFileContent(NOVA_API_CONF_FILE_PATH, '#APIsAndDrivers', APIsAndDrivers)
        FileUtil.replaceFileContent(NOVA_API_CONF_FILE_PATH, '#AccessParameters', AccessParameters)
        
        #############################################
        FileUtil.replaceFileContent(NOVA_API_CONF_FILE_PATH, 
                                    '#vif_plugging_is_fatal=true', 
                                    'vif_plugging_is_fatal=false')
        FileUtil.replaceFileContent(NOVA_API_CONF_FILE_PATH, 
                                    '#vif_plugging_timeout=300', 
                                    'vif_plugging_timeout=0')
        
        ShellCmdExecutor.execCmd('service openstack-nova-api restart')
        ShellCmdExecutor.execCmd('service openstack-nova-scheduler restart')
        ShellCmdExecutor.execCmd('service openstack-nova-conductor restart')
        
        os.system('touch %s' % TAG_FILE)
        pass
    print 'Nova is configured after neutron#######'
    pass

