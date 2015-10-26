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

debug = True
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

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

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
        template_string = 'export OS_SERVICE_ENDPOINT=http://<LOCAL_IP>:35357/v2.0'
        localIP = Keystone.getLocalIP()
        cmd = template_string.replace('<LOCAL_IP>', localIP)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def initKeystone():
        keystoneInitScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'keystone_init.sh')
        print 'keystoneInitScriptPath=%s' % keystoneInitScriptPath
#         os.system('bash %s' % keystoneInitScriptPath)

        if os.path.exists('/opt/keystone_init.sh') :
            ShellCmdExecutor.execCmd('sudo rm -rf /opt/keystone_init.sh')
            pass
        
        ShellCmdExecutor.execCmd('cp -rf %s /opt/' % keystoneInitScriptPath)
        
        localIP = Keystone.getLocalIP()
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<LOCAL_IP>', localIP)
        
        keystoneAdminEmail = JSONUtility.getValue("keystone_admin_email")
        print 'keystoneAdminEmail=%s' % keystoneAdminEmail
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<KEYSTONE_ADMIN_EMAIL>', keystoneAdminEmail)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        FileUtil.replaceFileContent('/opt/keystone_init.sh', '<KEYSTONE_VIP>', keystone_vip)
        ShellCmdExecutor.execCmd('bash /opt/keystone_init.sh')
        pass
        ##
        
    @staticmethod
    def sourceAdminOpenRC():
        adminOpenRCScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'admin_openrc.sh')
        print 'adminOpenRCScriptPath=%s' % adminOpenRCScriptPath
        
        ShellCmdExecutor.execCmd('cp -rf %s /opt/' % adminOpenRCScriptPath)
        
        FileUtil.replaceFileContent('/opt/admin_openrc.sh', '<LOCAL_IP>', Keystone.getLocalIP())
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
        
        os.system("sudo cp -rf %s %s" % (SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH, keystoneConfDir))
        
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
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('sudo cat %s' % local_ip_file_path)
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
                
                ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (haproxyTemplateFilePath, haproxyConfFilePath))
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
            ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (keystoneHAProxyTemplateFilePath, haproxyConfFilePath))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        ####
        keystoneFrontendStringTemplate = '''
frontend keystone-admin-vip
    bind <KEYSTONE_VIP>:35357
    default_backend keystone-admin-api

frontend keystone-public-vip
    bind <KEYSTONE_VIP>:5000
    default_backend keystone-public-api
'''
        keystoneFrontendString = keystoneFrontendStringTemplate.replace('<KEYSTONE_VIP>', keystone_vip)
        print 'keystoneFrontendString=%s--' % keystoneFrontendString
        
        ####
        keystone_ips = JSONUtility.getValue("keystone_ips")
        keystone_ip_list = keystone_ips.strip().split(',')
        
        keystoneBackendAdminApiStringTemplate = '''
backend keystone-admin-api
    balance roundrobin
    <KEYSTONE_ADMIN_API_SERVER_LIST>
        '''
        
        keystoneBackendPublicApiStringTemplate = '''
backend keystone-public-api
    balance roundrobin
    <KEYSTONE_PUBLIC_API_SERVER_LIST>
        '''
        
        serverKeystoneAdminAPIBackendTemplate   = 'server keystone-<INDEX> <SERVER_IP>:35357 check inter 10s'
        serverKeystonePublicAPIBackendTemplate  = 'server keystone-<INDEX> <SERVER_IP>:5000 check inter 10s'
        
        keystoneAdminAPIServerListContent = ''
        keystonePublicAPIServerListContent = ''
        
        index = 1
        for keystone_ip in keystone_ip_list:
            print 'keystone_ip=%s' % keystone_ip
            keystoneAdminAPIServerListContent += serverKeystoneAdminAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            keystonePublicAPIServerListContent += serverKeystonePublicAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            
            keystoneAdminAPIServerListContent += '\n'
            keystoneAdminAPIServerListContent += '    '
            
            keystonePublicAPIServerListContent += '\n'
            keystonePublicAPIServerListContent += '    '
            index += 1
            pass
        
        keystoneAdminAPIServerListContent = keystoneAdminAPIServerListContent.strip()
        keystonePublicAPIServerListContent = keystonePublicAPIServerListContent.strip()
        print 'keystoneAdminAPIServerListContent=%s--' % keystoneAdminAPIServerListContent
        print 'keystonePublicAPIServerListContent=%s--' % keystonePublicAPIServerListContent
        
        keystoneBackendAdminApiString = keystoneBackendAdminApiStringTemplate.replace('<KEYSTONE_ADMIN_API_SERVER_LIST>', keystoneAdminAPIServerListContent)
        keystoneBackendPublicApiString = keystoneBackendPublicApiStringTemplate.replace('<KEYSTONE_PUBLIC_API_SERVER_LIST>', keystonePublicAPIServerListContent)
        
        print 'keystoneBackendAdminApiString=%s--' % keystoneBackendAdminApiString
        print 'keystoneBackendPublicApiString=%s--' % keystoneBackendPublicApiString
        
        #append
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (keystoneFrontendString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (keystoneBackendAdminApiString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (keystoneBackendPublicApiString, haproxyConfFilePath))
        
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_ADMIN_API_SERVER_LIST>', keystoneAdminAPIServerListContent)
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_PUBLIC_API_SERVER_LIST>', keystonePublicAPIServerListContent)
#         
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_VIP>', keystone_vip)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)
        pass
    
    @staticmethod
    def configureKeepalived():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        ###################configure keepalived
        keepalivedTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'keepalived.conf')
        keepalivedConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEEPALIVED_CONF_FILE_PATH')
        print 'keepalivedConfFilePath=%s' % keepalivedConfFilePath
        if not os.path.exists('/etc/keepalived') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/keepalived')
            pass
        
        #configure haproxy check script in keepalived
        checkHAProxyScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
        ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (checkHAProxyScriptPath, '/etc/keepalived'))
        
        ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (keepalivedTemplateFilePath, keepalivedConfFilePath))
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
        #Call ZooKeeper lock & counter services
        keystone_weight_counter = Keystone.getWeightCounter()
        if keystone_weight_counter == 300 : #This is MASTER
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_INDEX>', '1')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_WEIGHT>', '300')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_STATE>', 'MASTER')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', keystone_vip_interface)
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', keystone_vip)
        else :
            index = 301 - keystone_weight_counter

            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_INDEX>', str(index))
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_WEIGHT>', str(keystone_weight_counter))
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_STATE>', 'SLAVE')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', keystone_vip_interface)
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', keystone_vip)
            pass
        
        ##temporary: if current user is not root
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keepalivedConfFilePath)
        
        #If keepalived need to support more VIP: append here
        pass
    
    @staticmethod
    def start():
        if debug == True :
            print "DEBUG=True.On local dev env, do test===="
            pass
        else :
            ShellCmdExecutor.execCmd('service haproxy start')
            ShellCmdExecutor.execCmd('service keepalived start')
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('service haproxy restart')
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    


if __name__ == '__main__':
    
    print 'hello openstack-icehouse:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /etc/puppet/localip, these two files are generated in init.pp in site.pp.
    argv = sys.argv
    argv.pop(0)
    print "agrv=%s--" % argv
    LOCAL_IP = ''
    if len(argv) > 0 :
        LOCAL_IP = argv[0]
        pass
    else :
        print "ERROR:no params."
        pass
    
    ###############################
    INSTALL_TAG_FILE = '/opt/keystone_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'keystone installed####'
        print 'exit===='
        exit()
        pass
        
    print 'start to install======='
    Prerequisites.prepare()
#     Keystone.install()
#     Keystone.configConfFile()
#          
#     if Keystone.isMasterNode()  == True :
#         Keystone.importKeystoneDBSchema()
#         Keystone.supportPKIToken()
#         pass
#          
#     Keystone.start()
#        
#     if Keystone.isMasterNode() == True :
#         Keystone.configureEnvVar()
#         Keystone.initKeystone()
#         Keystone.sourceAdminOpenRC()
#         pass
       
    #add HA
    KeystoneHA.install()
    KeystoneHA.configure()
    KeystoneHA.start()
    
    #mark: keystone is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:keystone#######'
    pass

