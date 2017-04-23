'''
Created on Mar 10, 2017

@author: zhangbai
'''

import sys
import os

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
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil

class NTP(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def ntpServer():
        ShellCmdExecutor.execCmd('yum install ntp -y')
        
        ntp_config_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ntp', 'ntp.conf.server')
        ShellCmdExecutor.execCmd('cp -r %s /etc/' % ntp_config_file_path)
        ShellCmdExecutor.execCmd('mv /etc/ntp.conf.server /etc/ntp.conf')
        ShellCmdExecutor.execCmd('hwclock --systohc')
        ShellCmdExecutor.execCmd('service ntpd restart')
        pass
    
    @staticmethod
    def ntpClient(ntpServerIP):
        ShellCmdExecutor.execCmd('yum install ntp -y')
        
        ntp_config_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ntp', 'ntp.conf.client')
        ShellCmdExecutor.execCmd('cp -r %s /etc/' % ntp_config_file_path)
        ShellCmdExecutor.execCmd('mv /etc/ntp.conf.client /etc/ntp.conf')
        
        FileUtil.replaceFileContent('/etc/ntp.conf', '<NTP_SERVER_MGMT_IP>', ntpServerIP)
        
        ShellCmdExecutor.execCmd('service ntpd stop')
        ShellCmdExecutor.execCmd('ntpdate -u %s' % ntpServerIP)
        
        ShellCmdExecutor.execCmd('hwclock --systohc')
        ShellCmdExecutor.execCmd('service ntpd restart')
        pass
    
    
if __name__ == '__main__':
    print 'start to test ntp=========='
    #TEST CODE
    NTP.ntpServer()
    print 'done to test ntp######'
    pass

