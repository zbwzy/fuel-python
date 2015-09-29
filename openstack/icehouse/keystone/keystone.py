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
    def configConfFile():
        print "configure keystone conf file======"
        mysql_vip = JSONUtility.getValue("mysql_vip")
        keystone_vip = JSONUtility.getValue("keystone_vip")
        
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
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('sudo cat %s' % local_ip_file_path)
        localIP = output.strip()
        print 'localip=%s--' % localIP
        
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<LOCAL_IP>', localIP)
#         FileUtil.replaceByRegularExpression(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        
        FileUtil.replaceFileContent(keystone_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(keystone_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keystone_conf_file_path)
        print "configure keystone conf file done####"
        pass
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
    def install():
        if debug == True :
            print "DEBUG is True.On local dev env, do test==="
            yumCmd = "ls -lt"
            pass
        else :
            yumCmd = "yum install keepalived haproxy -y"
            pass
        
        ShellCmdExecutor.execCmd(yumCmd)    
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
        keystoneHAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (keystoneHAProxyTemplateFilePath, haproxyConfFilePath))
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        keystone_ips = JSONUtility.getValue("keystone_ips")
        keystone_ip_list = keystone_ips.strip().split(',')
        
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
        
        FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_ADMIN_API_SERVER_LIST>', keystoneAdminAPIServerListContent)
        FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_PUBLIC_API_SERVER_LIST>', keystonePublicAPIServerListContent)
        
        FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_VIP>', keystone_vip)
        
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
  router_id glance-<KEYSTONE_INDEX>
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
        #Refactor later
        GLANCE_WEIGHT = 300
        if GLANCE_WEIGHT == 300 : #This is MASTER
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_INDEX>', '1')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_WEIGHT>', '300')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<KEYSTONE_STATE>', 'MASTER')
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', keystone_vip_interface)
            FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', keystone_vip)
        else :
            #
            #
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
    
    #
#     Keystone.install()
#     Keystone.configConfFile()
#     Keystone.start()
    
    #add HA
    KeystoneHA.install()
    KeystoneHA.configure()
    KeystoneHA.start()
    print 'hello openstack-icehouse:keystone#######'
    pass

