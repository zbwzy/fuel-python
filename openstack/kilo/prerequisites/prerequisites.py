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
from common.yaml.ParamsProducer import ParamsProducer
from openstack.kilo.iptables.iptables import IPTables


class Prerequisites(object):
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
        #######prerequisites
        ###do bond: refactor later
        
        #########################
        
        ###bind bclinux repo url
        
        ########################
        
        ShellCmdExecutor.execCmd('yum clean all && yum makecache')
        
        ShellCmdExecutor.execCmd('yum install tar -y')
        
        #memcache
        from openstack.kilo.memcached.memcached import Memcached
        Memcached.install()
        Memcached.start()
        
        #ssh root user mutual trust
        print 'do ssh mutual trust====='
        SSH.sshMutualTrust()
        print 'do ssh mutual trust#####'
        #iptables
        IPTables.apply()
        
        #keep log on disk
        print 'do keep log on disk======='
        ShellCmdExecutor.execCmd('mkdir -p /var/log/journal')
        ShellCmdExecutor.execCmd('systemctl restart systemd-journald')
        print 'do keep log on disk####'
        
        #sysctl
        print 'do sysctl============='
        sysctlConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'sysctl', 'sysctl.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/' % sysctlConfFileTemplatePath)
        ShellCmdExecutor.execCmd('sysctl -p')
        print 'do sysctl####'
        
        #######produce params
        print 'produce openstack params========'
        ParamsProducer.produce()
        print 'done to produce openstack params####'
        pass
    pass

if __name__ == '__main__':
    pass