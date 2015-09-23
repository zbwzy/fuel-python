'''
Created on Aug 26, 2015

@author: zhangbai
'''
from openstack.icehouse.common.Utils import ShellCmdExecutor

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    pass

class Glance(object):
    '''
    classdocs
    '''
    GLANCE_CONF_FILE_PATH = "/etc/nova/nova.conf"
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Glance node install start========'
        yumCmd = "yum install openstack-nova-compute -y"
        ShellCmdExecutor.execCmd(yumCmd)
        Glance.configConfFile()
        Glance.start()
        
        Glance.configAfterNetworkNodeConfiguration()
        print 'Glance node install done####'
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("glance")
        pass
    
    @staticmethod
    def configConfFile():
        #Use conf file template to replace the IP
        pass
    
    
if __name__ == '__main__':
    print 'hello openstack-icehouse:glance============'
    Glance.install()
    print '#######'
    pass

