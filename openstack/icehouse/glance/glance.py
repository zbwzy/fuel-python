'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python glance.py

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
SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-api.conf')
SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-registry.conf')

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
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
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
            os.system("sudo mkdir -p %s" % glanceConfDir)
            pass
        #if exist, remove original conf files
        if os.path.exists(glance_api_conf_file_path) :
            os.system("sudo rm -rf %s" % glance_api_conf_file_path)
            pass
        
        if os.path.exists(glance_registry_conf_file_path) :
            print 'tttttttt====='
            print 'glance_registry_conf_file_path=%s' % glance_registry_conf_file_path
            os.system("sudo rm -rf %s" % glance_registry_conf_file_path)
            pass
        
        os.system("sudo cp -rf %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        os.system("sudo cp -rf %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_registry_conf_file_path)
        ###########LOCAL_IP:retrieve it from one file, the LOCAL_IP file is generated when this project inits.
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('sudo cat %s' % local_ip_file_path)
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
    pass

class GlanceHA(object):
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
            if not GlanceHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not GlanceHA.isHAProxyInstalled() :
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
        GlanceHA.configureHAProxy()
#         GlanceHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        #server glance-01 192.168.1.137:9191 check inter 10s
        glance_vip = JSONUtility.getValue("glance_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        glanceHAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (glanceHAProxyTemplateFilePath, haproxyConfFilePath))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        #####
        glanceFrontendStringTemplate = '''
frontend glance-vip
    bind <GLANCE_VIP>:9292
    default_backend glance-api

frontend glance-registry-vip
    bind <GLANCE_REGISTRY_VIP>:9191
    default_backend glance-registry-api
        '''
        
        glanceFrontendString = glanceFrontendStringTemplate.replace('<GLANCE_VIP>', glance_vip)
        glanceFrontendString = glanceFrontendString.replace('<GLANCE_REGISTRY_VIP>', glance_vip)
        
        print 'glanceFrontendString=%s--' % glanceFrontendString
        
        #####
        glance_ips = JSONUtility.getValue("glance_ips")
        glance_ip_list = glance_ips.strip().split(',')
        
        serverGlanceRegistryAPIBackendTemplate = 'server glance-<INDEX> <SERVER_IP>:9191 check inter 10s'
        serverGlanceAPIBackendTemplate         = 'server glance-<INDEX> <SERVER_IP>:9292 check inter 10s'
        
        glanceRegistryAPIServerListContent = ''
        glanceAPIServerListContent = ''
        
        index = 1
        for glance_ip in glance_ip_list:
            print 'glance_ip=%s' % glance_ip
            glanceRegistryAPIServerListContent += serverGlanceRegistryAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            glanceAPIServerListContent += serverGlanceAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            
            glanceRegistryAPIServerListContent += '\n'
            glanceRegistryAPIServerListContent += '    '
            
            glanceAPIServerListContent += '\n'
            glanceAPIServerListContent += '    '
            
            index += 1
            pass
        
        glanceRegistryAPIServerListContent = glanceRegistryAPIServerListContent.strip()
        glanceAPIServerListContent = glanceAPIServerListContent.strip()
        print 'glanceRegistryAPIServerListContent=%s--' % glanceRegistryAPIServerListContent
        print 'glanceAPIServerListContent=%s--' % glanceAPIServerListContent
        
        glanceBackendRegistryApiStringTemplate = '''
backend glance-registry-api
    balance roundrobin
    <GLANCE_REGISTRY_API_SERVER_LIST>
        '''
        
        glanceBackendApiStringTemplate = '''
backend glance-api
    balance roundrobin
    <GLANCE_API_SERVER_LIST>
        '''
        
        glanceBackendRegistryApiString = glanceBackendRegistryApiStringTemplate.replace('<GLANCE_REGISTRY_API_SERVER_LIST>', glanceRegistryAPIServerListContent)
        
        glanceBackendApiString = glanceBackendApiStringTemplate.replace('<GLANCE_API_SERVER_LIST>', glanceAPIServerListContent)
        #append
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (glanceFrontendString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (glanceBackendRegistryApiString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (glanceBackendApiString, haproxyConfFilePath))
        
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<GLANCE_REGISTRY_API_SERVER_LIST>', glanceRegistryAPIServerListContent)
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<GLANCE_API_SERVER_LIST>', glanceAPIServerListContent)
        
        #Default: glance-api & glance-registry-api use the same vip
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<GLANCE_REGISTRY_VIP>', glance_vip)
#         FileUtil.replaceFileContent(haproxyConfFilePath, '<GLANCE_VIP>', glance_vip)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)
        pass
    
    @staticmethod
    def configureKeepalived():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        ###################configure keepalived
        glanceKeepalivedTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'keepalived.conf')
        keepalivedConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEEPALIVED_CONF_FILE_PATH')
        print 'keepalivedConfFilePath=%s' % keepalivedConfFilePath
        if not os.path.exists('/etc/keepalived') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/keepalived')
            pass
        
        #configure haproxy check script in keepalived
        checkHAProxyScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
        print 'checkHAProxyScriptPath=%s===========================---' % checkHAProxyScriptPath
        ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (checkHAProxyScriptPath, '/etc/keepalived'))
        
        ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (glanceKeepalivedTemplateFilePath, keepalivedConfFilePath))
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keepalivedConfFilePath)
        ##configure
        '''keepalived template====
        global_defs {
  router_id glance-<GLANCE_INDEX>
}
vrrp_script chk_haproxy {
   script "/etc/keepalived/check_haproxy.sh"
   interval 2
   weight  2
}

vrrp_instance 42 {
  virtual_router_id 42
  # for electing MASTER, highest priority wins.
  priority  <GLANCE_WEIGHT>
  state     <GLANCE_STATE>
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
        glance_vip = JSONUtility.getValue("glance_vip")
        glance_vip_interface = JSONUtility.getValue("glance_vip_interface")
        #Refactor later
        GLANCE_WEIGHT = 300
        if GLANCE_WEIGHT == 300 : #This is MASTER
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<GLANCE_INDEX>', '1')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<GLANCE_WEIGHT>', '300')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<GLANCE_STATE>', 'MASTER')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', glance_vip_interface)
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', glance_vip)
        else :
            #
            #
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<GLANCE_STATE>', 'SLAVE')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', glance_vip_interface)
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', glance_vip)
            pass
        
        ##temporary: if current user is not root
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keepalivedConfFilePath)
        
        #If keepalived need to support more VIP: append here
        pass
    
    @staticmethod
    def start():
        if debug == True :
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
    
    print 'hello openstack-icehouse:glance============'
    
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
    
    INSTALL_TAG_FILE = '/opt/glance_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'glance installed####'
        print 'exit===='
        exit()
        pass
        
    print 'start to install======='
    
    Prerequisites.prepare()
    #
    Glance.install()
    Glance.configConfFile()
    Glance.start()
    
    #add HA
    GlanceHA.install()
    GlanceHA.configure()
    GlanceHA.start()
    
    #mark: glance is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    
    print 'hello openstack-icehouse:glance#######'
    pass

