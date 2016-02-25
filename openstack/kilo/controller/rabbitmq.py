'''
Created on Aug 25, 2015

@author: zhangbai
'''

PROJECT_DEPLOYMENT_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel'
import time
import sys

sys.path.append(PROJECT_DEPLOYMENT_DIR)

from openstack.icehouse.common.Utils import ShellCmdExecutor
 
    
class RabbitMQ(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    INIT_USER_NAME = "guest"
    INIT_PASSWORD = "123456"
    MARK = "/var/log/openstack/rabbitmq"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def mark():
        ShellCmdExecutor.execCmd("mkdir -p /var/log/openstack/")
        ShellCmdExecutor.execCmd("touch /var/log/openstack/rabbitmq")
        pass
    
    @staticmethod
    def install():
        print 'RabbitMQ.install start====='
        yumCmd = "yum install -y rabbitmq-server.noarch"
        ShellCmdExecutor.execCmd(yumCmd)
        
        RabbitMQ.initRabbitMQ(RabbitMQ.INIT_USER_NAME, RabbitMQ.INIT_PASSWORD)
        #Mark
        RabbitMQ.mark()
        print 'RabbitMQ.install done####'
        pass
    
    @staticmethod
    def initRabbitMQ(username, password):
        startCmd = "/etc/init.d/rabbitmq-server restart"
        ShellCmdExecutor.execCmd(startCmd)
        
        chkconfigCmd = "chkconfig rabbitmq-server on"
        ShellCmdExecutor.execCmd(chkconfigCmd)
        
        initPasswordCmd = "rabbitmqctl change_password %s %s" % (username, password)
        ShellCmdExecutor.execCmd(initPasswordCmd)
        pass
    pass


if __name__ == '__main__':
    print 'openstack-icehouse:rabbitmq install============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    
    RabbitMQ.install()
    
    print 'end time: %s' % time.ctime()
    print 'openstack-icehouse:rabbitmq done#####'
    




