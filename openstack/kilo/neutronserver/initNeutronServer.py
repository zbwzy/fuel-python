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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.yaml.YAMLUtil import YAMLUtil
from openstack.kilo.ntp.ntp import NTP

from openstack.kilo.neutronserver.neutronserver import NeutronServer

if __name__ == '__main__':
    print 'hello openstack-kilo:neutron-server============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/init_neutronserver'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'neutron-server initted####'
        print 'exit===='
    else :
        if NeutronServer.getServerIndex() == 0 :
            NeutronServer.importNeutronDBSchema()
            time.sleep(2)
            NeutronServer.upgradeLBDBSchema()
            pass
        
        NeutronServer.start()
        time.sleep(2)
        NeutronServer.restart()
        
        #ntp server is the first keystone
        ntpServerIP = YAMLUtil.getIPList('keystone')[0]
        NTP.ntpClient(ntpServerIP)
        #mark: neutron-server is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:neutron-server initted#######'
    pass

