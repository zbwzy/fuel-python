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
        
        ShellCmdExecutor.execCmd('chmod 777 /etc/keystone')
        
#         os.system("sudo cp -r %s %s" % (SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH, keystoneConfDir))
        ###NEW
        ShellCmdExecutor.execCmd('cat %s > /tmp/keystone.conf' % SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH)
        ShellCmdExecutor.execCmd('mv /tmp/keystone.conf /etc/keystone')
        ShellCmdExecutor.execCmd('rm -rf /tmp/keystone.conf')
        
        
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
        keystone_ip_list = keystone_ips.strip().split(',')
        
        serverKeystoneAdminAPIBackendTemplate   = 'server keystone-<INDEX> <SERVER_IP>:35357 check inter 2000 rise 2 fall 5'
        serverKeystonePublicAPIBackendTemplate  = 'server keystone-<INDEX> <SERVER_IP>:5000 check inter 2000 rise 2 fall 5'
        
        keystoneAdminAPIServerListContent = ''
        keystonePublicAPIServerListContent = ''
        
        index = 1
        for keystone_ip in keystone_ip_list:
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
    
    print 'hello openstack-icehouse:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
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
    Keystone.install()
    Keystone.configConfFile()
          
#     if Keystone.isMasterNode()  == True :
#         Keystone.importKeystoneDBSchema()
#         Keystone.supportPKIToken()
#         pass
          
    Keystone.start()
        
#     if Keystone.isMasterNode() == True :
#         Keystone.configureEnvVar()
#         Keystone.initKeystone()
#         pass
    Keystone.sourceAdminOpenRC()
    #add HA
    KeystoneHA.install()
    KeystoneHA.configure()
    KeystoneHA.start()
    
    #mark: keystone is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:keystone#######'
    pass

