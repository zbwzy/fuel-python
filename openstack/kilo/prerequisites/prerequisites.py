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
from common.yaml.YAMLUtil import YAMLUtil
from common.file.FileUtil import FileUtil

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
        
        ###each node's ip-hostname mapping of cluster
        YAMLUtil.setHosts()
        
        ###set bclinux repo url
        from openstack.kilo.common.repo import Repo
        if Repo.useBCLinuxRepo :
            Repo.setBCLinuxRepo()
            pass
        
        ########################
        
        #ntp update
        fuel_master_ip = str(YAMLUtil.getValue('global', 'fuel_master_ip'))
        os.system('/usr/sbin/ntpdate -u %s' % fuel_master_ip)
                
        #install tar
        ShellCmdExecutor.execCmd('yum install tar -y')
        
        #install pexpect
        ShellCmdExecutor.execCmd('cd /etc/puppet/fuel-python/externals/pexpect-3.3; python setup.py install')
        if os.path.exists('/opt/openstack_conf/tag') :
#             ShellCmdExecutor.execCmd('rm -rf /opt/openstack_conf/tag')
            pass
        
        if os.path.exists('/opt/openstack_conf/scripts') :
#             ShellCmdExecutor.execCmd('rm -rf /opt/openstack_conf/scripts')
            pass
        
        ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/tag/')
        
        ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/tag/install')
        
        ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/scripts')
        
        #memcache
        from openstack.kilo.memcached.memcached import Memcached
        Memcached.install()
        Memcached.start()
        
        #######produce params
        print 'produce openstack params========'
        ParamsProducer.produce()
        print 'done to produce openstack params####'
        
        #ssh root user mutual trust
        #depend on openstack_params.json is produced
        print 'do ssh mutual trust====='
        SSH.sshMutualTrust()
        print 'do ssh mutual trust#####'
        
        #iptables
        IPTables.apply()
        ShellCmdExecutor.execCmd('systemctl restart iptables.service')
        
        #keep log on disk
        print 'do keep log on disk======='
        ShellCmdExecutor.execCmd('mkdir -p /var/log/journal')
        ShellCmdExecutor.execCmd('systemctl restart systemd-journald')
        print 'do keep log on disk####'
         
        #sysctl
        print 'do sysctl============='
        if os.path.exists('/etc/sysctl.conf') :
            ShellCmdExecutor.execCmd('rm -rf /etc/sysctl.conf')
            pass
        
        sysctlConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'sysctl', 'sysctl.conf')
        novaComputeSysctlConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'sysctl', 'sysctl.conf.compute')
        controllerSysctlConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'sysctl', 'sysctl.conf.ctl')
        from openstack.common.role import Role
        if Role.isNovaComputeRole4Prerequisites() :
            ShellCmdExecutor.execCmd('cp -r %s /etc/' % novaComputeSysctlConfFileTemplatePath)
            ShellCmdExecutor.execCmd('mv /etc/sysctl.conf.compute /etc/sysctl.conf')
            pass
        else :
            ShellCmdExecutor.execCmd('cp -r %s /etc/' % controllerSysctlConfFileTemplatePath)
            ShellCmdExecutor.execCmd('mv /etc/sysctl.conf.ctl /etc/sysctl.conf')
            pass
        
        ShellCmdExecutor.execCmd('sysctl -p')
        print 'do sysctl####'
        #set os limits
        limits_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'limits', 'limits.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/security/' % limits_file_template_path)
        pass
    pass

if __name__ == '__main__':
    print 'openstack kilo:to do prerequisites============'
    Prerequisites.install()
    print 'openstack kilo: done prerequisites######'
    pass
