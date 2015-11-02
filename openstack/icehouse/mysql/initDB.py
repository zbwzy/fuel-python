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

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

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
    def initPassword(user, initPasswd):
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
    
class VIP(object):
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
        if VIP.isExistVIP(vip, interface) :
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
        result = VIP.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not VIP.isExistVIP(vip, interface) :
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
        result = VIP.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if VIP.isExistVIP(vip, interface) :
            deleteVIPCmd = 'ip addr delete {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'deleteVIPCmd=%s--' % deleteVIPCmd
            ShellCmdExecutor.execCmd(deleteVIPCmd)
            pass
        else :
            print 'The VIP %s does not exist on interface %s.' % (vip, interface)
            pass
        pass

class Network(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def Prepare():
#         Network.stopIPTables()
        Network.stopNetworkManager()
        pass
    
    @staticmethod
    def stopNetworkManager():
        stopCmd = "service NetworkManager stop"
        chkconfigOffCmd = "chkconfig NetworkManager off"
        
        ShellCmdExecutor.execCmd(stopCmd)
        ShellCmdExecutor.execCmd(chkconfigOffCmd)
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
        importCmd = 'su -s /bin/sh -c "keystone-manage db_sync" keystone'
        ShellCmdExecutor.execCmd(importCmd)
        pass
    
    @staticmethod
    def supportPKIToken():
        cmd1 = 'keystone-manage pki_setup --keystone-user keystone --keystone-group keystone'
        cmd2 = 'chown -R keystone:keystone /etc/keystone/ssl'
        cmd3 = 'chmod -R o-rwx /etc/keystone/ssl'
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
        
        localIP = Keystone.getLocalIP()
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<LOCAL_IP>', localIP)
        
        keystoneAdminEmail = JSONUtility.getValue("admin_email")
        print 'keystoneAdminEmail=%s' % keystoneAdminEmail
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<ADMIN_EMAIL>', keystoneAdminEmail)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<KEYSTONE_VIP>', keystone_vip)
        ShellCmdExecutor.execCmd('bash /opt/keystone_init.sh')
        pass
        ##
        
    @staticmethod
    def sourceAdminOpenRC():
        adminOpenRCScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'admin_openrc.sh')
        print 'adminOpenRCScriptPath=%s' % adminOpenRCScriptPath
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % adminOpenRCScriptPath)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        FileUtil.replaceFileContent('/opt/admin_openrc.sh', '<KEYSTONE_VIP>', keystone_vip)
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
            ShellCmdExecutor.execCmd("sudo mkdir -p %s" % keystoneConfDir)
            pass
        #if exist, remove original conf files
        if os.path.exists(keystone_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % keystone_conf_file_path)
            pass
        
        print 'vvvvvvvvvvvvvvvvvvvvvvv=%s----' % SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH
        ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH, keystoneConfDir))
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keystone_conf_file_path)
        ###########LOCAL_IP:retrieve it from one file, the LOCAL_IP file is generated when this project inits.
        localIP = Keystone.getLocalIP()
        print 'localip=%s--' % localIP
        
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<LOCAL_IP>', localIP)
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        
        FileUtil.replaceFileContent(keystone_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keystone_conf_file_path)
        print "configure keystone conf file done####"
        pass
    
    @staticmethod
    def getLocalIP():
        local_ip_file_path = '/opt/localip'
#         openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
#         local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        localIP = ''
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        return localIP
    
    @staticmethod
    def getWeightCounter():
        print 'refactor later================'
        print 'get keystone weight=================='
        return 300
    
    @staticmethod
    def isMasterNode():
        print 'go into Master======'
        if Keystone.getWeightCounter() == 300 :
            return True
        else :
            return False
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
        
        ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_registry_conf_file_path)
        ###########LOCAL_IP:retrieve it from one file, the LOCAL_IP file is generated when this project inits.
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        print 'localip=%s--' % localIP
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<LOCAL_IP>', localIP)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        
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
        
        localIP = Keystone.getLocalIP()
        
        glanceAdminEmail = JSONUtility.getValue("admin_email")
        print 'glanceAdminEmail=%s' % glanceAdminEmail
        FileUtil.replaceFileContent('/opt/glance_init.sh', '<ADMIN_EMAIL>', glanceAdminEmail)
        
        glance_vip = JSONUtility.getValue("glance_vip")
        FileUtil.replaceFileContent('/opt/glance_init.sh', '<GLANCE_VIP>', glance_vip)
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
        
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (nova_api_conf_template_file_path, novaConfDir))
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
        FileUtil.replaceFileContent(nova_conf_file_path, '<NEUTRON_SERVER_VIP>', localIP)
        
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
        
        localIP = Keystone.getLocalIP()
        
        novaAdminEmail = JSONUtility.getValue("admin_email")
        print 'novaAdminEmail=%s' % novaAdminEmail
        FileUtil.replaceFileContent('/opt/nova_init.sh', '<ADMIN_EMAIL>', novaAdminEmail)
        
        nova_api_vip = JSONUtility.getValue("nova_api_vip")
        FileUtil.replaceFileContent('/opt/nova_init.sh', '<NOVA_API_VIP>', nova_api_vip)
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
        
        neutron_server_vip = JSONUtility.getValue("neutron_server_vip")
        FileUtil.replaceFileContent('/opt/neutron_init.sh', '<NEUTRON_SERVER_VIP>', neutron_server_vip)
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
        
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (cinder_conf_template_file_path, cinderConfDir))
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
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        cinderAdminEmail = JSONUtility.getValue("admin_email")
        print 'cinderAdminEmail=%s' % cinderAdminEmail
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<ADMIN_EMAIL>', cinderAdminEmail)
        
        cinder_vip = JSONUtility.getValue("cinder_vip")
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<CINDER_VIP>', cinder_vip)
        
        cinder_mysql_password = JSONUtility.getValue("cinder_mysql_password")
        FileUtil.replaceFileContent('/opt/cinder_init.sh', '<CINDER_MYSQL_PASSWORD>', cinder_mysql_password)
        
        ShellCmdExecutor.execCmd('bash /opt/cinder_init.sh')
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
        
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (heat_conf_template_file_path, heatConfDir))
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % heat_conf_file_path)
        
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
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        heatAdminEmail = JSONUtility.getValue("admin_email")
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<ADMIN_EMAIL>', heatAdminEmail)
        
        heat_vip = JSONUtility.getValue("heat_vip")
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<HEAT_VIP>', heat_vip)
        
        heat_mysql_password = JSONUtility.getValue("heat_mysql_password")
        FileUtil.replaceFileContent('/opt/heat_init.sh', '<HEAT_MYSQL_PASSWORD>', heat_mysql_password)
        
        ShellCmdExecutor.execCmd('bash /opt/heat_init.sh')
        pass
    pass

    
    
