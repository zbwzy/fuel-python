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
    def initMariaDB():
        try:
            import pexpect
            
            mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
        
            mysql_root_password = mysql_params_dict["mysql_password"]
    
            child = pexpect.spawn('mysql_secure_installation')
    
            child.expect('Enter current password for root.*')
            child.sendline('')
#             child.sendline('')
    
            child.expect('Set root password.*')
#             child.expect('Change the root password.*')
            child.sendline('Y')
            
            child.expect('New password:')
            child.sendline(mysql_root_password)
            
            child.expect('Re-enter new password:')
            child.sendline(mysql_root_password)
            
            child.expect('Remove anonymous users.*')
            child.sendline('n')
            
            child.expect('Disallow root login remotely.*')
            child.sendline('n')
            
            child.expect('Remove test database and access to it.*')
            child.sendline('n')
            
            child.expect('Reload privilege tables now.*')
            child.sendline('n')
            
            while True :
                regex = "[\\s\\S]*"
                index = child.expect([regex , pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:
                    break
                elif index == 1:
                    pass   #continue to wait
                elif index == 2:
                    pass    #continue to wait
    
            child.sendline('exit')
            child.sendcontrol('c')
            child.interact()
        except OSError:
            print 'Catch exception %s when init mariadb.' % OSError.strerror
            sys.exit(0)
            pass
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
        return (output,exitcode)
    
    
    @staticmethod
    def dropDb(user, passwd, database_name):
        myqlCmd = 'mysql -u%s -p%s -e "%s"' % (user, passwd, 'drop database %s;' % database_name)
        output, exitcode = ShellCmdExecutor.execCmd(myqlCmd)
#         print 'output=%s--' % output
        return (output,exitcode)
    
    @staticmethod
    def showTables(user, passwd, database_name):
        myqlCmd = 'mysql -u%s -p%s -e "%s"' % (user, passwd, 'select table_name from information_schema.tables where table_schema=\'%s\' and table_type=\'base table\';' % database_name)
        output, exitcode = ShellCmdExecutor.execCmd(myqlCmd)
#         print 'output=%s--' % output
        return (output,exitcode)
    
    @staticmethod
    def deleteAllTables(user, passwd, database_name):
        myqlCmd = 'mysql -u%s -p%s -e "%s"' % (user, passwd, 'delete * from %s;' % database_name)
        output, exitcode = ShellCmdExecutor.execCmd(myqlCmd)
#         print 'output=%s--' % output
        return (output,exitcode)
    
    @staticmethod
    def checkKeystoneDB(user, passwd):
        output, exitcode = MySQL.showTables(user, passwd, 'keystone')
        
        if exitcode != 0 :
            print 'checkDB.keystone.exitcode=%s' % str(exitcode)
            return False
        
        if output == None or output == '' :
            print 'checkDB.keystone.output is None.'
            return False
        
        tableNamesList = output.strip().split('\n')
        print 'checkDB.keystone.len=%s' % len(tableNamesList)
        if len(tableNamesList) >= 32 :
            return True
        else:
            return False
        pass
    
    @staticmethod
    def checkGlanceDB(user, passwd):
        output, exitcode = MySQL.showTables(user, passwd, 'glance')
        
        if exitcode != 0 :
            print 'checkDB.glance.exitcode=%s' % str(exitcode)
            return False
        
        if output == None or output == '' :
            print 'checkDB.glance.output is None.'
            return False
        
        tableNamesList = output.strip().split('\n')
        print 'checkDB.glance.len=%s' % len(tableNamesList)
        if len(tableNamesList) >= 20 :
            return True
        else:
            return False
        pass
    
    @staticmethod
    def checkNovaDB(user, passwd):
        output, exitcode = MySQL.showTables(user, passwd, 'nova')
        
        if exitcode != 0 :
            print 'checkDB.nova.exitcode=%s' % str(exitcode)
            return False
        
        if output == None or output == '' :
            print 'checkDB.nova.output is None.'
            return False
        
        tableNamesList = output.strip().split('\n')
        print 'checkDB.nova.len=%s' % len(tableNamesList)
        if len(tableNamesList) >= 108 :
            return True
        else:
            return False
        pass
    
    @staticmethod
    def checkCinderDB(user, passwd):
        output, exitcode = MySQL.showTables(user, passwd, 'cinder')
        
        if exitcode != 0 :
            print 'checkDB.cinder.exitcode=%s' % str(exitcode)
            return False
        
        if output == None or output == '' :
            print 'checkDB.cinder.output is None.'
            return False
        
        tableNamesList = output.strip().split('\n')
        print 'checkDB.cinder.len=%s' % len(tableNamesList)
        if len(tableNamesList) >= 24 :
            return True
        else:
            return False
        pass
    
    @staticmethod
    def checkNeutronDB(user, passwd):
        output, exitcode = MySQL.showTables(user, passwd, 'neutron')
        
        if exitcode != 0 :
            print 'checkDB.neutron.exitcode=%s' % str(exitcode)
            return False
        
        if output == None or output == '' :
            print 'checkDB.neutron.output is None.'
            return False
        
        tableNamesList = output.strip().split('\n')
        print 'checkDB.neutron.len=%s' % len(tableNamesList)
        if len(tableNamesList) >= 150 :
            return True
        else:
            return False
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
            
            mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
            initPasswd = mysql_params_dict['mysql_password']
            initPasswd = '123456'
            oldPasswd = 'bcrdb'
            print 'initPasswd=%s--' % initPasswd
            MySQL.initPassword(user, oldPasswd, initPasswd)
            
            
            flushCmd = 'flush privileges;'
            output, exitcode = ShellCmdExecutor.execCmd('hostname')
            hostname = output.strip()
            print 'init============================================'
            if YAMLUtil.hasRoleInNodes('haproxy-keepalived') :
                createHaproxyUserCmd = 'use mysql;CREATE USER \'haproxy\'@\'%\';update user set plugin=\'mysql_native_password\' where user=\'haproxy\';'
                MySQL.execMySQLCmd(user, initPasswd, createHaproxyUserCmd)
                MySQL.execMySQLCmd(user, initPasswd, flushCmd)
                
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
                keystone_dbpass = '123456'
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
                glance_dbpass = '123456'
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
                nova_dbpass = '123456'
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
                neutron_dbpass = '123456'
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
                cinder_dbpass = '123456'
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
    #####
#     MySQL.execMySQLCmd('root', 'dc95a64df31a8a82e4a8', 'create database pova;')
#     output, exitcode = MySQL.showTables('root', 'dc95a64df31a8a82e4a8', 'pova')
#     print 'output=%s--' % output
    ####
    
    MySQL.init()
    pass
    
    
    

