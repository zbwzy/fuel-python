'''
Created on Feb 29, 2016

@author: zhangbai
'''

'''
usage:

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

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor

class Patch(object):
    '''
    classdocs
    '''
    TIMEOUT = 600 #unit:second
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def patchOsloDbApi():
        osloDbApiTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'patch', 'oslo-db', 'api.py')
        if os.path.exists('/usr/lib/python2.7/site-packages/oslo_db/api.py') :
            ShellCmdExecutor.execCmd("rm -rf /usr/lib/python2.7/site-packages/oslo_db/api.py")
            
            ShellCmdExecutor.execCmd("cp -r %s %s" % (osloDbApiTemplateFilePath, '/usr/lib/python2.7/site-packages/oslo_db/'))
            pass
        pass
    
    

if __name__ == '__main__':
    pass



