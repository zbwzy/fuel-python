'''
Created on Feb 26, 2016

@author: zhangbai
'''

import sys
import os
import time

debug = True
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
from openstack.common.role import Role

class ServerSequence(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def getIndex(management_ip_list, management_ip):
        management_ip = management_ip.strip()
        print 'management_ip=%s---------------------' % management_ip
        index = management_ip_list.index(management_ip)
        print 'index=%s-----------' % index
        return index
    
    
if __name__ == '__main__':
    management_ip_list = ['10.20.0.84', '10.20.0.85', '10.20.0.86']
    management_ip = '10.20.0.84'
    index = ServerSequence.getIndex(management_ip_list, management_ip)
    print 'index=%s' % index
    if index == 0 :
        print 'This server is master.'
        pass
    
    management_ip = '10.20.0.86'
    index = ServerSequence.getIndex(management_ip_list, management_ip)
    print 'index=%s' % index
    if index == 2 :
        print 'The server index is %d.' % index
    pass


