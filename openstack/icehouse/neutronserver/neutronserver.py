'''
Created on Sept 27, 2015

@author: zhangbai
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
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil   
    

class Prerequisites(object):
    '''
    classdocs
    '''
    SYS_CTL_FILE_PATH = "/etc/sysctl.conf"
    
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
    

class NeutronServer(object):
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
        print 'NeutronServer.install start===='
        #Install Openstack network services
        yumCmd = "yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch python-neutronclient which -y"
        ShellCmdExecutor.execCmd(yumCmd)
        print 'NeutronServer.install done####'
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd('service neutron-server start')
        ShellCmdExecutor.execCmd('chkconfig neutron-server on')
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('service neutron-server restart')
        pass
    
    @staticmethod
    def configConfFile():
        NeutronServer.configNeutronConfFile()
        
        NeutronServer.configML2()
        
        ShellCmdExecutor.execCmd('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
        
        if NeutronServerHA.isMasterNode() :
            importNeutronDBSchemaCmd = 'su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf \
            --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade juno" neutron'
            output, exitcode = ShellCmdExecutor.execCmd(importNeutronDBSchemaCmd)
            print 'importNeutronSchemaOutput=%s--' % output
            pass
        pass
        
    @staticmethod
    def getServiceTenantID():
        #install keystone client
        ShellCmdExecutor.execCmd('yum install python-keystoneclient -y')
        
        serviceTenantIDScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server','serviceTenantID.sh')
        print 'serviceTenantIDScriptPath=%s' % serviceTenantIDScriptPath
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/' % serviceTenantIDScriptPath)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        FileUtil.replaceFileContent('/opt/serviceTenantID.sh', '<KEYSTONE_VIP>', keystone_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash /opt/serviceTenantID.sh')
        serviceTenantID = output.strip()
        if debug == True : #fake for local debug
            serviceTenantID = '112233445566'
            pass
        
        print 'serviceTenantID=%s--' % serviceTenantID
        return serviceTenantID
        pass
    
    @staticmethod
    def configNeutronConfFile():
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        neutron_mysql_password = JSONUtility.getValue("neutron_mysql_password")
        
        rabbit_host = JSONUtility.getValue("rabbit_host")
        rabbit_vip = JSONUtility.getValue("rabbit_vip")
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        nova_vip = JSONUtility.getValue("nova_vip")
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'nova_vip=%s' % nova_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        neutron_server_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'neutron.conf')
        print 'neutron_server_conf_template_file_path=%s' % neutron_server_conf_template_file_path
        
        neutronConfDir = '/etc/neutron'
        if not os.path.exists(neutronConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % neutronConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % neutronConfDir)
        
        neutron_conf_file_path = os.path.join(neutronConfDir, 'neutron.conf')
        if os.path.exists(neutron_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % neutron_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/neutron.conf" % neutron_server_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/neutron.conf /etc/neutron/")
        
        serviceTenantID = NeutronServer.getServiceTenantID()
        FileUtil.replaceFileContent(neutron_conf_file_path, '<NOVA_ADMIN_TENANT_ID>', serviceTenantID  )
        FileUtil.replaceFileContent(neutron_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<NEUTRON_MYSQL_PASSWORD>', neutron_mysql_password)
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_HOST>', rabbit_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<NOVA_VIP>', nova_vip)
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % neutron_conf_file_path)
        pass
    
    @staticmethod
    def configML2():
        if os.path.exists(NeutronServer.NEUTRON_ML2_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd('rm -rf %s' % NeutronServer.NEUTRON_ML2_CONF_FILE_PATH)
            pass
        
        NEUTRON_ML2_CONF_DIR = '/etc/neutron/plugins/ml2/'
        neutron_server_ml2_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ml2_conf.ini')
        ShellCmdExecutor.execCmd('cp -r %s %s' % (neutron_server_ml2_template_file_path, NEUTRON_ML2_CONF_DIR))
        pass
    pass
    
class NeutronServerHA(object):
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
        if NeutronServerHA.isExistVIP(vip, interface) :
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
        result = NeutronServerHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not NeutronServerHA.isExistVIP(vip, interface) :
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
        result = NeutronServerHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if NeutronServerHA.isExistVIP(vip, interface) :
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
            if not NeutronServerHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not NeutronServerHA.isHAProxyInstalled() :
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
        NeutronServerHA.configureHAProxy()
        NeutronServerHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        neutron_vip = JSONUtility.getValue("neutron_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        HAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (HAProxyTemplateFilePath, '/etc/haproxy'))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        ####
        ##############new
        neutronApiBackendStringTemplate = '''
