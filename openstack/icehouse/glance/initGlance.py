'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python glance.py

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
SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-api.conf')
SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-registry.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.icehouse.glance.glance import Glance
from openstack.icehouse.glance.glance import GlanceHA

    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:glance============'
    
    print 'start time: %s' % time.ctime()
    
    INSTALL_TAG_FILE = '/opt/initGlance'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'glance installed####'
        print 'exit===='
        exit()
        pass
        
    print 'start to install======='
    
    #
    Glance.sourceAdminOpenRC()
    
    Glance.start()
    #add HA
    GlanceHA.install()
    GlanceHA.configure()
    GlanceHA.start()
    
    Glance.restart()
    GlanceHA.restart
    
#     os.system("service openstack-glance-api restart")
#     os.system("service openstack-glance-registry restart")
#     
#     os.system("service haproxy restart")
    #mark: glance is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    
    print 'hello openstack-icehouse:glance#######'
    pass

