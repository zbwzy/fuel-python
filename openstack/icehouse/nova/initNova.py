'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python initNova.py

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

from openstack.icehouse.nova.nova import Nova
from openstack.icehouse.nova.nova import NovaHA
    
if __name__ == '__main__':
    print 'hello openstack-icehouse:nova-api============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/initNovaApi'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-api initted####'
        print 'exit===='
        pass
    else :
        #Nova DB Schema
        if NovaHA.isMasterNode() :
            dbSchema_init_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'nova_dbschema_init.sh')
            ShellCmdExecutor.execCmd('cp -r %s /opt/' % dbSchema_init_script_path)
            ShellCmdExecutor.execCmd('bash /opt/nova_dbschema_init.sh')
            pass

        Nova.start()
        
        ## Nova HA
        NovaHA.install()
        NovaHA.configure()
        NovaHA.start()
        #
        
        Nova.restart()
        NovaHA.start()

        #mark: nova-api is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello nova-api initted#######'
    pass

