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
    def prepare():
        Network.Prepare()
        
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
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
        #Enable 
        if debug == True:
            print 'DEBUG is True.On local dev env, do test====='
            yumCmd = "ls -lt"
        else :
            yumCmd = "yum install openstack-glance python-glanceclient -y"
            
        output, exitcode = ShellCmdExecutor.execCmd(yumCmd)
        print 'output=\n%s--' % output
        Glance.configConfFile()
        Glance.start()
        
        print 'Glance node install done####'
        pass
    
    @staticmethod
    def start():
        print "start glance========="
        if debug == True :
            print 'DEBUG=True.On local dev env, do test===='
            pass
        else :
            ShellCmdExecutor.execCmd('service openstack-glance-api start')
            ShellCmdExecutor.execCmd('service openstack-glance-registry start')
            
            ShellCmdExecutor.execCmd('chkconfig openstack-glance-api on')
            ShellCmdExecutor.execCmd('chkconfig openstack-glance-registry on')
        print "start glance done####"
        pass
    
    @staticmethod
    def restart():
        print "restart glance========="
        if debug == True :
            print 'DEBUG=True.On local dev env, do test===='
            pass
        else :
            ShellCmdExecutor.execCmd('service openstack-glance-api restart')
            ShellCmdExecutor.execCmd('service openstack-glance-registry restart')
            pass
        
        print "restart glance done####"
        pass
    
    @staticmethod
    def configConfFile():
        print "configure glance conf file======"
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        glance_vip = JSONUtility.getValue("glance_vip")
        print "glance_vip=%s" % glance_vip
        glance_ips = JSONUtility.getValue("glance_ips")
        print "glance_ips=%s" % glance_ips
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        rabbit_host = JSONUtility.getValue("rabbit_host")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        glanceConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'GLANCE_CONF_DIR')
        print 'glanceConfDir=%s' % glanceConfDir #/etc/glance
        
        glance_api_conf_file_path = os.path.join(glanceConfDir, 'glance-api.conf')
        glance_registry_conf_file_path = os.path.join(glanceConfDir, 'glance-registry.conf')
        
        if not os.path.exists(glanceConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir -p %s" % glanceConfDir)
            pass
        #if exist, remove original conf files
        if os.path.exists(glance_api_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % glance_api_conf_file_path)
            pass
        
        if os.path.exists(glance_registry_conf_file_path) :
            print 'tttttttt====='
            print 'glance_registry_conf_file_path=%s' % glance_registry_conf_file_path
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % glance_registry_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glanceConfDir)
        
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ######NEW
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/glance-api.conf" % SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH)
        ShellCmdExecutor.execCmd("cat %s > /tmp/glance-registry.conf" % SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH)
        
        ShellCmdExecutor.execCmd("mv /tmp/glance-api.conf /etc/glance")
        ShellCmdExecutor.execCmd("mv /tmp/glance-registry.conf /etc/glance")
        
        ShellCmdExecutor.execCmd("rm -rf /tmp/glance-api.conf")
        ShellCmdExecutor.execCmd("rm -rf /tmp/glance-registry.conf")
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_registry_conf_file_path)
        ###########LOCAL_IP:retrieve it from one file, the LOCAL_IP file is generated when this project inits.
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        print 'localip=%s--' % localIP
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<LOCAL_IP>', localIP)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<GLANCE_VIP>', glance_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<GLANCE_VIP>', glance_vip)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % glance_registry_conf_file_path)
        pass
    
    @staticmethod
    def initGlance():
        glanceInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'glance_init.sh')
        print 'glanceInitScriptPath=%s' %glanceInitScriptPath
        
        if os.path.exists('/opt/glance_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/glance_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % glanceInitScriptPath)
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')

        localIP = output.strip()
        
        glanceAdminEmail = JSONUtility.getValue("admin_email")
        print 'glanceAdminEmail=%s' % glanceAdminEmail
        FileUtil.replaceFileContent('/opt/glance_init.sh', '<ADMIN_EMAIL>', glanceAdminEmail)
        
        glance_vip = JSONUtility.getValue("glance_vip")
        FileUtil.replaceFileContent('/opt/glance_init.sh', '<GLANCE_VIP>', glance_vip)
        FileUtil.replaceFileContent('/opt/glance_init.sh', '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/glance_init.sh')
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
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
        rabbit_host = JSONUtility.getValue("rabbit_host")
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        
        #controller: Horizon, Neutron-server
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        nova_api_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'nova.conf')
        print 'nova_api_conf_template_file_path=%s' % nova_api_conf_template_file_path
        
        novaConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'NOVA_CONF_DIR')
        print 'novaConfDir=%s' % novaConfDir #/etc/keystone
        
        nova_conf_file_path = os.path.join(novaConfDir, 'nova.conf')
        print 'nova_conf_file_path=%s' % nova_conf_file_path
        
        if not os.path.exists(novaConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % novaConfDir)
            pass
        
        if os.path.exists(nova_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % nova_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd("chmod 777 /etc/nova")
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (nova_api_conf_template_file_path, novaConfDir))
        ####NEW
        ShellCmdExecutor.execCmd('cat %s > /tmp/nova.conf' % nova_api_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/nova.conf /etc/nova")
        
        ShellCmdExecutor.execCmd("rm -rf /tmp/nova.conf")
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % nova_conf_file_path)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        ######rabbitmq cluster
#         FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
#         FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
#         FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<MANAGEMENT_LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<PUBLIC_LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NEUTRON_VIP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % nova_conf_file_path)
        pass
    
    @staticmethod
    def initNova():
        novaInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'nova_init.sh')
        print 'novaInitScriptPath=%s' % novaInitScriptPath
        
        if os.path.exists('/opt/nova_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/nova_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % novaInitScriptPath)
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')

        localIP = output.strip()
        
        novaAdminEmail = JSONUtility.getValue("admin_email")
        print 'novaAdminEmail=%s' % novaAdminEmail
        FileUtil.replaceFileContent('/opt/nova_init.sh', '<ADMIN_EMAIL>', novaAdminEmail)
        
        nova_vip = JSONUtility.getValue("nova_vip")
        FileUtil.replaceFileContent('/opt/nova_init.sh', '<NOVA_VIP>', nova_vip)
        FileUtil.replaceFileContent('/opt/nova_init.sh', '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/nova_init.sh')
        pass
    
class Neutron(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/neutron/neutron.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def initNeutron():
        neutronInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'network', 'neutron_init.sh')
        print 'neutronInitScriptPath=%s' % neutronInitScriptPath
        
        if os.path.exists('/opt/neutron_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/neutron_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % neutronInitScriptPath)
        
        neutronAdminEmail = JSONUtility.getValue("admin_email")
        print 'neutronAdminEmail=%s' % neutronAdminEmail
        FileUtil.replaceFileContent('/opt/neutron_init.sh', '<ADMIN_EMAIL>', neutronAdminEmail)
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        neutron_vip = JSONUtility.getValue("neutron_vip")
        FileUtil.replaceFileContent('/opt/neutron_init.sh', '<NEUTRON_VIP>', neutron_vip)
        FileUtil.replaceFileContent('/opt/neutron_init.sh', '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/neutron_init.sh')
        pass
    pass


class Cinder(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/cinder/cinder.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Cinder.install start===='
        yumCmd = 'yum install openstack-cinder python-cinderclient python-oslo-db -y'
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Cinder.install done####'
        pass

    @staticmethod
    def restart():
        #restart cinder service
        ShellCmdExecutor.execCmd("service openstack-cinder-api restart")
        ShellCmdExecutor.execCmd("service openstack-cinder-scheduler restart")
        pass
    
    @staticmethod
    def start():        
        ShellCmdExecutor.execCmd("service openstack-cinder-api start")
        ShellCmdExecutor.execCmd("service openstack-cinder-scheduler start")
        pass
    
    @staticmethod
    def configConfFile():
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
        rabbit_host = JSONUtility.getValue("rabbit_host")
        
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        cinder_mysql_password = JSONUtility.getValue("cinder_mysql_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_host=%s' % rabbit_host
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        cinder_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'cinder.conf')
        print 'nova_api_conf_template_file_path=%s' % cinder_conf_template_file_path
        
        cinderConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'CINDER_CONF_DIR')
        print 'cinderConfDir=%s' % cinderConfDir #/etc/cinder
        
        cinder_conf_file_path = os.path.join(cinderConfDir, 'cinder.conf')
        print 'cinder_conf_file_path=%s' % cinder_conf_file_path
        
        if not os.path.exists(cinderConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % cinderConfDir)
            pass
        
        if os.path.exists(cinder_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % cinder_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 /etc/cinder")
        
        ####NEW
        ShellCmdExecutor.execCmd("cat %s > /tmp/cinder.conf" % cinder_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/cinder.conf /etc/cinder/")
        ShellCmdExecutor.execCmd("rm -rf /tmp/cinder.conf")
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % cinder_conf_file_path)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<CINDER_MYSQL_PASSWORD>', cinder_mysql_password)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % cinder_conf_file_path)
        pass
    
    @staticmethod
    def initCinder():
        cinderInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'cinder_init.sh')
        print 'cinderInitScriptPath=%s' % cinderInitScriptPath
        
        if os.path.exists('/opt/cinder_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/cinder_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % cinderInitScriptPath)
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        cinderAdminEmail = JSONUtility.getValue("admin_email")
        print 'cinderAdminEmail=%s' % cinderAdminEmail
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<ADMIN_EMAIL>', cinderAdminEmail)
        
        cinder_vip = JSONUtility.getValue("cinder_vip")
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<CINDER_VIP>', cinder_vip)
        
        cinder_mysql_password = JSONUtility.getValue("cinder_mysql_password")
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<CINDER_MYSQL_PASSWORD>', cinder_mysql_password)
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/cinder_init.sh')
        pass
    pass



class Ceilometer(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def initCeilometer():
        initScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'ceilometer_init.sh')
        print 'ceilometerInitScriptPath=%s' % initScriptPath
        
        if os.path.exists('/opt/ceilometer_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/ceilometer_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % initScriptPath)
        
        ShellCmdExecutor.execCmd('chmod 777 /opt/ceilometer_init.sh')
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        adminEmail = JSONUtility.getValue("admin_email")
        print 'ceilometerAdminEmail=%s' % adminEmail
        FileUtil.replaceFileContent('/opt/ceilometer_init.sh', '<ADMIN_EMAIL>', adminEmail)
        
        ceilometer_vip = JSONUtility.getValue("ceilometer_vip")
        
        FileUtil.replaceFileContent('/opt/ceilometer_init.sh', '<CEILOMETER_VIP>', ceilometer_vip)
        
        FileUtil.replaceFileContent('/opt/ceilometer_init.sh', '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/ceilometer_init.sh')
        pass
    pass


class Heat(object):
    '''
    classdocs
    '''
    HEAT_CONF_FILE_PATH = "/etc/heat/heat.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Heat.install start===='
        yumCmd = 'yum install openstack-heat-api openstack-heat-api-cfn openstack-heat-engine python-heatclient -y'
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Heat.install done####'
        pass

    @staticmethod
    def restart():
        #restart heat service
        ShellCmdExecutor.execCmd("service openstack-heat-api restart")
        ShellCmdExecutor.execCmd("service openstack-heat-api-cfn restart")
        ShellCmdExecutor.execCmd("service  openstack-heat-engine restart")
        pass
    
    
    @staticmethod
    def start():    
        ShellCmdExecutor.execCmd("service openstack-heat-api start")
        ShellCmdExecutor.execCmd("service openstack-heat-api-cfn start")
        ShellCmdExecutor.execCmd("service  openstack-heat-engine start")
            
        ShellCmdExecutor.execCmd("chkconfig openstack-heat-api on")
        ShellCmdExecutor.execCmd("chkconfig openstack-heat-api-cfn on")
        ShellCmdExecutor.execCmd("chkconfig  openstack-heat-engine on")
        pass
    
    @staticmethod
    def configConfFile():
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
        rabbit_host = JSONUtility.getValue("rabbit_host")
        
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        glance_vip = JSONUtility.getValue("glance_vip")
        heat_mysql_password = JSONUtility.getValue("heat_mysql_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_host=%s' % rabbit_host
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        heat_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'heat', 'heat.conf')
        print 'heat_conf_template_file_path=%s' % heat_conf_template_file_path
        
        heatConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HEAT_CONF_DIR')
        print 'heatConfDir=%s' % heatConfDir #/etc/heat
        
        heat_conf_file_path = os.path.join(heatConfDir, 'heat.conf')
        print 'heat_conf_file_path=%s' % heat_conf_file_path
        
        if not os.path.exists(heatConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % heatConfDir)
            pass
        
        if os.path.exists(heat_conf_file_path) :
            ShellCmdExecutor.execCmd("rm -rf %s" % heat_conf_file_path)
            pass
        
        print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx====='
        print 'existHeatConf=%s' % os.path.exists('/etc/heat/heat.conf')
        ShellCmdExecutor.execCmd("sudo chmod 777 /etc/heat")
        ShellCmdExecutor.execCmd('cat %s > %s' % (heat_conf_template_file_path, '/tmp/heat.conf'))
        ShellCmdExecutor.execCmd('mv /tmp/heat.conf %s' % heatConfDir)
#         ShellCmdExecutor.execCmd("rm -rf /tmp/heat.conf")
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % heat_conf_file_path)
        print 'yyyyyyyyyyyyyyyyyyyyyyyyyyyy======='
        print 'existHeatConf=%s--' % os.path.exists('/etc/heat/heat.conf')
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(heat_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<HEAT_MYSQL_PASSWORD>', heat_mysql_password)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(heat_conf_file_path, '<GLANCE_VIP>', glance_vip)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % heat_conf_file_path)
        pass
    
    @staticmethod
    def initHeat():
        heatInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'heat', 'heat_init.sh')
        print 'heatInitScriptPath=%s' % heatInitScriptPath
        
        if os.path.exists('/opt/heat_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/heat_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % heatInitScriptPath)
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        heatAdminEmail = JSONUtility.getValue("admin_email")
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<ADMIN_EMAIL>', heatAdminEmail)
        
        heat_vip = JSONUtility.getValue("heat_vip")
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<HEAT_VIP>', heat_vip)
        
        heat_mysql_password = JSONUtility.getValue("heat_mysql_password")
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<HEAT_MYSQL_PASSWORD>', heat_mysql_password)
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd('bash /opt/heat_init.sh')
        pass
    pass

class Keystone(object):
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
        print 'Keystone node install start========'
        #Enable 
        if debug == True:
            print 'DEBUG is True.On local dev env, do test====='
            yumCmd = "ls -lt"
        else :
            yumCmd = "yum install openstack-keystone python-keystoneclient -y"
            
        output, exitcode = ShellCmdExecutor.execCmd(yumCmd)
        print 'output=\n%s--' % output
        Keystone.configConfFile()
        Keystone.start()
        
        print 'Keystone node install done####'
        pass
    
    @staticmethod
    def start():
        print "start keystone========="
        if debug == True :
            print 'DEBUG=True.On local dev env, do test===='
            pass
        else :
            ShellCmdExecutor.execCmd('service openstack-keystone start')
            ShellCmdExecutor.execCmd('chkconfig openstack-keystone on')
        print "start keystone done####"
        pass
    
    @staticmethod
    def restart():
        print "restart keystone========="
        if debug == True :
            print 'DEBUG=True.On local dev env, do test===='
            pass
        else :
            ShellCmdExecutor.execCmd('service openstack-keystone restart')
            pass
        
        print "restart keystone done####"
        pass
    
    @staticmethod
    def importKeystoneDBSchema():
        #Before import,detect the database rights for mysql user keystone.
        
        ##
        importCmd = 'su -s /bin/sh -c "keystone-manage db_sync" keystone'
        ShellCmdExecutor.execCmd(importCmd)
        pass
    
    @staticmethod
    def supportPKIToken():
        cmd0 = 'keystone-manage pki_setup --keystone-user keystone --keystone-group keystone'
        cmd1 = 'chown -R keystone:keystone /var/log/keystone'
        cmd2 = 'chown -R keystone:keystone /etc/keystone/ssl'
        cmd3 = 'chmod -R o-rwx /etc/keystone/ssl'
        ShellCmdExecutor.execCmd(cmd0)
        ShellCmdExecutor.execCmd(cmd1)
        ShellCmdExecutor.execCmd(cmd2)
        ShellCmdExecutor.execCmd(cmd3)
        pass
    
    @staticmethod
    def configureEnvVar():
        ShellCmdExecutor.execCmd('export OS_SERVICE_TOKEN=123456')
        template_string = 'export OS_SERVICE_ENDPOINT=http://<KEYSTONE_VIP>:35357/v2.0'
        keystone_vip = JSONUtility.getValue('keystone_vip')
        cmd = template_string.replace('<KEYSTONE_VIP>', keystone_vip)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def initKeystone():
        keystoneInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'keystone_init.sh')
        print 'keystoneInitScriptPath=%s' % keystoneInitScriptPath
        
        if os.path.exists('/opt/keystone_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/keystone_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % keystoneInitScriptPath)
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<LOCAL_IP>', localIP)
        
        keystoneAdminEmail = JSONUtility.getValue("admin_email")
        print 'keystoneAdminEmail=%s' % keystoneAdminEmail
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<ADMIN_EMAIL>', keystoneAdminEmail)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<LOCAL_IP>', localIP)
        print 'keystone db init==========================='
        print ''
        print 'keystone process----------'
        out, exitcode = ShellCmdExecutor.execCmd('ps aux | grep keystone')
        print output
        
        out, exitcode = ShellCmdExecutor.execCmd('cat /opt/keystone_init.sh')
        print 'keystone init script==============='
        print output
        print 'keystone init script#######'
        print 'bash /opt/keystone_init.sh=========================='
        output, exitcode = ShellCmdExecutor.execCmd('bash /opt/keystone_init.sh')
        print 'output=%s--' % output
        pass
        
    @staticmethod
    def sourceAdminOpenRC():
        adminOpenRCScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'admin_openrc.sh')
        print 'adminOpenRCScriptPath=%s' % adminOpenRCScriptPath
        
        if os.path.exists('/opt/admin_openrc.sh') :
            ShellCmdExecutor.execCmd("rm -rf /opt/admin_openrc.sh")
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % adminOpenRCScriptPath)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        #Only for db init
        output, exitcode = ShellCmdExecutor.execCmd("cat /opt/localip")
        localIP = output.strip()
        
        FileUtil.replaceFileContent('/opt/admin_openrc.sh', '<KEYSTONE_VIP>', localIP)
        time.sleep(2)
        ShellCmdExecutor.execCmd('source /opt/admin_openrc.sh')
        pass
    
    @staticmethod
    def configConfFile():
        print "configure keystone conf file======"
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        keystoneConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEYSTONE_CONF_DIR')
        print 'keystoneConfDir=%s' % keystoneConfDir #/etc/keystone
        
        keystone_conf_file_path = os.path.join(keystoneConfDir, 'keystone.conf')
        
        if not os.path.exists(keystoneConfDir) :
            os.system("sudo mkdir -p %s" % keystoneConfDir)
            pass
        #if exist, remove original conf files
        if os.path.exists(keystone_conf_file_path) :
            os.system("sudo rm -rf %s" % keystone_conf_file_path)
            pass
        
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH, keystoneConfDir))
        #########mv
        ShellCmdExecutor.execCmd('chmod 777 %s' % keystoneConfDir)
        output, exitcode = ShellCmdExecutor.execCmd("cat %s > /tmp/keystone.conf" % SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH)
        
        ShellCmdExecutor.execCmd('mv /tmp/keystone.conf %s' % keystoneConfDir)
        ShellCmdExecutor.execCmd('rm -rf /tmp/keystone.conf')
        
        #####
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keystone_conf_file_path)
        ###########LOCAL_IP:retrieve it from one file, the LOCAL_IP file is generated when this project inits.
        localIP = Keystone.getLocalIP()
        print 'localip=%s--' % localIP
        
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<LOCAL_IP>', localIP)
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        
        #for db init
        mysql_port = '3309'
        mysql_vip = localIP
        
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_PORT>', mysql_port)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keystone_conf_file_path)
        print "configure keystone conf file done####"
        pass
    
    @staticmethod
    def getLocalIP():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        return localIP
    
