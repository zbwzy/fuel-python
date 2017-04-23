'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python keystone.py

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

OPENSTACK_VERSION_TAG = 'newton'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.newton.keystone.keystone import Keystone


if __name__ == '__main__':
    
    print 'hello openstack-newton:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/check_keystone'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'keystone initted####'
        print 'exit===='
    else :
        from openstack.kilo.keystone.keystone import Keystone
        if Keystone.getServerIndex() == 0 :
            get_keystone_service_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'getKeystoneServiceID.sh')
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % get_keystone_service_script_path)
            ############
            vipParamsDict = JSONUtility.getValue('vip')
            keystone_vip = vipParamsDict["keystone_vip"]
            admin_token = JSONUtility.getValue('admin_token')
            keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
            
            scriptPath = '/opt/openstack_conf/scripts/getKeystoneServiceID.sh'
            ShellCmdExecutor.execCmd('chmod 777 %s' % scriptPath)
            FileUtil.replaceFileContent(scriptPath, '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent(scriptPath, '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent(scriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            
            delete_keystone_service_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'deleteKeystoneServiceID.sh')
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % delete_keystone_service_script_path)
            scriptPath1 = '/opt/openstack_conf/scripts/deleteKeystoneServiceID.sh'
            
            ShellCmdExecutor.execCmd('chmod 777 %s' % scriptPath1)
            FileUtil.replaceFileContent(scriptPath1, '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent(scriptPath1, '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent(scriptPath1, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
             
            ###########
            output, exitcode = ShellCmdExecutor.execCmd('bash %s' % scriptPath)
            keystoneServiceIDs = output.strip()
            if keystoneServiceIDs == '' or keystoneServiceIDs == None :
                pass
            else :
                keystoneServiceIDList = keystoneServiceIDs.split('\n')
                if len(keystoneServiceIDList) > 1 :
                    print 'delete keystone service=========================================='
                    for id in keystoneServiceIDList[1:] :
                        output, exitcode = ShellCmdExecutor.execCmd('bash %s %s' % (scriptPath1, id))
                        pass
                    pass
                pass
            #####################################
            ##add keystone endpoint if not exist
            getKeystoneEndpointTemplateScript = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'getKeystoneEndpoint.sh')
            createKeystoneEndpointTemplateScript = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'createKeystoneEndpoint.sh')
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % getKeystoneEndpointTemplateScript)
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % createKeystoneEndpointTemplateScript)
            
            getKeystoneEndpointScript = '/opt/openstack_conf/scripts/getKeystoneEndpoint.sh'
            createKeystoneEndpointScript = '/opt/openstack_conf/scripts/createKeystoneEndpoint.sh'
            
            ShellCmdExecutor.execCmd('chmod 777 %s' % getKeystoneEndpointScript)
            FileUtil.replaceFileContent(getKeystoneEndpointScript, '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent(getKeystoneEndpointScript, '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent(getKeystoneEndpointScript, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            
            ShellCmdExecutor.execCmd('chmod 777 %s' % createKeystoneEndpointScript)
            FileUtil.replaceFileContent(createKeystoneEndpointScript, '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent(createKeystoneEndpointScript, '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent(createKeystoneEndpointScript, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            
            output, exitcode = ShellCmdExecutor.execCmd('bash %s' % getKeystoneEndpointScript)
            if output.strip() == '' or output.strip() == None :
                #add keystone endpoint
                print 'add keystone endpoint======================='
                output, exitcode = ShellCmdExecutor.execCmd('bash %s' % createKeystoneEndpointScript)
                print 'output=\n%s' % output
                pass
            pass
            
            
        else :
            pass
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-newton:keystone#######'
    pass

