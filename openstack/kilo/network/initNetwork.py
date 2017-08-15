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

from openstack.kilo.network.network import Network
    
if __name__ == '__main__':
    print 'hello openstack-kilo:network============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/init_network'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'network initted####'
        print 'exit===='
        pass
    else :
        Network.finalizeInstallation()
        #mark: network is initted
        #open limits of file & restart always
        if not Network.isNeutronServerNode() :
            from common.openfile.OpenFile import OpenFile
            OpenFile.execModification('/usr/lib/systemd/system', 'openstack-')
            OpenFile.execModificationBy('/usr/lib/systemd/system', 'neutron-dhcp-agent.service')
            pass
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello network initted#######'
    pass

