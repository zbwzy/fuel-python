'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python initSecgroupRules.py

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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil

    
if __name__ == '__main__':
    print 'hello openstack-kilo:configure default secgroup rules============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    TAG_FILE = '/opt/openstack_conf/tag/install/init_secgroup'
    if os.path.exists(TAG_FILE) :
        print 'Default secgroup rules configured####'
        print 'exit===='
        pass
    else :
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        admin_token = JSONUtility.getValue('admin_token')
        
        initTemplateScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'initDefaultSecgroupRules.sh')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts/' % initTemplateScriptPath)
        
        initScriptPath = '/opt/openstack_conf/scripts/initDefaultSecgroupRules.sh'
        FileUtil.replaceFileContent(initScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initScriptPath, '<ADMIN_TOKEN>', admin_token)
        #######
        
        from openstack.common.serverSequence import ServerSequence
        nova_params_dict = JSONUtility.getRoleParamsDict('nova-api')
        nova_ip_list = nova_params_dict["mgmt_ips"]
        localIP = YAMLUtil.getManagementIP() 
        if ServerSequence.getIndex(nova_ip_list, localIP) == 0:
            ShellCmdExecutor.execCmd('bash %s' % initScriptPath)
            pass
        
        os.system('touch %s' % TAG_FILE)
        pass
    print 'Default secgroup rules are configured#######'
    pass