class KeystoneHA(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isExistVIP(vip, interface):
        cmd = 'ip addr show dev {interface} | grep {vip}'.format(interface=interface, vip=vip)
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == None or output == '':
            print 'Do no exist vip %s on interface %s.' % (vip, interface)
            return False
        
        if debug == True :
            output = '''
            xxxx
            inet 192.168.11.100/32 scope global eth0
            xxxx
            '''
            pass
        
        newString = vip + '/'
        if newString in output :
            print 'exist vip %s on interface %s.' % (vip, interface)
            return True
        else :
            print 'Do no exist vip %s on interface %s.' % (vip, interface)
            return False
        pass
    
    #return value: 192.168.11.100/32
    @staticmethod
    def getVIPFormatString(vip, interface):
        vipFormatString = ''
        if KeystoneHA.isExistVIP(vip, interface) :
            print 'getVIPFormatString====exist vip %s on interface %s' % (vip, interface) 
            cmd = 'ip addr show dev {interface} | grep {vip}'.format(interface=interface, vip=vip)
            output, exitcode = ShellCmdExecutor.execCmd(cmd)
            vipFormatString = output.strip()
            if debug == True :
                fakeVIPFormatString = 'inet 192.168.11.100/32 scope global eth0'
                vipFormatString = fakeVIPFormatString
                pass
            
            result = vipFormatString.split(' ')[1]
            pass
        else :
            #construct vip format string
            print 'getVIPFormatString====do not exist vip %s on interface %s, to construct vip format string' % (vip, interface) 
            vipFormatString = '{vip}/32'.format(vip=vip)
            print 'vipFormatString=%s--' % vipFormatString
            result = vipFormatString
            pass
        
        return result
    
    @staticmethod
    def addVIP(vip, interface):
        result = KeystoneHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not KeystoneHA.isExistVIP(vip, interface) :
            print 'NOT exist vip %s on interface %s.' % (vip, interface)
            addVIPCmd = 'ip addr add {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'addVIPCmd=%s--' % addVIPCmd
            ShellCmdExecutor.execCmd(addVIPCmd)
            pass
        else :
            print 'The VIP %s already exists on interface %s.' % (vip, interface)
            pass
        pass
    
    @staticmethod
    def deleteVIP(vip, interface):
        result = KeystoneHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if KeystoneHA.isExistVIP(vip, interface) :
            deleteVIPCmd = 'ip addr delete {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'deleteVIPCmd=%s--' % deleteVIPCmd
            ShellCmdExecutor.execCmd(deleteVIPCmd)
            pass
        else :
            print 'The VIP %s does not exist on interface %s.' % (vip, interface)
            pass
        pass
    
    @staticmethod
    def isKeepalivedInstalled():
        KEEPALIVED_CONF_FILE_PATH = '/etc/keepalived/keepalived.conf'
        if os.path.exists(KEEPALIVED_CONF_FILE_PATH) :
            return True
        else :
            return False
        
    @staticmethod
    def isHAProxyInstalled():
        HAPROXY_CONF_FILE_PATH = '/etc/haproxy/haproxy.cfg'
        if os.path.exists(HAPROXY_CONF_FILE_PATH) :
            return True
        else :
            return False
    
    @staticmethod
    def install():
        if debug == True :
            print "DEBUG is True.On local dev env, do test==="
            yumCmd = "ls -lt"
            ShellCmdExecutor.execCmd(yumCmd)
            pass
        else :
            if not KeystoneHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not KeystoneHA.isHAProxyInstalled() :
                haproxyInstallCmd = 'yum install haproxy -y'
                ShellCmdExecutor.execCmd(haproxyInstallCmd)
                
                #prepare haproxy conf file template
                openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
                haproxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
                haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
                print 'haproxyTemplateFilePath=%s' % haproxyTemplateFilePath
                print 'haproxyConfFilePath=%s' % haproxyConfFilePath
                if not os.path.exists('/etc/haproxy') :
                    ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
                    pass
                
                ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (haproxyTemplateFilePath, '/etc/haproxy'))
                pass
            pass
        pass
    
    @staticmethod
    def configure():
        KeystoneHA.configureHAProxy()
        KeystoneHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        #server keystone-01 192.168.1.137:35357 check inter 10s
        keystone_vip = JSONUtility.getValue("keystone_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        keystoneHAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (keystoneHAProxyTemplateFilePath, '/etc/haproxy'))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        ####
        ##############new
        keystoneBackendAdminApiStringTemplate = '''
listen keystone_admin_cluster
  bind <KEYSTONE_VIP>:35357
  balance source
  <KEYSTONE_ADMIN_API_SERVER_LIST>
  '''
        keystoneBackendPublicApiStringTemplate = '''
listen keystone_public_internal_cluster
  bind <KEYSTONE_VIP>:5000
  <KEYSTONE_PUBLIC_API_SERVER_LIST>
  '''
        keystoneBackendAdminApiString = keystoneBackendAdminApiStringTemplate.replace('<KEYSTONE_VIP>', keystone_vip)
        keystoneBackendPublicApiString = keystoneBackendPublicApiStringTemplate.replace('<KEYSTONE_VIP>', keystone_vip)
        
        ################new
        keystone_ips = JSONUtility.getValue("keystone_ips")
        
        output, exitcode = ShellCmdExecutor.execCmd("cat /opt/localip")
        mysql_master_ip = output.strip()
        keystone_ips_list = []
        keystone_ips_list.append(mysql_master_ip)
        
        serverKeystoneAdminAPIBackendTemplate   = 'server keystone-<INDEX> <SERVER_IP>:35357 check inter 2000 rise 2 fall 5'
        serverKeystonePublicAPIBackendTemplate  = 'server keystone-<INDEX> <SERVER_IP>:5000 check inter 2000 rise 2 fall 5'
        
        keystoneAdminAPIServerListContent = ''
        keystonePublicAPIServerListContent = ''
        
        index = 1
        for keystone_ip in keystone_ips_list:
            print 'keystone_ip=%s' % keystone_ip
            keystoneAdminAPIServerListContent += serverKeystoneAdminAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            keystonePublicAPIServerListContent += serverKeystonePublicAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            
            keystoneAdminAPIServerListContent += '\n'
            keystoneAdminAPIServerListContent += '  '
            
            keystonePublicAPIServerListContent += '\n'
            keystonePublicAPIServerListContent += '  '
            index += 1
            pass
        
        keystoneAdminAPIServerListContent = keystoneAdminAPIServerListContent.strip()
        keystonePublicAPIServerListContent = keystonePublicAPIServerListContent.strip()
        print 'keystoneAdminAPIServerListContent=%s--' % keystoneAdminAPIServerListContent
        print 'keystonePublicAPIServerListContent=%s--' % keystonePublicAPIServerListContent
        
        keystoneBackendAdminApiString = keystoneBackendAdminApiString.replace('<KEYSTONE_ADMIN_API_SERVER_LIST>', keystoneAdminAPIServerListContent)
        keystoneBackendPublicApiString = keystoneBackendPublicApiString.replace('<KEYSTONE_PUBLIC_API_SERVER_LIST>', keystonePublicAPIServerListContent)
        
        print 'keystoneBackendAdminApiString=%s--' % keystoneBackendAdminApiString
        print 'keystoneBackendPublicApiString=%s--' % keystoneBackendPublicApiString
        
        #append
        if os.path.exists(haproxyConfFilePath) :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % haproxyConfFilePath)
        else :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % keystoneHAProxyTemplateFilePath)
            pass
        
        haproxyNativeContent = output.strip()
        
        MYSQL_MASTER_NATIVE_HAPROXY = '/tmp/mysql_haproxy.cfg'
        FileUtil.writeContent(MYSQL_MASTER_NATIVE_HAPROXY, haproxyNativeContent)
        
        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        
        haproxyContent += keystoneBackendAdminApiString
        haproxyContent += keystoneBackendPublicApiString
        
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        if os.path.exists(haproxyConfFilePath):
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % haproxyConfFilePath)
            pass
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy')
        #############
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)
        pass
    
    @staticmethod
    def configureKeepalived():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        ###################configure keepalived
        keepalivedTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keepalived.conf')
        keepalivedConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEEPALIVED_CONF_FILE_PATH')
        print 'keepalivedConfFilePath=%s' % keepalivedConfFilePath
        if not os.path.exists('/etc/keepalived') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/keepalived')
            pass
        
        #configure haproxy check script in keepalived
        checkHAProxyScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (checkHAProxyScriptPath, '/etc/keepalived'))
        if os.path.exists(keepalivedConfFilePath) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % keepalivedConfFilePath)
            pass
        
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (keepalivedTemplateFilePath, '/etc/keepalived'))
        print 'keepalivedTemplateFilePath=%s==========----' % keepalivedTemplateFilePath
        print 'keepalivedConfFilePath=%s=============----' % keepalivedConfFilePath
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keepalivedConfFilePath)
        ##configure
        '''keepalived template====
        global_defs {
  router_id LVS-DEVEL
}
vrrp_script chk_haproxy {
   script "/etc/keepalived/check_haproxy.sh"
   interval 2
   weight  2
}

vrrp_instance 42 {
  virtual_router_id 42
  # for electing MASTER, highest priority wins.
  priority  <KEYSTONE_WEIGHT>
  state     <KEYSTONE_STATE>
  interface <INTERFACE>
  track_script {
    chk_haproxy
}
  virtual_ipaddress {
        <VIRTURL_IPADDR>
  }
}
        '''
        #GLANCE_WEIGHT is from 300 to down, 300 belongs to MASTER, and then 299, 298, ...etc, belong to SLAVE
        ##Here: connect to ZooKeeper to coordinate the weight
        keystone_vip = JSONUtility.getValue("keystone_vip")
        keystone_vip_interface = JSONUtility.getValue("keystone_vip_interface")
        
        weight_counter = 300
        if KeystoneHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = KeystoneHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass
            
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', keystone_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', keystone_vip)
        
        ##temporary: if current user is not root
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keepalivedConfFilePath)
        
        #If keepalived need to support more VIP: append here
        pass
    
    @staticmethod
    def isHAProxyRunning():
        cmd = 'ps aux | grep haproxy | grep -v grep | wc -l'
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == '0' :
            return False
        else :
            return True
        
    @staticmethod
    def isKeepalivedRunning():
        cmd = 'ps aux | grep keepalived | grep -v grep | wc -l'
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == '0' :
            return False
        else :
            return True
    
    @staticmethod
    def getIndex(): #get host index, the ips has been sorted ascended.
        print 'To get this host index of role %s==============' % "keystone" 
        keystone_ips = JSONUtility.getValue('keystone_ips')
        keystone_ip_list = keystone_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'keystone_ip_list=%s--------------' % keystone_ip_list
        index = keystone_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if KeystoneHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            keystone_vip_interface = JSONUtility.getValue("keystone_vip_interface")
            keystone_vip = JSONUtility.getValue("keystone_vip")
            
            KeystoneHA.addVIP(keystone_vip, keystone_vip_interface)
            
            if KeystoneHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
