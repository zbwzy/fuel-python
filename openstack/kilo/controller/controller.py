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
#         NTP.install()
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
            ShellCmdExecutor.execCmd("echo '%s  %s' >> /etc/hosts" % (ip, domain))
            pass
        pass
    
class NTP(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    CONFIG_FILE_PATH = "/etc/ntp.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def initNTP():
        NTP.configNTPFile()
        
        restartNTPCmd = "service ntpd restart"
        ShellCmdExecutor.execCmd(restartNTPCmd)
        pass
    
    @staticmethod
    def configNTPFile():
        pass
    
    @staticmethod
    def install():
        print 'NTP.install start====='
        yumCmd = "yum install -y ntp"
        ShellCmdExecutor.execCmd(yumCmd)
        
        NTP.initNTP()
        print 'NTP.install done####'
        pass
    pass

class RDO(object):
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
    def install():
        yumCmd = "yum install yum-plugin-priorities -y"
        ShellCmdExecutor.execCmd(yumCmd)
        
        yumCmd = "yum install http://repos.fedorapeople.org/repos/openstack/openstack-icehouse/rdo-release-icehouse-3.noarch.rpm -y"
        ShellCmdExecutor.execCmd(yumCmd)
        
        yumCmd = "yum install http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm -y"
        ShellCmdExecutor.execCmd(yumCmd)
        pass
    pass

class OpenStack(object):
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
    def init():
        pass
    
    @staticmethod
    def install():
        yumCmd = "yum install openstack-utils -y"
        ShellCmdExecutor.execCmd(yumCmd)
        
        yumCmd = "yum install openstack-selinux -y"
        ShellCmdExecutor.execCmd(yumCmd)
        pass
    
    @staticmethod
    def installClient():
        yumCmd = "yum install python-openstackclient -y"
        ShellCmdExecutor.execCmd(yumCmd)
        pass
    
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
    
class RabbitMQ(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    INIT_USER_NAME = "guest"
    INIT_PASSWORD = "123456"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'RabbitMQ.install start====='
        yumCmd = "yum install -y rabbitmq-server.noarch"
        ShellCmdExecutor.execCmd(yumCmd)
        
        RabbitMQ.initRabbitMQ(RabbitMQ.INIT_USER_NAME, RabbitMQ.INIT_PASSWORD)
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

class Namespace(object):
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
    def install():
        print 'Namespace.install start======'
        yumCmd = "yum install kernel iproute -y"
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Namespace.install done####'
        pass
    pass

class AdminOpenrc(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def sourceAdminOpenrc():
        curDir = os.getcwd()
        print "curDir=%s" % curDir
        adminOpenrcFilePath = os.path.join(curDir, "configfile.template", "admin_openrc.sh")
        ShellCmdExecutor.execCmd("source %s" % adminOpenrcFilePath)
        pass

class KeyStone(object):
    '''
    classdocs
    '''
    CONFIG_FILE_PATH = "/etc/keystone/keystone.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def configEnvVar():
        ## configure env var
        ShellCmdExecutor.execCmd("export OS_SERVICE_TOKEN=123456")
        ShellCmdExecutor.execCmd("export OS_SERVICE_ENDPOINT=http://controller:35357/v2.0")
        pass
    
    @staticmethod
    def createAdminUser():
        ## create admin user
        ShellCmdExecutor.execCmd("keystone user-create --name=admin --pass=123456 --email=example@a.com")
        ShellCmdExecutor.execCmd("keystone role-create --name=admin")
        ShellCmdExecutor.execCmd("keystone tenant-create --name=admin --description=\"Admin Tenant\"")
        ShellCmdExecutor.execCmd("keystone user-role-add --user=admin --tenant=admin --role=admin")
        ShellCmdExecutor.execCmd("keystone user-role-add --user=admin --role=_member_ --tenant=admin")
        pass
    
    @staticmethod
    def createDemoUser():
        ShellCmdExecutor.execCmd("keystone user-create --name=demo --pass=123456 --email=demo@abc.com")
        ShellCmdExecutor.execCmd("keystone tenant-create --name=demo --description=\"Demo Tenant\"")
        ShellCmdExecutor.execCmd("keystone user-role-add --user=demo --role=_member_ --tenant=demo")
        pass
    
    @staticmethod
    def install():
        print "KeyStone.install start======="
        yumCmd = "yum install -y openstack-keystone python-keystoneclient"
        ShellCmdExecutor.execCmd(yumCmd)
        
        KeyStone.configConfFile()
        KeyStone.configDB()
        KeyStone.configKeyStone()
        #start
        ShellCmdExecutor.execCmd("service openstack-keystone start")
        ShellCmdExecutor.execCmd("chkconfig openstack-keystone on")
        #create user/tenant/role
        KeyStone.configEnvVar()
        ## create an admin user
        KeyStone.createAdminUser()
        ## create a normal user -- demo
        KeyStone.createDemoUser()
        #create service tenant
        ShellCmdExecutor.execCmd("keystone tenant-create --name=service --description=\"Service Tenant\"")
        #create keystone users,services & endpoint
        ShellCmdExecutor.execCmd("keystone service-create --name=keystone --type=identity --description=\"OpenStack Identity\"")

        cmd = "keystone endpoint-create \
        --service-id=$(keystone service-list | awk '/ identity / {print $2}') \
        --publicurl=http://controller:5000/v2.0 \
        --internalurl=http://controller:5000/v2.0 \
        --adminurl=http://controller:35357/v2.0"
        ShellCmdExecutor.execCmd(cmd)
        
        AdminOpenrc.sourceAdminOpenrc()        
        print "KeyStone.install done####"
        pass
    
    @staticmethod
    def configConfFile():
        
        newString = "connection=mysql://keystone:123456@controller/keystone"
        
        newString = "admin_token=123456"
        
        pass
    
    @staticmethod
    def configKeyStone():
        #configure KeyStone to support PKI token
        cmd = "keystone-manage pki_setup --keystone-user keystone --keystone-group keystone"
        ShellCmdExecutor.execCmd(cmd)
        ShellCmdExecutor.execCmd("chown -R keystone:keystone /etc/keystone/ssl")
        ShellCmdExecutor.execCmd("chmod -R o-rwx /etc/keystone/ssl")
        
        pass
    
    @staticmethod
    def configDB():
        createDbCmd = "CREATE DATABASE keystone"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, createDbCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        #Import db schema to Keystone db
        importDBCmd = "su -s /bin/sh -c \"keystone-manage db_sync\" keystone"
        ShellCmdExecutor.execCmd(importDBCmd)
        pass
    
class Glance(object):
    '''
    classdocs
    '''
    GLANCE_API_CONF_FILE_PATH = "/etc/glance/glance-api.conf"
    GLANCE_REGISTRY_CONF_FILE_PATH = "/etc/glance/glance-registry.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Glance.install start====='
        yumCmd = "yum install openstack-glance python-glanceclient"
        ShellCmdExecutor.execCmd(yumCmd)
        
        Glance.configConfFile()
        Glance.configDB()
        
        Glance.createGlanceUser()

        ShellCmdExecutor.execCmd("keystone service-create --name=glance --type=image --description=\"OpenStack Image Service\"")
        ShellCmdExecutor.execCmd("keystone endpoint-create --service-id=$(keystone service-list | awk '/ image / {print $2}') --publicurl=http://controller:9292 --internalurl=http://controller:9292 --adminurl=http://controller:9292")
        
        ShellCmdExecutor.execCmd("service openstack-glance-api start")
        ShellCmdExecutor.execCmd("service openstack-glance-registry start")
        ShellCmdExecutor.execCmd("chkconfig openstack-glance-api on")
        ShellCmdExecutor.execCmd("chkconfig openstack-glance-registry on")
        
        Glance.validation()
        
        print 'Glance.install done####'
        pass
    
    @staticmethod
    def validation():
        '''
        #Validate Glance success?
mkdir /tmp/images
cd /tmp/images/
wget http://cdn.download.cirros-cloud.net/0.3.2/cirros-0.3.2-x86_64-disk.img
#wget https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img

glance image-create --name "cirros-0.3.2-x86_64" --disk-format qcow2 \
--container-format bare --is-public True --progress < cirros-0.3.2-x86_64-disk.img

glance image-create --name "cirros-0.3.0-x86_64" --disk-format qcow2 \
--container-format bare --is-public True --progress < cirros-0.3.0-x86_64-disk.img

glance image-list
        '''
        print 'Glance.validation to be implemented======'
        pass
    
    @staticmethod
    def configConfFile():
        #use template file to replace the CONTROLLER_IP
        '''
2).config Glance conf file: glance-api.conf
connection=mysql://glance:123456@<CONTROLLER_IP>/glance

3). modify glance-api.conf ,set MQ Server:

rpc_backend=rabbit
rabbit_host=<CONTROLLER_IP>
rabbit_password=123456

4).modify glance-registry.conf:
connection=mysql://glance:123456@<CONTROLLER_IP>/glance

5).modify the files: glance-api.conf & glance-registry.conf,[keystone_authtoken] [paste_deploy]:
[keystone_authtoken]
auth_uri=http://controller:5000
auth_host=controller
auth_protocal=http
auth_port=35357
admin_tenant_name=service
admin_user=glance
admin_password=123456

[paste_deploy]
flavor=keystone
        '''
        pass
    
    @staticmethod
    def configDB():
        createDbCmd = "CREATE DATABASE glance"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, createDbCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        #Import db schema to Glance db
        importDBCmd = "su -s /bin/sh -c \"glance-manage db_sync\" glance"
        ShellCmdExecutor.execCmd(importDBCmd)
        pass
    
    @staticmethod
    def createGlanceUser():
        #prepare env var
        AdminOpenrc.sourceAdminOpenrc()
        ShellCmdExecutor.execCmd("keystone user-create --name=glance --pass=123456  --email=example@a.com")
        ShellCmdExecutor.execCmd("keystone user-role-add --user=glance --tenant=service --role=admin")
        pass
    pass

class Nova(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/nova/nova.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Nova.install start===='
        yumCmd = "yum install -y openstack-nova-api openstack-nova-cert openstack-nova-conductor openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler python-novaclient"
        ShellCmdExecutor.execCmd(yumCmd)
        Nova.configConfFile()
        Nova.configDB()
        Nova.createUserRole()
        
#         ShellCmdExecutor.execCmd("keystone service-create --name=nova --type=compute --description=\"OpenStack Compute\"")
#         ShellCmdExecutor.execCmd("keystone endpoint-create --service-id=$(keystone service-list | awk '/ compute / {print $2}') --publicurl=http://192.168.122.80:8774/v2/%\(tenant_id\)s  --internalurl=http://192.168.122.80:8774/v2/%\(tenant_id\)s --adminurl=http://192.168.122.80:8774/v2/%\(tenant_id\)s")
#         
        Nova.start()
        
        #After Network node configuration done
        Nova.configAfterNetworkNodeConfiguration()
        Nova.restart()
        print 'Nova.install done####'
        pass
    
    @staticmethod
    def configAfterNetworkNodeConfiguration():
        '''
1.on Controller node: moidfy /etc/nova/nova.conf, enabled metadata:

[DEFAULT]
service_neutron_metadata_proxy=true
neutron_metadata_proxy_shared_secret=123456

2. on Controller node: moidfy /etc/nova/nova.conf:to support VMs creation if vif_plug fails
vif_plugging_is_fatal=false
vif_plugging_timeout=0

        '''
        pass
    
    @staticmethod
    def restart():
        #restart Controller nova-api service
        restartCmd = "service openstack-nova-api restart"
        ShellCmdExecutor.execCmd(restartCmd)
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("service openstack-nova-api start")
        ShellCmdExecutor.execCmd("service openstack-nova-cert start")
        ShellCmdExecutor.execCmd("service openstack-nova-consoleauth start")
        ShellCmdExecutor.execCmd("service openstack-nova-scheduler start")
        ShellCmdExecutor.execCmd("service openstack-nova-conductor start")
        ShellCmdExecutor.execCmd("service openstack-nova-novncproxy start")
        
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-api on")
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-cert on")
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-consoleauth on ")
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-scheduler on")
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-conductor on")
        ShellCmdExecutor.execCmd("chkconfig openstack-nova-novncproxy on")
        pass
    
    @staticmethod
    def configConfFile():
        #use conf template file to replace <CONTROLLER_IP>
        '''
        #modify nova.conf:

[database]
connection=mysql://nova:123456@controller/nova

[DEFAULT]
rpc_backend=rabbit
rabbit_host=<CONTROLLER_IP>
rabbit_password=123456
my_ip=<CONTROLLER_IP>
vncserver_listen=<CONTROLLER_IP>
vncserver_proxyclient_address=<CONTROLLER_IP>
#########
#
rpc_backend=rabbit
rabbit_host=<CONTROLLER_IP>
rabbit_password=123456
my_ip=<CONTROLLER_IP>
vncserver_listen=<CONTROLLER_IP>
vncserver_proxyclient_address=<CONTROLLER_IP>

5).modify nova.conf: set the auth info of keystone:

[DEFAULT]
auth_strategy=keystone

[keystone_authtoken]
auth_uri=http://controller:5000
auth_host=<CONTROLLER_IP>
auth_protocal=http
auth_port=35357
admin_tenant_name=service
admin_user=nova
admin_password=123456
        '''
        pass
    
    @staticmethod
    def configDB():
        createDbCmd = "CREATE DATABASE nova"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, createDbCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        #Import db schema to Nova db
        importDBCmd = "su -s /bin/sh -c \"nova-manage db_sync\" nova"
        ShellCmdExecutor.execCmd(importDBCmd)
        pass
    
    @staticmethod
    def createUserRole():
        #create nova user & role
        ShellCmdExecutor.execCmd("keystone user-create --name=nova --pass=123456 --email=nova@example.com")
        ShellCmdExecutor.execCmd("keystone user-role-add --user=nova --tenant=service --role=admin")
        pass
    
class Dashboard(object):
    '''
    classdocs
    '''
    DASHBOARD_CONF_FILE_PATH = "/etc/openstack-dashboard/local_settings"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Dashboard.install start===='
        yumCmd = "yum install memcached python-memcached mod_wsgi openstack-dashboard"
        ShellCmdExecutor.execCmd(yumCmd)
        Dashboard.configConfFile()
        
        #assign network connect
        ShellCmdExecutor.execCmd("setsebool -P httpd_can_network_connect on")
        Dashboard.start()
        print 'Dashboard.install done####'
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("service httpd restart")
        ShellCmdExecutor.execCmd("service memcached restart")
        ShellCmdExecutor.execCmd("chkconfig httpd on")
        ShellCmdExecutor.execCmd("chkconfig memcached on")
        pass
    
    
    @staticmethod
    def configConfFile():
        '''
CACHES = {
'default': {
'BACKEND' : 'django.core.cache.backends.memcached.MemcachedCache',
'LOCATION' : '127.0.0.1:11211'
}
}
ALLOWED_HOSTS = ['localhost','my-desktop','*','0.0.0.0']
OPENSTACK_HOST = "controller"
        '''
        pass
    pass

class Neutron(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        Neutron.configDB()
        Neutron.createUserRole()
        
        #Install Neutron package,use ml2 as the second layer core_plugin
        yumCmd = "yum install openstack-neutron openstack-neutron-ml2 python-neutronclient -y"
        ShellCmdExecutor.execCmd(yumCmd)
        
        Neutron.configConfFile()
        
        #execute command to configure nova_admin_tenant_id
        ShellCmdExecutor.execCmd("openstack-config --set /etc/neutron/neutron.conf DEFAULT nova_admin_tenant_id $(keystone tenant-list | awk '/ service / { print $2 }')")

        #create soft link: from ml2_conf.ini to plugin.ini
        ShellCmdExecutor.execCmd("ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini")
        
        #start
        ShellCmdExecutor.execCmd("service neutron-server start")
        ShellCmdExecutor.execCmd("chkconfig neutron-server on")
        pass
    
    @staticmethod
    def configDB():
        createDbCmd = "CREATE DATABASE neutron"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, createDbCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        
        grantCmd = "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '123456'"
        MySQL.execMySQLCmd(MySQL.USERNAME, MySQL.INIT_PASSWORD, grantCmd)
        pass
    
    @staticmethod
    def createUserRole():
        '''
$ keystone endpoint-create --service-id $(keystone service-list | awk '/ network / {print $2}') --publicurl http://controller:9696 --adminurl http://controller:9696 --internalurl http://controller:9696

        '''
        ShellCmdExecutor.execCmd("keystone user-create --name neutron --pass 123456 --email neutron@example.com")
        ShellCmdExecutor.execCmd("keystone user-role-add --user neutron --tenant service --role admin")
        ShellCmdExecutor.execCmd("keystone service-create --name neutron --type network --description \"OpenStack Networking\"")
        ShellCmdExecutor.execCmd("keystone endpoint-create --service-id $(keystone service-list | awk '/ network / {print $2}') --publicurl http://controller:9696 --adminurl http://controller:9696 --internalurl http://controller:9696")
        pass
    
    @staticmethod
    def configConfFile():
        '''
        1.neutron.conf
[DEFAULT]
network_api_class=nova.network.neutronv2.api.API
neutron_url=http://controller:9696
neutron_auth_strategy=keystone
neutron_admin_tenant_name=service
neutron_admin_username=neutron
neutron_admin_password=123456
neutron_admin_auth_url=http://controller:35357/v2.0
linuxnet_interface_driver=nova.network.linux_net.LinuxOVSInterfaceDriver
firewall_driver=nova.virt.firewall.NoopFirewallDriver
security_group_api=neutron

auth_strategy=keystone
rpc_backend = neutron.openstack.common.rpc.impl_kombu
rabbit_host =controller
rabbit_password = 123456
notify_nova_on_port_status=true
notify_nova_on_port_data_changes=true
nova_url=http://controller:8774/v2
nova_admin_username=nova
nova_admin_password=123456
nova_admin_auth_url=http://contorller:35357/v2.0
core_plugin=ml2
service_plugins=router

[keystone_authtoken]
auth_host=controller
auth_protocal=http
auth_port=35357
admin_tenant_name=service
admin_user=neutron
admin_password=123456

[database]
connection = mysql://neutron:123456@controller/neutron

2.configure ML2

modify /etc/neutron/plugins/ml2/ml2_conf.ini

[ml2]
type_driver=gre,flat
tenant_network_types=gre,flat
mechanism_drivers=openvswitch

[ml2_type_flat]
flat_networks = physnet1

[ml2_type_gre]
tunnel_id_ranges =1:1000

[securitygroup]
firewall_driver=neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver
enable_security_group=true

3. configure Compute: use Neutron to provide network services

modify /etc/nova/nova.conf

[DEFAULT]
network_api_class=nova.network.neutronv2.api.API
neutron_url=http://controller:9696
neutron_auth_strategy=keystone
neutron_admin_tenant_name=service
neutron_admin_username=neutron
neutron_admin_password=123456
neutron_admin_auth_url=http://controller:35357/v2.0
linuxnet_interface_driver=nova.network.linux_net.LinuxOVSInterfaceDriver
firewall_driver=nova.virt.firewall.NoopFirewallDriver
security_group_api=neutron

        '''
        pass
    pass

class FWaaS(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        '''
        1)    on Controller, Network node: modify neutron.conf
#### service_plugins add fwaas
service_plugins= router,firewall,lbaas

2)    modify fwaas.ini conf file: /etc/neutron/fwaas_driver.ini

[fwaas]
driver = neutron.services.firewall.drivers.linux.iptables_fwaas.IptablesFwaasDriver
enabled = True

3)    on Neutron-Controller, Network: lbaas.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
ovs_use_veth = True
device_driver = neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver

        '''
        
        #Install haproxy @network node, controller node
        ShellCmdExecutor.execCmd("yum intsall haproxy -y")
        
        #create nogroup , nobody @network, controller node
        ShellCmdExecutor.execCmd("groupadd nogroup")
        ShellCmdExecutor.execCmd("useradd -g nogroup nobody")

        '''
        4)    moidfy dashboard configuration to support use FWaaS
###on Controller Node,/etc/openstack-dashboard/local_settings

OPENSTACK_NEUTRON_NETWORK = {
    'enable_firewall': True,
}

OPENSTACK_NEUTRON_NETWORK = {
    'enable_lbaas': True,
}
        '''
        # restart  neutron server @ controller node
        ShellCmdExecutor.execCmd("/etc/init.d/neutron-server restart")
        
        #restart dashboard
        ShellCmdExecutor.execCmd("/etc/init.d/httpd restart")
        pass
    
class LBaaS(object):
    '''
    classdocs
    '''
    NEUTRON_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    NEUTRON_ML2_CONF_FILE_PATH = "/etc/neutron/plugins/ml2/ml2_conf.ini"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        pass

    '''
    5)    Install LoadBalance services:
1)    on Neutron-Controller and Network: neutron.conf

[DEFAULT]
service_plugins= router,firewall,lbaas

2)    on Neutron-Controller, Network: lbaas.ini
[DEFAULT]
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver
ovs_use_veth = True
device_driver = neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver

3)    Install haproxy @network node, controller node
yum intsall haproxy

4)    create nogroup , nobody @network, controller node

# groupadd nogroup
# useradd -g nogroup nobody

5)    restart neutron-server  neutron-lbaas-agent

@controller node
# /etc/init.d/neutron-server restart

@network node
# /etc/init.d/neutron-lbaas-agent restart
# chkconfig neutron-lbaas-agent on


6)    modify dashboard to support LBaaS
on Controller Node:/etc/openstack-dashboard/local_settings

OPENSTACK_NEUTRON_NETWORK = {
    'enable_lbaas': True,
}

7)    restart dashboard
# /etc/init.d/httpd restart
    '''


if __name__ == '__main__':
    print 'openstack-icehouse:controller install============'
    print 'start time: %s' % time.ctime()
    argv = sys.argv
    argv.pop(0)
    print "agrv=%s--" % argv
    if len(argv) > 0 :
        LOCAL_IP = argv[0]
        pass
    else :
        print "ERROR:no params."
        pass
    
    output, exitcode = ShellCmdExecutor.execCmd('ls -lt')
    print 'ooutput=\n%s--' % output
    
#     Prerequisites.install(LOCAL_IP, "controller")
#     MySQL.install()
#     RDO.install()
#     OpenStack.install()
#     RabbitMQ.install()
#     Namespace.install()
#     
#     KeyStone.install()
#     OpenStack.installClient()
#     Glance.install()
#     Nova.install()
#     
#     Dashboard.install()
#     Neutron.install()
    curDir = os.getcwd()
    print "curDir=%s" % curDir
    adminOpenrcFilePath = os.path.join(curDir, "configfile.template", "admin_openrc.sh")
    ShellCmdExecutor.execCmd("source %s" % adminOpenrcFilePath)
    print 'end time: %s' % time.ctime()
    print 'openstack-icehouse:controller done#####'
    


