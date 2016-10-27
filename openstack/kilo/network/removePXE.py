'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python initNetwork.py

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
from openstack.kilo.network.network import Network
    
if __name__ == '__main__':
    print 'hello openstack-kilo:network============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    REMOVE_TAG_FILE = '/opt/openstack_conf/tag/install/remove_pxe'
    if os.path.exists(REMOVE_TAG_FILE) :
        print 'network initted####'
        print 'exit===='
        pass
    else :
        from openstack.kilo.common.net import Net
        pxeInterfaceName = Net.getInterfaceNameByBridge('br-fw-admin')
        exInterfaceName = Net.getInterfaceNameByBridge('br-data')
        
        if pxeInterfaceName in exInterfaceName :
            #remove the pxe bridge from business network interface
            delCmd = 'brctl delif br-fw-admin %s' % pxeInterfaceName
            ShellCmdExecutor.execCmd(delCmd)
            pass
        #mark: network is initted
        
        os.system('touch %s' % REMOVE_TAG_FILE)
    print 'hello network initted#######'
    pass