#             KeystoneHA.deleteVIP(keystone_vip, keystone_vip_interface)
            
            if KeystoneHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            isMasterNode = KeystoneHA.isMasterNode()
            if isMasterNode == True :
                KeystoneHA.restart()
                pass
            else :
                KeystoneHA.deleteVIP(keystone_vip, keystone_vip_interface)
                pass
            pass
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('service haproxy restart')
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass


    
    
if __name__ == '__main__':
    print 'hello openstack-icehouse:initDB============'
    
    print 'start time: %s' % time.ctime()
    if debug :
        print 'debug====================='
        print 'debug#########'
        exit()
        pass
    
    #Produce params
    paramsProducerPath = os.path.join(PROJ_HOME_DIR, 'common', 'yaml', 'ParamsProducer.py')
    
    #Refactor
#     ShellCmdExecutor.execCmd('python %s' % paramsProducerPath)
        
    output, exitcode = ShellCmdExecutor.execCmd('cat /opt/mysql_ip_list')
    mysql_ip_list = output.strip().split(',')
    mysql_master_ip = mysql_ip_list[0]
    
    output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
    localIP = output.strip()
    
    if not localIP == mysql_master_ip :
        print 'This is not master mysql node,skip db init.............'
        exit()
        pass
    
    os.system('mkdir -p /opt/openstack_conf/tag/')
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/db_init'
    
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
            
            grantCmd1 = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            print 'grantCmd1=%s--' % grantCmd1
            grantCmd2 = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
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
            Keystone.install()
            ########
            Keystone.configConfFile()
             
            Keystone.importKeystoneDBSchema()
            #######
            Keystone.supportPKIToken()
                     
            Keystone.start()
            
            ####NEW
            Keystone.configureEnvVar()
            Keystone.sourceAdminOpenRC()####NEW
            Keystone.initKeystone()
            Keystone.sourceAdminOpenRC()
        
        #glance
        if YAMLUtil.hasRoleInNodes('glance') :
            print 'create glance mysql user============'
            createDBCmd = 'CREATE DATABASE glance'
            MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            grantCmd1 = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
            grantCmd2 = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
