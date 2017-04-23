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

OPENSTACK_VERSION_TAG = 'newton'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)

from openstack.newton.dashboard.dashboard import Dashboard
    
if __name__ == '__main__':
    
    print 'hello openstack-newton:dashboard============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    RESTART_TAG_FILE = '/opt/openstack_conf/tag/install/restart_dashboard'
    if os.path.exists(RESTART_TAG_FILE) :
        print 'dashboard restarted####'
        print 'exit===='
        pass
    else :
#         Dashboard.configureDashboardRights()
        Dashboard.restart()
    #     ShellCmdExecutor.execCmd('service haproxy restart')
        #mark: dashboard is installed
        os.system('touch %s' % RESTART_TAG_FILE)
    print 'hello openstack-kilo:dashboard restarted#######'
    pass

