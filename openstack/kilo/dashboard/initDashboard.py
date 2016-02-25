'''
Created on Sep 29, 2015

@author: zhangbai
'''

'''
Note:
Defaultly,on localhost, dashboard is listened on port 8080.

usage:

python dashboard.py

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
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from openstack.icehouse.dashboard.dashboard import Dashboard
from openstack.icehouse.dashboard.dashboard import DashboardHA
    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:dashboard============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /etc/puppet/localip, these two files are generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/initDashboard'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'dashboard installed####'
        print 'exit===='
        pass
    else :
        Dashboard.start()
    
        DashboardHA.install()
        DashboardHA.configure()
        DashboardHA.start()
        #
        Dashboard.restart()
        DashboardHA.start()
    #     ShellCmdExecutor.execCmd('service haproxy restart')
        #mark: dashboard is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:dashboard installed#######'
    pass

