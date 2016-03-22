'''
Created on Mar 17, 2016

@author: zhangbai
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
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from openstack.kilo.ssh.SSH import SSH
from openstack.common.role import Role

class IPTables(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def apply():
        iptable4ComputeTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'iptables', 'iptables.compute')
        iptable4ControllerTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'iptables', 'iptables.controller')
        
        #stop firewalld
        ShellCmdExecutor.execCmd('systemctl stop firewalld.service')
        
        if Role.isNovaComputeRole() :
            ShellCmdExecutor.execCmd('rm -rf /etc/sysconfig/iptables')
            ShellCmdExecutor.execCmd('cp -r %s /etc/sysconfig' % iptable4ComputeTemplatePath)
            ShellCmdExecutor.execCmd('mv /etc/sysconfig/iptables.compute /etc/sysconfig/iptables')
            pass
        else :
            ShellCmdExecutor.execCmd('rm -rf /etc/sysconfig/iptables')
            ShellCmdExecutor.execCmd('cp -r %s /etc/sysconfig' % iptable4ControllerTemplatePath)
            ShellCmdExecutor.execCmd('mv /etc/sysconfig/iptables.controller /etc/sysconfig/iptables')
            pass
        
        ShellCmdExecutor.execCmd('systemctl restart iptables.service')
        pass
    pass

