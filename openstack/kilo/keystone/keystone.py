'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python keystone.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time

reload(sys)
sys.setdefaultencoding('utf8')

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
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from openstack.common.serverSequence import ServerSequence
from openstack.kilo.ssh.SSH import SSH

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
        Network.stopIPTables()
        Network.stopNetworkManager()
        pass
    
    @staticmethod
    def stopIPTables():
        stopCmd = "service iptables stop"
        ShellCmdExecutor.execCmd(stopCmd)
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
            yumCmd = "yum install openstack-keystone httpd mod_wsgi python-openstackclient python-memcached -y"
            
        ShellCmdExecutor.execCmd(yumCmd)
#         Keystone.configConfFile()
#         Keystone.start()
        
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
        ShellCmdExecutor.execCmd(cmd0)
        
        if not os.path.exists('/var/log/keystone') :
            os.system('mkdir -p /var/log/keystone')
            pass
        
        if not os.path.exists('/etc/keystone/ssl') :
            os.system('mkdir -p /etc/keystone/ssl')
            pass
        
        cmd1 = 'chown -R keystone:keystone /var/log/keystone'
        cmd2 = 'chown -R keystone:keystone /etc/keystone/ssl'
        cmd3 = 'chmod -R o-rwx /etc/keystone/ssl'
        ShellCmdExecutor.execCmd(cmd1)
        ShellCmdExecutor.execCmd(cmd2)
        ShellCmdExecutor.execCmd(cmd3)
        pass
    
    @staticmethod
    def httpConf():
        wsgi_keystone_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'wsgi-keystone.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/httpd/conf.d/' % wsgi_keystone_conf_file_path)
        pass
    
    @staticmethod
    def startHttp():
        ShellCmdExecutor.execCmd('systemctl enable httpd.service')
        ShellCmdExecutor.execCmd('systemctl start httpd.service')
        pass
    
    @staticmethod
    def installWSGI():
        ShellCmdExecutor.execCmd('mkdir -p /var/www/cgi-bin/keystone')
        main_python_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'main')
        ShellCmdExecutor.execCmd('cp -r %s /var/www/cgi-bin/keystone' % main_python_file_path)
        ShellCmdExecutor.execCmd('cp /var/www/cgi-bin/keystone/main /var/www/cgi-bin/keystone/admin')
        ShellCmdExecutor.execCmd('chown -R keystone:keystone /var/www/cgi-bin/keystone')
        ShellCmdExecutor.execCmd('chmod 755 /var/www/cgi-bin/keystone/*')
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
        admin_token = JSONUtility.getValue("admin_token")
        #memcache service list
        keystone_ips_string = JSONUtility.getValue("keystone_ips")
        keystone_ip_list = keystone_ips_string.split(',')
        memcached_service_list = []
        for ip in keystone_ip_list:
            memcached_service_list.append(ip.strip() + ':11211')
            pass
        
        memcached_service_string = ','.join(memcached_service_list)
        print 'memcached_service_string=%s--' % memcached_service_string
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        keystoneConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEYSTONE_CONF_DIR')
        
        keystone_conf_file_path = os.path.join(keystoneConfDir, 'keystone.conf')
        
        if not os.path.exists(keystoneConfDir) :
            os.system("sudo mkdir -p %s" % keystoneConfDir)
            pass
        
        ShellCmdExecutor.execCmd("cp -r %s %s" % (SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH, keystoneConfDir))
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keystone_conf_file_path)
#         #if exist, remove original conf files
#         if os.path.exists(keystone_conf_file_path) :
#             os.system("sudo rm -rf %s" % keystone_conf_file_path)
#             pass
#         
#         ShellCmdExecutor.execCmd('chmod 777 /etc/keystone')
#         
# #         os.system("sudo cp -r %s %s" % (SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH, keystoneConfDir))
#         ###NEW
#         ShellCmdExecutor.execCmd('cat %s > /tmp/keystone.conf' % SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH)
#         ShellCmdExecutor.execCmd('mv /tmp/keystone.conf /etc/keystone/')
#         
#         ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keystone_conf_file_path)
        ###########LOCAL_IP:retrieve it from one file, the LOCAL_IP file is generated when this project inits.
        localIP = Keystone.getLocalIP()
        print 'localip=%s--' % localIP
        
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<LOCAL_IP>', localIP)
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        keystoneDbPass = JSONUtility.getValue('keystone_dbpass')
        FileUtil.replaceFileContent(keystone_conf_file_path, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<LOCAL_MANAGEMENT_IP>', localIP)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<KEYSTONE_DBPASS>', keystoneDbPass)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MEMCACHED_LIST>', memcached_service_string)
        
        ShellCmdExecutor.execCmd("chmod 644 %s" % keystone_conf_file_path)
        print "configure keystone conf file done####"
        pass
    
    @staticmethod
    def getLocalIP():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        return localIP
    
    @staticmethod
    def getServerIndex():
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        local_management_ip = output.strip()
        keystone_ips = JSONUtility.getValue('keystone_ips')
        keystone_ip_list = keystone_ips.split(',')
        index = ServerSequence.getIndex(keystone_ip_list, local_management_ip)
        return index
    
    @staticmethod
    def getLaunchedRDBServersNum():
        cmd = 'ls -lt /opt/openstack_conf/tag/ | grep bcrdb_ | wc -l' 
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        launchedRdbNum = output.strip()
        return launchedRdbNum
    

