'''
Created on May 30, 2017

@author: zhangbai
'''
import sys
import os
import time

#DEBUG
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
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class NTPService(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    
    @staticmethod
    def setNTPServer():
        ShellCmdExecutor.execCmd('yum install -y ntp')
        ntp_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ntp', 'ntp.conf.server')
        if os.path.exists('/etc/ntp.conf') :
            ShellCmdExecutor.execCmd('rm -rf /etc/ntp.conf')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /etc' % ntp_template_file_path)
        ShellCmdExecutor.execCmd('mv /etc/ntp.conf.server /etc/ntp.conf')
        ShellCmdExecutor.execCmd('hwclock --systohc')
        ShellCmdExecutor.execCmd('service ntpd restart')
        pass
    
    @staticmethod
    def setNTPClient(ntp_server_ip):
        ShellCmdExecutor.execCmd('yum install -y ntp')
        ntp_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ntp', 'ntp.conf.client')
        if os.path.exists('/etc/ntp.conf') :
            ShellCmdExecutor.execCmd('rm -rf /etc/ntp.conf')
            pass
        ShellCmdExecutor.execCmd('cp -r %s /etc' % ntp_template_file_path)
        FileUtil.replaceFileContent('/etc/ntp.conf.client', '<NTP_SERVER_IP>', ntp_server_ip)
        ShellCmdExecutor.execCmd('mv /etc/ntp.conf.client /etc/ntp.conf')
        ShellCmdExecutor.execCmd('service ntpd stop')
        update_cmd = 'ntpdate -u %s' % ntp_server_ip
        output, exitcode = ShellCmdExecutor.execCmd(update_cmd)
        print 'setNTPClient.output=%s--' % output
        ShellCmdExecutor.execCmd('hwclock --systohc')
        ShellCmdExecutor.execCmd('service ntpd restart')
        pass
        