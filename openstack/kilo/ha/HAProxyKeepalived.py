'''
Created on Mar 11, 2016

@author: zhangbai
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
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil
from openstack.common.serverSequence import ServerSequence

class HAProxyKeepalived(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        ShellCmdExecutor.execCmd('yum install keepalived ipvsadm haproxy -y')
        pass
    
    @staticmethod
    def configKeepalived():
        pass
    
    @staticmethod
    def configHaproxy():
        pass
    
    @staticmethod
    def start():
        pass
    
    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:haproxy-keepalived============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/ha_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        pass
    else :
        pass
    print 'hello openstack-icehouse:haproxy-keepalived########'
    
    
    