if __name__ == '__main__':
    debug = False
    print 'hello openstack-icehouse:glance============'
    
    print 'start time: %s' % time.ctime()
    if debug :
        print 'debug====================='
        
        print 'debug#########'
        exit()
    INSTALL_TAG_FILE = '/opt/db_init'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'openstack db is initted####'
        print 'exit===='
        exit()
        pass
        
    print 'start to init======='
    
    Prerequisites.prepare()
    
    #init mysql password
    user = 'root'
    initPasswd = JSONUtility.getValue('mysql_password')
    print 'initPasswd=%s--' % initPasswd
    MySQL.initPassword(user, initPasswd)
    
    
    print 'init============================================'
    #keystone
    if YAMLUtil.hasRoleInNodes('keystone') :
        createDBCmd = 'CREATE DATABASE keystone'
        MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
        
        grantCmd1 = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        print 'grantCmd1=%s--' % grantCmd1
        grantCmd2 = 'GRANT ALL PRIVILEGES ON keystone.* TO \'keystone\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
    
        
    #     ########
        Keystone.install()
        Keystone.configConfFile()
         
        Keystone.importKeystoneDBSchema()
        Keystone.supportPKIToken()
                 
        Keystone.start()
               
        Keystone.configureEnvVar()
        Keystone.initKeystone()
        Keystone.sourceAdminOpenRC()
    
    #glance
    if YAMLUtil.hasRoleInNodes('glance') :
        createDBCmd = 'CREATE DATABASE glance'
        MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
        
        grantCmd1 = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        grantCmd2 = 'GRANT ALL PRIVILEGES ON glance.* TO \'glance\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
        
        Glance.install()
        Glance.configConfFile()
        Glance.initGlance()
    
    #nova
    if YAMLUtil.hasRoleInNodes('nova-api') :
        createDBCmd = 'CREATE DATABASE nova'
        MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
        
        grantCmd1 = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        grantCmd2 = 'GRANT ALL PRIVILEGES ON nova.* TO \'nova\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
        
        ##nova
        Nova.install()
        Nova.configConfFile()
        Nova.initNova()
    
    #neutron
    if YAMLUtil.hasRoleInNodes('neutron-server') :
        createDBCmd = 'CREATE DATABASE neutron'
        MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
        
        grantCmd1 = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        grantCmd2 = 'GRANT ALL PRIVILEGES ON neutron.* TO \'neutron\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
        
        Neutron.initNeutron()
    
    #cinder
    if YAMLUtil.hasRoleInNodes('cinder-api') :
        createDBCmd = 'CREATE DATABASE cinder'
        MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
        
        grantCmd1 = 'GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        grantCmd2 = 'GRANT ALL PRIVILEGES ON cinder.* TO \'cinder\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
        
        Cinder.install()
        Cinder.configConfFile()
        Cinder.initCinder()
    
    #heat
    if YAMLUtil.hasRoleInNodes('heat') :
        createDBCmd = 'CREATE DATABASE heat'
        MySQL.execMySQLCmd(user, initPasswd, createDBCmd)
        
        grantCmd1 = 'GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'localhost\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        
        grantCmd2 = 'GRANT ALL PRIVILEGES ON heat.* TO \'heat\'@\'%\' IDENTIFIED BY \'{init_passwd}\''\
        .format(init_passwd=initPasswd)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd1)
        MySQL.execMySQLCmd(user, initPasswd, grantCmd2)
        
        Heat.install()
        Heat.configConfFile()
        Heat.initHeat()
      
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

