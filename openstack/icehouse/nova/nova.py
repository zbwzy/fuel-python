'''
Created on Sep 29, 2015

@author: zhangbai
'''

'''
usage:

python nova.py

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
        yumCmd = "yum install -y openstack-nova-api openstack-nova-cert openstack-nova-conductor \
        openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler python-novaclient"
        
        ShellCmdExecutor.execCmd(yumCmd)
#         Nova.configConfFile()
        
#         Nova.start()
        
        #After Network node configuration done
#         Nova.configAfterNetworkNodeConfiguration()
#         Nova.restart()
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
        #restart nova-api service
        ShellCmdExecutor.execCmd("service openstack-nova-api restart")
        ShellCmdExecutor.execCmd("service openstack-nova-cert restart")
        ShellCmdExecutor.execCmd("service openstack-nova-consoleauth restart")
        ShellCmdExecutor.execCmd("service openstack-nova-scheduler restart")
        ShellCmdExecutor.execCmd("service openstack-nova-conductor restart")
        ShellCmdExecutor.execCmd("service openstack-nova-novncproxy restart")
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
        #use conf template file to replace 
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
#         rabbit_host = JSONUtility.getValue("rabbit_host")
#         rabbit_vip = JSONUtility.getValue("rabbit_vip")
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        glance_vip = JSONUtility.getValue("glance_vip")
        
        nova_mysql_password = JSONUtility.getValue("nova_mysql_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH') 
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'ddddddddddddddd========='
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'glance_vip=%s' % glance_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        nova_api_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'nova.conf')
        print 'nova_api_conf_template_file_path=%s' % nova_api_conf_template_file_path
        
        novaConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'NOVA_CONF_DIR')
        print 'novaConfDir=%s' % novaConfDir #/etc/nova
        
        nova_conf_file_path = os.path.join(novaConfDir, 'nova.conf')
        print 'nova_conf_file_path=%s' % nova_conf_file_path
        
        if not os.path.exists(novaConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % novaConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % novaConfDir)
        
        if os.path.exists(nova_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % nova_conf_file_path)
            pass
        
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (nova_api_conf_template_file_path, novaConfDir))
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/nova.conf" % nova_api_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/nova.conf /etc/nova/")
        ShellCmdExecutor.execCmd("rm -rf /tmp/nova.conf")
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % nova_conf_file_path)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<LOCAL_IP>', localIP)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NOVA_MYSQL_PASSWORD>', nova_mysql_password)
        
#         FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOST>', rabbit_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<GLANCE_VIP>', glance_vip)
        
#         FileUtil.replaceFileContent(nova_conf_file_path, '<NEUTRON_VIP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % nova_conf_file_path)
        
        #special handling
        PYTHON_SITE_PACKAGE_DIR = '/usr/lib/python2.6/site-packages'
        if os.path.exists(PYTHON_SITE_PACKAGE_DIR) :
            ShellCmdExecutor.execCmd('chmod 777 %s' % PYTHON_SITE_PACKAGE_DIR)
            pass
            
        LIB_NOVA_DIR = '/var/lib/nova'
        if os.path.exists(LIB_NOVA_DIR) :
            ShellCmdExecutor.execCmd('chown -R nova:nova %s' % LIB_NOVA_DIR)
            pass
        
        if os.path.exists('/etc/nova/') :
            ShellCmdExecutor.execCmd("chown -R nova:nova /etc/nova")
        pass
    

class NovaHA(object):
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
        if NovaHA.isExistVIP(vip, interface) :
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
        result = NovaHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not NovaHA.isExistVIP(vip, interface) :
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
        result = NovaHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if NovaHA.isExistVIP(vip, interface) :
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
            if not NovaHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not NovaHA.isHAProxyInstalled() :
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
        NovaHA.configureHAProxy()
        NovaHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        nova_vip = JSONUtility.getValue("nova_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        HAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        nova_ips = JSONUtility.getValue("nova_ips")
        nova_ip_list = nova_ips.strip().split(',')
        
        novaEC2ApiBackendStringTemplate = '''
listen nova_ec2_api_cluster
  bind <NOVA_VIP>:8773
  balance source
  <NOVA_EC2_API_SERVER_LIST>
  '''
        novaComputeApiBackendStringTemplate = '''
listen nova_compute_api_cluster
  bind <NOVA_VIP>:8774
  balance source
  <NOVA_COMPUTE_API_SERVER_LIST>
        '''
        
        novaMetadataApiBackendStringTemplate = '''
listen nova_metadata_api_cluster
  bind <NOVA_VIP>:8775
  balance source
  <NOVA_METADATA_API_SERVER_LIST>
        '''
        
        vncBackendStringTemplate = '''
