'''
Created on Oct 24, 2015

@author: zhangbai
'''

'''
usage:

python initDB.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time

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
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql','keystone.conf')

SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-api.conf')
SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-registry.conf')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil


class MySQL(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    MYSQL_CONF_FILE_PATH = "/etc/my.cnf"
    USERNAME = "root"
    INIT_PASSWORD = "123456"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
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
        
        pass
    
    @staticmethod
    def initPassword(user, old_password, new_password):
        initPasswdCmd = 'mysqladmin -u%s -p%s password %s' % (user, old_password, new_password)
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
        cpMyCnfCmd = "sudo cp -r %s /etc/" % mysqlConfFilePath
        ShellCmdExecutor.execCmd(cpMyCnfCmd)
        print 'config done####'
        pass
    
    @staticmethod
    def install():
        print 'MySQL.install start====='
        yumCmd = 'yum install mysql mysql-server MySQL-python -y'
        ShellCmdExecutor.execCmd(yumCmd)
        
        MySQL.initMySQL(MySQL.USERNAME, MySQL.INIT_PASSWORD)
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
        myqlCmd = 'mysql -u%s -p%s -e "%s"' % (user, passwd, cmds)
        output, exitcode = ShellCmdExecutor.execCmd(myqlCmd)
        print 'output=%s--' % output
        pass
    
    @staticmethod
    def init():
        INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/db_init'
        
        if os.path.exists(INSTALL_TAG_FILE) :
            print 'openstack db is initted####'
            print 'exit===='
            pass
        else :
            print 'start to init======='
            
    #         Prerequisites.prepare()
            
            #init mysql password
            user = 'root'
            initPasswd = JSONUtility.getValue('mysql_password')
            oldPasswd = 'bcrdb'
            print 'initPasswd=%s--' % initPasswd
            MySQL.initPassword(user, oldPasswd, initPasswd)
            
            
            flushCmd = 'flush privileges;'
            output, exitcode = ShellCmdExecutor.execCmd('hostname')
            hostname = output.strip()
            print 'init============================================'
            if YAMLUtil.hasRoleInNodes('haproxy-keepalived') :
                grantHaproxyUserUsage = 'grant usage on *.* to haproxy@\'%\''
                MySQL.execMySQLCmd(user, initPasswd, grantHaproxyUserUsage)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                pass
            
            #keystone
            if YAMLUtil.hasRoleInNodes('keystone') :
                createDBCmd = 'CREATE DATABASE keystone'
                MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                keystone_dbpass = JSONUtility.getValue('keystone_dbpass')
                grantCmd1 = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=keystone_dbpass)
                print 'grantCmd1=%s--' % grantCmd1
                grantCmd2 = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=keystone_dbpass)
                print 'grantCmd2=%s--' % grantCmd2
                
    #             grantToHostname = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
    #             .format(hostname=hostname,init_passwd=initPasswd)
                
                MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
                MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
    #             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
    #             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                #add default role with specific id
                print 'add default role with specific id============'
    #             addDefaultRoleCmd = 'insert into role(id,name,extra) values(\'9fe2ff9ee4384b1894a90878d3e92bab\',\'__member__\',\'\{\}\')'
    #             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
    #             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                print 'add default role with specific id########'
                
            ########
    #             Keystone.install()
    #             ########
    #             Keystone.configConfFile()
    #              
    #             Keystone.importKeystoneDBSchema()
    #             #######
    #             Keystone.supportPKIToken()
    #                      
    #             Keystone.start()
    #             
    #             ####NEW
    #             Keystone.configureEnvVar()
    #             Keystone.sourceAdminOpenRC()####NEW
    #             Keystone.initKeystone()
    #             Keystone.sourceAdminOpenRC()
            
            #glance
            if YAMLUtil.hasRoleInNodes('glance') :
                print 'create glance mysql user============'
                createDBCmd = 'CREATE DATABASE glance'
                MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                glance_dbpass= JSONUtility.getValue('glance_dbpass')
                grantCmd1 = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=glance_dbpass)
                
                grantCmd2 = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=glance_dbpass)
                
    #             grantToHostname = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
    #             .format(hostname=hostname,init_passwd=initPasswd)
                
                MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
                MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
    #             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
    #             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            #nova
            if YAMLUtil.hasRoleInNodes('nova-api') :
                createDBCmd = 'CREATE DATABASE nova'
                MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                nova_dbpass= JSONUtility.getValue('nova_dbpass')
                grantCmd1 = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=nova_dbpass)
                
                grantCmd2 = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=nova_dbpass)
                
    #             grantToHostname = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
    #             .format(hostname=hostname,init_passwd=initPasswd)
                
                MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
                MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
    #             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
    #             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
    #             Nova.install()
    #             ShellCmdExecutor.execCmd('chmod 777 /etc/nova')
    #             Nova.configConfFile()
    #             
    #             Keystone.sourceAdminOpenRC()
    #             Nova.initNova()
            
            #neutron
            if YAMLUtil.hasRoleInNodes('neutron-server') :
                createDBCmd = 'CREATE DATABASE neutron'
                MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                neutron_dbpass= JSONUtility.getValue('neutron_dbpass')
                grantCmd1 = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=neutron_dbpass)
                
                grantCmd2 = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=neutron_dbpass)
                
    #             grantToHostname = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
    #             .format(hostname=hostname,init_passwd=initPasswd)
                
                MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            #cinder
            if YAMLUtil.hasRoleInNodes('cinder-api') :
                createDBCmd = 'CREATE DATABASE cinder'
                MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                cinder_dbpass= JSONUtility.getValue('cinder_dbpass')
                grantCmd1 = 'GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=cinder_dbpass)
                
                grantCmd2 = 'GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=cinder_dbpass)
                
    #             grantToHostname = 'GRANT ALL PRIVILEGES ON keystone.* TO \'cinder\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
    #             .format(hostname=hostname,init_passwd=initPasswd)
                
                MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
                MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
    #             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
    #             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
    #             ####Special handling
    #             if os.path.isfile('/etc/cinder') :
    #                 ShellCmdExecutor.execCmd("rm -rf /etc/cinder")
    #                 pass
                pass
            
            #ceilometer
            if YAMLUtil.hasRoleInNodes('ceilometer') :
    #             Ceilometer.initCeilometer()
                pass
                
            #heat
            if YAMLUtil.hasRoleInNodes('heat') :
                createDBCmd = 'CREATE DATABASE heat'
                MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
                heat_dbpass= JSONUtility.getValue('heat_dbpass')
                grantCmd1 = 'GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=heat_dbpass)
                
                grantCmd2 = 'GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
                .format(init_passwd=heat_dbpass)
                
    #             grantToHostname = 'GRANT ALL PRIVILEGES ON keystone.* TO \'heat\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
    #             .format(hostname=hostname,init_passwd=initPasswd)
                
                MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
                MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
    #             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
    #             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
            #mark: db is initted
            os.system('touch %s' % INSTALL_TAG_FILE)
            print 'hello openstack is initted#######'

    
if __name__ == '__main__':
    print 'hello openstack-kilo:initDB============'
    
    print 'start time: %s' % time.ctime()
    if debug :
        print 'debug====================='
        print 'debug#########'
        exit()
        pass
    
    MySQL.init()
    
#     output, exitcode = ShellCmdExecutor.execCmd('cat /opt/mysql_ip_list')
#     mysql_ip_list = output.strip().split(',')
#     mysql_master_ip = mysql_ip_list[0]
#     
#     output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
#     localIP = output.strip()
#     
#     if not localIP == mysql_master_ip :
#         print 'This is not master mysql node,skip db init.............'
#         pass
#     else :
#         MySQL.init()
#         pass
#     pass
    
    