#             grantToHostname = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
#             .format(hostname=hostname,init_passwd=initPasswd)
            
            MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
            MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
#             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
#             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            #Refactor
            print 'glance db init test=============='
            exit()
            
            Glance.install()
            Glance.configConfFile()
            
            Keystone.sourceAdminOpenRC()
            Glance.initGlance()
        
        #nova
        if YAMLUtil.hasRoleInNodes('nova-api') :
            createDBCmd = 'CREATE DATABASE nova'
            MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            grantCmd1 = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
            grantCmd2 = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
#             grantToHostname = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
#             .format(hostname=hostname,init_passwd=initPasswd)
            
            MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
            MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
#             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
#             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            exit()
            
            ##nova
            Nova.install()
            ShellCmdExecutor.execCmd('chmod 777 /etc/nova')
            Nova.configConfFile()
            
            Keystone.sourceAdminOpenRC()
            Nova.initNova()
        
        #neutron
        if True : #YAMLUtil.hasRoleInNodes('neutron-server') :
            createDBCmd = 'CREATE DATABASE neutron'
            MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            grantCmd1 = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
            grantCmd2 = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
#             grantToHostname = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
#             .format(hostname=hostname,init_passwd=initPasswd)
            
            MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
#             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
#             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            #Refactor
            exit()
            
            Keystone.sourceAdminOpenRC()
            Neutron.initNeutron()
        
        #cinder
        if True :#YAMLUtil.hasRoleInNodes('cinder-api') :
            createDBCmd = 'CREATE DATABASE cinder'
            MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            grantCmd1 = 'GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
            grantCmd2 = 'GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
