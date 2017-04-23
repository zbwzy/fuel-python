'''
Created on Nov 24, 2015

@author: zhangbai
'''

'''
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
SOURCE_NOVA_COMPUTE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova-compute', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil
from openstack.newton.common.net import Net


class NovaCompute(object):
    
    def __init__(self):
        pass
    
    @staticmethod
    def configurePrerequisites():
        sysctlConfTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'sysctl.conf')
        
        ShellCmdExecutor.execCmd('cp -r %s /etc/' % sysctlConfTemplateFilePath)
        ShellCmdExecutor.execCmd('sysctl -p')
        pass
    
    @staticmethod
    def install():
        installCmd = 'yum install openstack-neutron-linuxbridge ebtables ipset -y'
        ShellCmdExecutor.execCmd(installCmd)
        pass
    
    @staticmethod
    def confiugureNeutron():
        neutronConfTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'neutron.conf')
        
        ShellCmdExecutor.execCmd('cp -r %s /etc/neutron/' % neutronConfTemplateFilePath)
        #configure neutron
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        rabbit_vip = vipParamsDict["rabbit_vip"]
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        
        localIP = YAMLUtil.getManagementIP() 
        
        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        
        neutronConfFilePath = '/etc/neutron/neutron.conf'
        ShellCmdExecutor.execCmd('chmod 777 /etc/neutron/neutron.conf')
        FileUtil.replaceFileContent(neutronConfFilePath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(neutronConfFilePath, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        FileUtil.replaceFileContent(neutronConfFilePath, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(neutronConfFilePath, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(neutronConfFilePath, '<RABBIT_PASSWORD>', rabbit_password)
        FileUtil.replaceFileContent(neutronConfFilePath, '<LOCAL_MANAGEMENT_IP>', localIP)
        FileUtil.replaceFileContent(neutronConfFilePath, '<RABBIT_VIP>',rabbit_vip)
        
        ShellCmdExecutor.execCmd('chown -R neutron:neutron /etc/neutron')
        pass
    
    
    @staticmethod
    def configureLinuxBridgeAgent():
        linuxBridgeAgentConfTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'linuxbridge_agent.ini')
        ShellCmdExecutor.execCmd("cp -r %s %s" % (linuxBridgeAgentConfTemplatePath, "/etc/neutron/plugins/ml2/"))
        localIP = YAMLUtil.getManagementIP()
        FileUtil.replaceFileContent('/etc/neutron/plugins/ml2/', '<LOCAL_MANAGEMENT_IP>', localIP)
        pass
    
    @staticmethod
    def configureML2():
        ml2ConfTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'ml2_conf.ini')
#         ShellCmdExecutor.execCmd('cp -r %s /etc/neutron/plugins/ml2/' % ml2ConfTemplatePath)
#         
#         localExIP = YAMLUtil.getExIP()
#         FileUtil.replaceFileContent('/etc/neutron/plugins/ml2/ml2_conf.ini', '<INSTANCE_TUNNELS_INTERFACE_IP_ADDRESS>', localExIP)
        pass
    
    @staticmethod
    def configureOVS():
        ShellCmdExecutor.execCmd("systemctl enable openvswitch.service")
        ShellCmdExecutor.execCmd("systemctl start openvswitch.service")
        
#         scriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'addBridgeAndInterface.sh')
#         ShellCmdExecutor.execCmd('cp -r %s /opt/' % scriptPath)
#         
#         localIP = YAMLUtil.getManagementIP() 
#         
#         FileUtil.replaceFileContent('/opt/addBridgeAndInterface.sh', '<LOCAL_IP>', localIP)
#         ShellCmdExecutor.execCmd('bash /opt/addBridgeAndInterface.sh')
        pass
    
    #configure Compute to use networking
    @staticmethod
    def reconfigureNovaCompute():
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
        
        #REFACTOR LATER
        neutron_pass = '123456'
        AccessParameters = AccessParameters.replace('<NEUTRON_PASS>', neutron_pass)
        
        NOVA_CONF_FILE_PATH = '/etc/nova/nova.conf'
        
        FileUtil.replaceFileContent(NOVA_CONF_FILE_PATH, '#APIsAndDrivers', APIsAndDrivers)
        FileUtil.replaceFileContent(NOVA_CONF_FILE_PATH, '#AccessParameters', AccessParameters)
        
        ##############################
        FileUtil.replaceFileContent(NOVA_CONF_FILE_PATH, 
                                    '#vif_plugging_is_fatal=true', 
                                    'vif_plugging_is_fatal=false')
        FileUtil.replaceFileContent(NOVA_CONF_FILE_PATH, 
                                    '#vif_plugging_timeout=300', 
                                    'vif_plugging_timeout=0')
        pass
    
    @staticmethod
    def finalizeInstallation():
#         ShellCmdExecutor.execCmd('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
        
        ShellCmdExecutor.execCmd('chown -R neutron:neutron /etc/neutron/')
        
        ShellCmdExecutor.execCmd('systemctl restart openstack-nova-compute.service')
        
#         ShellCmdExecutor.execCmd('systemctl enable neutron-openvswitch-agent.service')
        
#         ShellCmdExecutor.execCmd('systemctl restart neutron-openvswitch-agent.service')
        
        ShellCmdExecutor.execCmd('systemctl enable neutron-linuxbridge-agent.service')
        ShellCmdExecutor.execCmd('systemctl start neutron-linuxbridge-agent.service')
        pass
    
    
    
    
        
if __name__ == '__main__':
    print 'hello openstack-newton:confiugre nova-compute after neutron============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    TAG_FILE = '/opt/openstack_conf/tag/install/configureNovaComputeAfterNeutron'
    if os.path.exists(TAG_FILE) :
        print 'After neutron, nova-compute configured####'
        print 'exit===='
        pass
    else :
        NovaCompute.install()
        NovaCompute.confiugureNeutron()
        NovaCompute.configureLinuxBridgeAgent()
#         NovaCompute.configureOVS()
#         NovaCompute.reconfigureNovaCompute()
        NovaCompute.finalizeInstallation()
        
        os.system('touch %s' % TAG_FILE)
        pass
    print 'nova-compute is configured after neutron#######'
    pass

