'''
Created on Dec 15, 2015

@author: zhangbai
'''

'''
usage:

python initOSTF.py

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

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.icehouse.neutronserver.neutronserver import NeutronServerHA

    
if __name__ == '__main__':
    print 'hello openstack-icehouse:init ostf============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/initOSTFNetwork'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'ostf initted####'
        print 'exit===='
        pass
    else :
        if NeutronServerHA.isMasterNode() :
            network_init_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ostf_network_init.sh')
            ShellCmdExecutor.execCmd('cp -r %s /opt/' % network_init_script_path)
            ############
            keystone_vip = JSONUtility.getValue('keystone_vip')
            FileUtil.replaceFileContent('/opt/ostf_network_init.sh', '<KEYSTONE_VIP>', keystone_vip)
            
            ###########
            ShellCmdExecutor.execCmd('bash /opt/ostf_network_init.sh')
            pass

        #mark: OSTF is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello ostf initted#######'
    pass


