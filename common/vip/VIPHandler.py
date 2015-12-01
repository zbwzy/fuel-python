'''
Created on Nov 30, 2015

@author: zhangbai
'''
# coding=UTF-8  
import sys
import os
import time
import string

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
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

import yaml

class VIPHandler(object):
    '''
    classdocs
    '''
    ASTUTE_YAML_FILE_PATH = '/etc/astute.yaml'
    OPENSTACK_ROLES = ['mysql', 'rabbitmq', 'keystone', 'glance', 'nova-api', 'nova-compute', 'neutron-server', 'neutron', 'cinder', 'cinder-storage', 'ceilometer', 'heat']
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    
if __name__ == "__main__":
    print 'test delete vip========================'
    pass

    
    
        
        
    