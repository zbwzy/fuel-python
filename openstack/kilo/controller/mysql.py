'''
Created on Aug 25, 2015

@author: zhangbai
'''

PROJECT_DEPLOYMENT_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel'
import time
import sys
import os

sys.path.append(PROJECT_DEPLOYMENT_DIR)

from openstack.icehouse.common.Utils import ShellCmdExecutor
from openstack.icehouse.common.Prerequisites import Prerequisites
 

class MySQL(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    MYSQL_CONF_FILE_PATH = "/etc/my.cnf"
    USERNAME = "root"
    INIT_PASSWORD = "123456"
    MARK = "/var/log/openstack/mysql"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def mark():
        ShellCmdExecutor.execCmd("mkdir -p /var/log/openstack/")
        ShellCmdExecutor.execCmd("touch /var/log/openstack/mysql")
    
    @staticmethod
    def initMySQL(user, initPasswd):
        #when mysql is installed,config file and the root password is None, init the db.
        MySQL.configMyConfFile()
        
        #start
        startCmd = "service mysql start"
        ShellCmdExecutor.execCmd(startCmd)
        
        #chkcofnig
        chkconfigCmd = "chkconfig mysql on"
        ShellCmdExecutor.execCmd(chkconfigCmd)
        
        initPasswdCmd = 'mysqladmin -u%s password %s' % (user, initPasswd)
        ShellCmdExecutor.execCmd(initPasswdCmd)
        pass
    
    @staticmethod
    def configMyConfFile():
        print 'start to config my.conf file====='
        curDir = os.getcwd()
        print "curDir=%s" % curDir
        curFileName = os.path.basename(curDir)
        mysqlConfDir = os.path.join(curDir.rstrip(curFileName), 'configfile.template', 'controller')
        mysqlConfFilePath = os.path.join(mysqlConfDir, 'my.cnf')
        print 'mysqlConfFilePath=%s' % mysqlConfFilePath
        cpMyCnfCmd = "sudo cp -rf %s /etc/" % mysqlConfFilePath
        ShellCmdExecutor.execCmd(cpMyCnfCmd)
        print 'config done####'
        pass
    
    @staticmethod
    def install():
        print 'MySQL.install start====='
        yumCmd = 'yum install mysql mysql-server MySQL-python -y'
        ShellCmdExecutor.execCmd(yumCmd)
        
        MySQL.initMySQL(MySQL.USERNAME, MySQL.INIT_PASSWORD)
        
        #mark
        MySQL.mark()
        print 'MySQL.install done====='
        pass
    
    @staticmethod
    def setPassword(user, oldpasswd, newpasswd):
        cmd = 'mysqladmin -u%s -p%s password %s' % (user, oldpasswd, newpasswd)
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        print "output=%s--" % output
        pass
    
    @staticmethod
    def createDb(user, passwd, db_name):
        listDbCmd = 'mysql -u%s -p%s -e "show databases" | grep %s' % (user, passwd, db_name)
        output, exitcde = ShellCmdExecutor.execCmd(listDbCmd)
        if (db_name not in output) or output == '' or output == None :
            createDbCmd = 'mysql -u%s -p%s -e "create database %s"' % (user, passwd, db_name)
            output, exitcode = ShellCmdExecutor.execCmd(createDbCmd)
            print "output=%s--" % output
        else :
            print "The DB:%s already exists!" % db_name
            pass
        pass
    
    #set password for 'root'@'localhost'=password('newpasswd')
    @staticmethod
    def execMySQLCmd(user, passwd, cmds):
        cmd = 'mysql -u%s -p%s -e "%s"' % (user, passwd, cmds)
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        print 'output=%s--' % output
        pass
    

if __name__ == '__main__':
    print 'openstack-icehouse:mysql install============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path> LOCAL_IP
    argv = sys.argv
    argv.pop(0)
    if len(argv) > 0 :
        LOCAL_IP = argv[0]
        pass
    else :
        print "ERROR:no params."
        pass
    
    Prerequisites.install(LOCAL_IP, "controller")
    MySQL.install()
    print 'end time: %s' % time.ctime()
    print 'openstack-icehouse:mysql done#####'
    