if __name__ == '__main__':
    
    print 'hello openstack-icehouse:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/keystone_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'keystone installed####'
        print 'exit===='
        pass
    else :
        print 'start to install======='
#         Prerequisites.prepare()
        Keystone.install()
        Keystone.configConfFile()
        
        
        if Keystone.getServerIndex() == 0 :
            Keystone.supportPKIToken()
            pass
        else :
            ##scp /etc/keystone/ssl from first keystone.
            pass
        
        ####only when rdb cluster is prepared, then import keystone db schema.
        if Keystone.getServerIndex() == 0 :
            TIMEOUT = 3600
            timeout = TIMEOUT
            time_count = 0
            print 'test timeout==='
            while True:
                launchedMysqlServerNum = Keystone.getLaunchedRDBServersNum()
                mysql_ips = JSONUtility.getValue('mysql_ips')
                mysql_ip_list = mysql_ips.split(',')
                if  str(launchedMysqlServerNum) == str(len(mysql_ip_list)) :
                    print 'wait time: %s second(s).' % time_count
                    Keystone.importKeystoneDBSchema()
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                
                if time_count == timeout :
                    print 'Do nothing!timeout=%s.' % timeout
                    break
                pass
            pass
        
        Keystone.httpConf()
        
        Keystone.installWSGI()
        
        Keystone.startHttp()
        
        if Keystone.getServerIndex() == 0 :
            from openstack.kilo.keystone.initKeystone import InitKeystone
            InitKeystone.init()
            
            tag_file_name = 'keystone0_launched'
            from common.yaml.YAMLUtil import YAMLUtil
            #send to first glance
            if YAMLUtil.hasRoleInNodes('glance'):
                glance_ips = JSONUtility.getValue('glance_ips')
                glance_ip_list = glance_ips.split(',')
                SSH.sendTagTo(glance_ip_list[0], tag_file_name)
            
            #send to first neutron-server
            if YAMLUtil.hasRoleInNodes('neutron-server'):
                neutron_ips = JSONUtility.getValue('neutron_ips')
                neutron_ip_list = neutron_ips.split(',')
                SSH.sendTagTo(neutron_ip_list[0], tag_file_name)
            
            #send to first nova-api
            if YAMLUtil.hasRoleInNodes('nova-api'):
                nova_ips = JSONUtility.getValue('nova_ips')
                nova_ip_list = nova_ips.split(',')
                SSH.sendTagTo(nova_ip_list[0], tag_file_name)
                
            #send to first cinder
            if YAMLUtil.hasRoleInNodes('cinder'):
                cinder_ips = JSONUtility.getValue('cinder_ips')
                cinder_ip_list = cinder_ips.split(',')
                SSH.sendTagTo(cinder_ip_list[0], tag_file_name)
                
            pass
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        #mark: keystone is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:keystone#######'
    pass