#             grantToHostname = 'GRANT ALL PRIVILEGES ON keystone.* TO \'cinder\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
#             .format(hostname=hostname,init_passwd=initPasswd)
            
            MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
            MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
#             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
#             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            #Refactor
            exit()
            
            ####Special handling
            if os.path.isfile('/etc/cinder') :
                ShellCmdExecutor.execCmd("rm -rf /etc/cinder")
                pass
            
            ShellCmdExecutor.execCmd("yum remove openstack-cinder -y")
            ##########
            
            Cinder.install()
            Cinder.configConfFile()
            
            Keystone.sourceAdminOpenRC()
            Cinder.initCinder()
            pass
        
        #ceilometer
        if YAMLUtil.hasRoleInNodes('ceilometer') :
            Ceilometer.initCeilometer()
            pass
            
        
        #heat
        if YAMLUtil.hasRoleInNodes('heat') :
            createDBCmd = 'CREATE DATABASE heat'
            MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            grantCmd1 = 'GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
            grantCmd2 = 'GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
            .format(init_passwd=initPasswd)
            
#             grantToHostname = 'GRANT ALL PRIVILEGES ON keystone.* TO \'heat\'@\'{hostname}\' IDENTIFIED BY \'{init_passwd}\''\
#             .format(hostname=hostname,init_passwd=initPasswd)
            
            MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)         
            MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
            MySQL.execMySQLCmd(user, initPasswd, flushCmd)