listen vnc_cluster
  bind <NOVA_VIP>:6080
  balance source
  option tcpka
  option tcplog
  <VNC_SERVER_LIST>
        '''
        
        novaEC2ApiBackendString = novaEC2ApiBackendStringTemplate.replace('<NOVA_VIP>', nova_vip)
        novaComputeApiBackendString = novaComputeApiBackendStringTemplate.replace('<NOVA_VIP>', nova_vip)
        novaMetadataApiBackendString = novaMetadataApiBackendStringTemplate.replace('<NOVA_VIP>', nova_vip)
        vncBackendString = vncBackendStringTemplate.replace('<NOVA_VIP>', nova_vip)
        ###############
        
        serverNovaEC2APIBackendTemplate = 'server nova-<INDEX> <SERVER_IP>:8773 check inter 2000 rise 2 fall 5'
        serverNovaComputeAPIBackendTemplate = 'server nova-<INDEX> <SERVER_IP>:8774 check inter 2000 rise 2 fall 5'
        serverNovaMetadataAPIBackendTemplate = 'server nova-<INDEX> <SERVER_IP>:8775 check inter 2000 rise 2 fall 5'
        serverVNCBackendTemplate = 'server nova-<INDEX> <SERVER_IP>:6080 check inter 2000 rise 2 fall 5'
        
        novaEC2APIServerListContent = ''
        novaComputeAPIServerListContent = ''
        novaMetadataAPIServerListContent = ''
        vncServerListContent = ''
        
        index = 1
        for ip in nova_ip_list:
            print 'nova_ip=%s' % ip
            novaEC2APIServerListContent += serverNovaEC2APIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            novaComputeAPIServerListContent += serverNovaComputeAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            novaMetadataAPIServerListContent += serverNovaMetadataAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            vncServerListContent += serverVNCBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            
            novaEC2APIServerListContent += '\n'
            novaEC2APIServerListContent += '  '
            
            novaComputeAPIServerListContent += '\n'
            novaComputeAPIServerListContent += '  '
            
            novaMetadataAPIServerListContent += '\n'
            novaMetadataAPIServerListContent += '  '
            
            vncServerListContent += '\n'
            vncServerListContent += '  '
            
            index += 1
            pass
        
        novaEC2APIServerListContent = novaEC2APIServerListContent.strip()
        novaComputeAPIServerListContent = novaComputeAPIServerListContent.strip()
        novaMetadataAPIServerListContent = novaMetadataAPIServerListContent.strip()
        
        novaEC2ApiBackendString = novaEC2ApiBackendString.replace('<NOVA_EC2_API_SERVER_LIST>', novaEC2APIServerListContent)
        novaComputeApiBackendString = novaComputeApiBackendString.replace('<NOVA_COMPUTE_API_SERVER_LIST>', novaComputeAPIServerListContent)
        novaMetadataApiBackendString = novaMetadataApiBackendString.replace('<NOVA_METADATA_API_SERVER_LIST>', novaMetadataAPIServerListContent)
        vncBackendString = vncBackendString.replace('<VNC_SERVER_LIST>', vncServerListContent)
        
        #append to haproxy.cfg
        if os.path.exists(haproxyConfFilePath) :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % haproxyConfFilePath)
        else :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % HAProxyTemplateFilePath)
            pass
        
        haproxyNativeContent = output.strip()
        
        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        
        haproxyContent += novaEC2ApiBackendString
        haproxyContent += novaComputeApiBackendString
        haproxyContent += novaMetadataApiBackendString
        haproxyContent += vncBackendString
        
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        if os.path.exists(haproxyConfFilePath):
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % haproxyConfFilePath)
            pass
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
        
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
        nova_vip = JSONUtility.getValue("nova_vip")
        nova_vip_interface = JSONUtility.getValue("nova_vip_interface")
        
        weight_counter = 300
        if NovaHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = NovaHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass
        
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', nova_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', nova_vip)
        
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
        nova_ips = JSONUtility.getValue('nova_ips')
        nova_ip_list = nova_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'nova_ip_list=%s--------------' % nova_ip_list
        index = nova_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if NovaHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            nova_vip_interface = JSONUtility.getValue("nova_vip_interface")
            nova_vip = JSONUtility.getValue("nova_vip")
            
            NovaHA.addVIP(nova_vip, nova_vip_interface)
            
            if NovaHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
            if NovaHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            #Ensure only one VIP exists.
            isMasterNode = NovaHA.isMasterNode()
            if isMasterNode == True :
                NovaHA.restart()
            else :
                NovaHA.deleteVIP(nova_vip, nova_vip_interface)
            pass
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('service haproxy restart')
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:nova============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
    
    ###############################
    INSTALL_TAG_FILE = '/opt/novaapi_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-api installed####'
        print 'exit===='
        pass
    
    else :
        Prerequisites.prepare()
        Nova.install()
        Nova.configConfFile()
#         Nova.start()
#         
#         NovaHA.install()
#         NovaHA.configure()
#         NovaHA.start()
        
        #mark: nova-api is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:nova-api#######'
    pass

