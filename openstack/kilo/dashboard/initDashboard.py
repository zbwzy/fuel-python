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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)

from openstack.kilo.dashboard.dashboard import Dashboard
from common.yaml.YAMLUtil import YAMLUtil
from openstack.kilo.ntp.ntp import NTP
    
if __name__ == '__main__':
    
    print 'hello openstack-kilo:dashboard============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/init_dashboard'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'dashboard installed####'
        print 'exit===='
        pass
    else :
        Dashboard.start()
        #mark: dashboard is started
        
        #ntp server is the first keystone
        ntpServerIP = YAMLUtil.getIPList('keystone')[0]
        NTP.ntpClient(ntpServerIP)
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:dashboard installed#######'
    pass