#             MySQL.execMySQLCmd(user, initPasswd, grantToHostname)
#             MySQL.execMySQLCmd(user, initPasswd, flushCmd)
            
            Heat.install()
            heatConfDir = '/etc/heat'
            if os.path.exists(heatConfDir) :
                ShellCmdExecutor.execCmd('chmod 777 %s' % heatConfDir)
                pass
            Heat.configConfFile()
            
            Keystone.sourceAdminOpenRC()
            Heat.initHeat()
          
        ShellCmdExecutor.execCmd('service haproxy restart')
        
        #destroy
        killKeystoneCmd = 'ps aux |grep python | grep keystone | awk \'{print "kill -9 " $2}\' | bash'
        killGlanceCmd   = 'ps aux |grep python | grep glance | awk \'{print "kill -9 " $2}\' | bash'
        killNovaCmd   = 'ps aux |grep python | grep nova | awk \'{print "kill -9 " $2}\' | bash'
        killNeutronCmd   = 'ps aux |grep python | grep neutron | awk \'{print "kill -9 " $2}\' | bash'
         
        ShellCmdExecutor.execCmd(killKeystoneCmd)
        ShellCmdExecutor.execCmd(killGlanceCmd)
        ShellCmdExecutor.execCmd(killNovaCmd)
        ShellCmdExecutor.execCmd(killNeutronCmd)
        
        #mark: db is initted
        
        os.system('touch %s' % INSTALL_TAG_FILE)
        print 'hello openstack is initted#######'
        pass

