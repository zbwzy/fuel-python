'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python glance.py <LOCAL_IP> <MYSQL_VIP> <RABBIT_HOST> <KEYSTONE_VIP> 
'''

from common.shell.ShellCmdExecutor import ShellCmdExecutor

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
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Glance node install start========'
        yumCmd = "yum install telnet -y"
        output, exitcode = ShellCmdExecutor.execCmd("ls -lt")
        print 'output=\n%s--' % output
        Glance.configConfFile()
        Glance.start()
        
        print 'Glance node install done####'
        pass
    
    @staticmethod
    def start():
        print "start glance========="
        
        print "start glance done####"
#         ShellCmdExecutor.execCmd("glance")
        pass
    
    @staticmethod
    def configConfFile():
        print "configure glance conf file======"
        #Use conf file template to replace the IP
        pass
    
    
if __name__ == '__main__':
    print 'hello openstack-icehouse:glance============'
    Glance.install()
    print 'hello openstack-icehouse:glance#######'
    pass