listen neutron_api_cluster
  bind <NEUTRON_VIP>:9696
  balance source
  <NEUTRON_API_SERVER_LIST>
  '''

        neutronApiBackendString = neutronApiBackendStringTemplate.replace('<NEUTRON_VIP>', neutron_vip)
        
        ################new
        neutron_ips = JSONUtility.getValue("neutron_ips")
        neutron_ip_list = neutron_ips.strip().split(',')
        
        serverNeutronAPIBackendTemplate   = 'server neutron-<INDEX> <SERVER_IP>:9696 check inter 2000 rise 2 fall 5'
        neutronAPIServerListContent = ''
        index = 1
        for ip in neutron_ip_list:
            print 'neutron_ip=%s' % ip
            neutronAPIServerListContent += serverNeutronAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            
            neutronAPIServerListContent += '\n'
            neutronAPIServerListContent += '  '
            index += 1
            pass
        
        neutronAPIServerListContent = neutronAPIServerListContent.strip()
        print 'neutronAPIServerListContent=%s--' % neutronAPIServerListContent
        
        neutronApiBackendString = neutronApiBackendString.replace('<NEUTRON_API_SERVER_LIST>', neutronAPIServerListContent)
        
        print 'neutronApiBackendString=%s--' % neutronApiBackendString
        
        #append
        if os.path.exists(haproxyConfFilePath) :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % haproxyConfFilePath)
        else :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % HAProxyTemplateFilePath)
            pass
        
        haproxyNativeContent = output.strip()
        
        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        
        haproxyContent += neutronApiBackendString
        
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        if os.path.exists(haproxyConfFilePath):
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % haproxyConfFilePath)
            pass
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
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
        neutron_vip = JSONUtility.getValue("neutron_vip")
        neutron_vip_interface = JSONUtility.getValue("neutron_vip_interface")
        
        weight_counter = 300
        if NeutronServerHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = NeutronServerHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass
            
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', neutron_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', neutron_vip)
        
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
        print 'To get this host index of role %s==============' % "neutron-server" 
        neutron_ips = JSONUtility.getValue('neutron_ips')
        neutron_ip_list = neutron_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'neutron_ip_list=%s--------------' % neutron_ip_list
        index = neutron_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if NeutronServerHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            neutron_vip_interface = JSONUtility.getValue("neutron_vip_interface")
            neutron_vip = JSONUtility.getValue("neutron_vip")
            
            NeutronServerHA.addVIP(neutron_vip, neutron_vip_interface)
            
            if NeutronServerHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
            if NeutronServerHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            isMasterNode = NeutronServerHA.isMasterNode()
            if isMasterNode == True :
                NeutronServerHA.restart()
                pass
            else :
                NeutronServerHA.deleteVIP(neutron_vip, neutron_vip_interface)
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
    print 'openstack-icehouse:neutron-server start============'
    INSTALL_TAG_FILE = '/opt/neutronserver_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'neutron-server installed####'
        print 'exit===='
        pass
    else :
        Prerequisites.prepare()
        
        NeutronServer.install()
        
        NeutronServer.configConfFile()
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'openstack-icehouse:neutron-server done#######'
    pass

