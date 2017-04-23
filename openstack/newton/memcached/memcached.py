'''
Created on Feb 26, 2016

@author: zhangbai
'''

'''
usage:

python memcached.py

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

OPENSTACK_VERSION_TAG = 'newton'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor

class Memcached(object):
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
        cmd = 'yum install memcached -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd('systemctl enable memcached')
        ShellCmdExecutor.execCmd('systemctl start memcached')
        pass
    pass



if __name__ == '__main__':
        
    print 'hello openstack-newton:memcached======='
    Memcached.install()
    Memcached.start()
    
    print 'hello openstack-newton:memcached installed#######'
    pass

