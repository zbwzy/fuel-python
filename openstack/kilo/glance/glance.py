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
#         rabbit_vip = JSONUtility.getValue("rabbit_vip")
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
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
        
#         os.system("sudo cp -r %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
#         os.system("sudo cp -r %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glanceConfDir)
        
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ######NEW
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/glance-api.conf" % SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH)
        ShellCmdExecutor.execCmd("cat %s > /tmp/glance-registry.conf" % SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH)
        
        ShellCmdExecutor.execCmd("mv /tmp/glance-api.conf /etc/glance/")
        ShellCmdExecutor.execCmd("mv /tmp/glance-registry.conf /etc/glance/")
        
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
        
#         FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_HOST>', rabbit_vip)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % glance_registry_conf_file_path)
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
        if GlanceHA.isExistVIP(vip, interface) :
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
        result = GlanceHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not GlanceHA.isExistVIP(vip, interface) :
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
        result = GlanceHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if GlanceHA.isExistVIP(vip, interface) :
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
                
                ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (haproxyTemplateFilePath, '/etc/haproxy'))
                pass
            pass
        pass
    
    @staticmethod
    def configure():
        GlanceHA.configureHAProxy()
        GlanceHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        glance_vip = JSONUtility.getValue("glance_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        glanceHAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (glanceHAProxyTemplateFilePath, '/etc/haproxy'))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        glance_ips = JSONUtility.getValue("glance_ips")
        glance_ip_list = glance_ips.strip().split(',')
        
        glanceBackendApiStringTemplate = '''
listen glance_api_cluster
  bind <GLANCE_VIP>:9292
  balance source
  <GLANCE_API_SERVER_LIST>
  '''
        glanceBackendRegistryApiStringTemplate = '''
listen glance_registry_cluster
  bind <GLANCE_VIP>:9191
  balance source
  <GLANCE_REGISTRY_API_SERVER_LIST>
        '''
        
        glanceBackendApiString = glanceBackendApiStringTemplate.replace('<GLANCE_VIP>', glance_vip)
        
        glanceBackendRegistryApiString = glanceBackendRegistryApiStringTemplate.replace('<GLANCE_VIP>', glance_vip)
        ###############
        
        serverGlanceRegistryAPIBackendTemplate = 'server glance-<INDEX> <SERVER_IP>:9191 check inter 2000 rise 2 fall 5'
        serverGlanceAPIBackendTemplate         = 'server glance-<INDEX> <SERVER_IP>:9292 check inter 2000 rise 2 fall 5'
        
        glanceRegistryAPIServerListContent = ''
        glanceAPIServerListContent = ''
        
        index = 1
        for glance_ip in glance_ip_list:
            print 'glance_ip=%s' % glance_ip
            glanceRegistryAPIServerListContent += serverGlanceRegistryAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            glanceAPIServerListContent += serverGlanceAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            
            glanceRegistryAPIServerListContent += '\n'
            glanceRegistryAPIServerListContent += '  '
            
            glanceAPIServerListContent += '\n'
            glanceAPIServerListContent += '  '
            
            index += 1
            pass
        
        glanceRegistryAPIServerListContent = glanceRegistryAPIServerListContent.strip()
        glanceAPIServerListContent = glanceAPIServerListContent.strip()
        print 'glanceRegistryAPIServerListContent=%s--' % glanceRegistryAPIServerListContent
        print 'glanceAPIServerListContent=%s--' % glanceAPIServerListContent
        
        glanceBackendRegistryApiString = glanceBackendRegistryApiString.replace('<GLANCE_REGISTRY_API_SERVER_LIST>', glanceRegistryAPIServerListContent)
        
        glanceBackendApiString = glanceBackendApiString.replace('<GLANCE_API_SERVER_LIST>', glanceAPIServerListContent)
        #append to haproxy.cfg
        if os.path.exists(haproxyConfFilePath) :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % haproxyConfFilePath)
        else :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % glanceHAProxyTemplateFilePath)
            pass
        
        haproxyNativeContent = output.strip()
        
        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        
        haproxyContent += glanceBackendRegistryApiString
        haproxyContent += glanceBackendApiString
        
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        if os.path.exists(haproxyConfFilePath):
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % haproxyConfFilePath)
            pass
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
        ##############

        #Default: glance-api & glance-registry-api use the same vip
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)
        pass
    
    @staticmethod
    def configureKeepalived():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        ###################configure keepalived
        glanceKeepalivedTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keepalived.conf')
        keepalivedConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEEPALIVED_CONF_FILE_PATH')
        print 'keepalivedConfFilePath=%s' % keepalivedConfFilePath
        if not os.path.exists('/etc/keepalived') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/keepalived')
            pass
        
        #configure haproxy check script in keepalived
        checkHAProxyScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
        print 'checkHAProxyScriptPath=%s===========================---' % checkHAProxyScriptPath
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (checkHAProxyScriptPath, '/etc/keepalived'))
        if os.path.exists(keepalivedConfFilePath) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % keepalivedConfFilePath)
            pass
            
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (glanceKeepalivedTemplateFilePath, '/etc/keepalived'))
        
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
        
        weight_counter = 300
        if GlanceHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = GlanceHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass
        
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', glance_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', glance_vip)
        
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
        print 'To get this host index of role %s==============' % "glance" 
        glance_ips = JSONUtility.getValue('glance_ips')
        glance_ip_list = glance_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'glance_ip_list=%s--------------' % glance_ip_list
        index = glance_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if GlanceHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            glance_vip_interface = JSONUtility.getValue("glance_vip_interface")
            glance_vip = JSONUtility.getValue("glance_vip")
            
            GlanceHA.addVIP(glance_vip, glance_vip_interface)
            
            if GlanceHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
#             GlanceHA.deleteVIP(glance_vip, glance_vip_interface)
            if GlanceHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            #Ensure only one VIP exists.
            isMasterNode = GlanceHA.isMasterNode()
            if isMasterNode == True :
                GlanceHA.restart()
            else :
                GlanceHA.deleteVIP(glance_vip, glance_vip_interface)
            pass
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('service haproxy restart')
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:glance============'
    
    print 'start time: %s' % time.ctime()
    
#     print 'test exist VIP============================'
#     print 'existVIP=%s' % GlanceHA.isExistVIP('192.168.11.100', 'eth0')
#     print 'test add VIP=============================='
#     GlanceHA.addVIP('192.168.11.100', 'eth0')
#     print 'test delete VIP==========================='
#     GlanceHA.deleteVIP('192.168.11.100', 'eth0')
    
    INSTALL_TAG_FILE = '/opt/glance_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'glance installed####'
        print 'exit===='
        pass
    else :
        print 'start to install======='
        Prerequisites.prepare()
        #
        Glance.install()
        Glance.configConfFile()
    #     Glance.start()
    # #      
    #     Glance.sourceAdminOpenRC()
    #     #add HA
    #     GlanceHA.install()
    #     GlanceHA.configure()
    #     GlanceHA.start()
    #     
    #     Glance.restart()
    #     GlanceHA.restart
        
    #     os.system("service openstack-glance-api restart")
    #     os.system("service openstack-glance-registry restart")
    #     
    #     os.system("service haproxy restart")
        #mark: glance is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    
    print 'hello openstack-icehouse:glance#######'
    pass

