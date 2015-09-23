'''
Created on Sep 10, 2015

@author: zhangbai
'''
from openstack.icehouse.common.Utils import ShellCmdExecutor

class Prerequisites(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install(localip, domain):
        print 'Prerequisites.install start===='
        Network.Prepare(localip, domain)
        print 'Prerequisites.install done####'
        pass
    
class Network(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def Prepare(localip, domain):
        Network.stopIPTables()
        Network.stopNetworkManager()
        Network.configToEtcHosts(localip, domain)
        
        pass
    
    @staticmethod
    def stopNetworkManager():
        stopCmd = "service NetworkManager stop"
        chkconfigOffCmd = "chkconfig NetworkManager off"
        
        ShellCmdExecutor.execCmd(stopCmd)
        ShellCmdExecutor.execCmd(chkconfigOffCmd)
        pass
    
    @staticmethod
    def stopIPTables():
        stopCmd = "service iptables stop"
        ShellCmdExecutor.execCmd(stopCmd)
        pass
    
    @staticmethod
    def configToEtcHosts(ip, domain):
        output, exitcode = ShellCmdExecutor.execCmd("cat /etc/hosts")
        if domain not in output :
            ShellCmdExecutor.execCmd("sudo echo '%s  %s' >> /etc/hosts" % (ip, domain))
            pass
        pass

    