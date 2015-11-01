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
        controller_vip = JSONUtility.getValue("controller_vip")
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
        
        ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (nova_api_conf_template_file_path, novaConfDir))
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
    def configDB():
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
                
                ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (haproxyTemplateFilePath, haproxyConfFilePath))
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
        nova_api_vip = JSONUtility.getValue("nova_api_vip")
        print 'nova_api_vip=%s' % nova_api_vip
        
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
        novaApiFrontendStringTemplate = '''
frontend nova-api-vip-1
    bind <NOVA_API_VIP>:8773
    default_backend nova-api-1

frontend nova-api-vip-2
    bind <NOVA_API_VIP>:8774
    default_backend nova-api-2
    
frontend nova-api-vip-3
    bind <NOVA_API_VIP>:8775
    default_backend nova-api-3
    
frontend nova-api-vip-4
    bind <NOVA_API_VIP>:8776
    default_backend nova-api-4
'''
        novaApiFrontendString = novaApiFrontendStringTemplate.replace('<NOVA_API_VIP>', nova_api_vip)
        print 'novaApiFrontendString=%s--' % novaApiFrontendString
        
        ####
        nova_api_ips = JSONUtility.getValue("nova_api_ips")
        nova_api_ip_list = nova_api_ips.strip().split(',')
        
        novaApi1BackendStringTemplate = '''
backend nova-api-1
    balance roundrobin
    <NOVA_API1_SERVER_LIST>
        '''
        
        novaApi2BackendStringTemplate = '''
backend nova-api-2
    balance roundrobin
    <NOVA_API2_SERVER_LIST>
        '''
        
        novaApi3BackendStringTemplate = '''
backend nova-api-3
    balance roundrobin
    <NOVA_API3_SERVER_LIST>
        '''
        
        novaApi4BackendStringTemplate = '''
backend nova-api-4
    balance roundrobin
    <NOVA_API4_SERVER_LIST>
        '''
        
        serverNovaApi1BackendTemplate  = 'server nova-api-<INDEX> <SERVER_IP>:8773 check inter 10s'
        serverNovaApi2BackendTemplate  = 'server nova-api-<INDEX> <SERVER_IP>:8774 check inter 10s'
        serverNovaApi3BackendTemplate  = 'server nova-api-<INDEX> <SERVER_IP>:8775 check inter 10s'
        serverNovaApi4BackendTemplate  = 'server nova-api-<INDEX> <SERVER_IP>:8776 check inter 10s'
        
        novaAPI1ServerListContent = ''
        novaAPI2ServerListContent = ''
        novaAPI3ServerListContent = ''
        novaAPI4ServerListContent = ''
        
        index = 1
        for nova_api_ip in nova_api_ip_list:
            novaAPI1ServerListContent += serverNovaApi1BackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            novaAPI2ServerListContent += serverNovaApi2BackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            novaAPI3ServerListContent += serverNovaApi3BackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            novaAPI4ServerListContent += serverNovaApi4BackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            
            novaAPI1ServerListContent += '\n'
            novaAPI1ServerListContent += '    '
            
            novaAPI2ServerListContent += '\n'
            novaAPI2ServerListContent += '    '
            
            novaAPI3ServerListContent += '\n'
            novaAPI3ServerListContent += '    '
            
            novaAPI4ServerListContent += '\n'
            novaAPI4ServerListContent += '    '
            
            index += 1
            pass
        
        novaAPI1ServerListContent = novaAPI1ServerListContent.strip()
        novaAPI2ServerListContent = novaAPI2ServerListContent.strip()
        novaAPI3ServerListContent = novaAPI3ServerListContent.strip()
        novaAPI4ServerListContent = novaAPI4ServerListContent.strip()
        
        
        novaApi1BackendString = novaApi1BackendStringTemplate.replace('<NOVA_API1_SERVER_LIST>', novaAPI1ServerListContent)
        novaApi2BackendString = novaApi2BackendStringTemplate.replace('<NOVA_API2_SERVER_LIST>', novaAPI2ServerListContent)
        novaApi3BackendString = novaApi3BackendStringTemplate.replace('<NOVA_API3_SERVER_LIST>', novaAPI3ServerListContent)
        novaApi4BackendString = novaApi4BackendStringTemplate.replace('<NOVA_API4_SERVER_LIST>', novaAPI4ServerListContent)
        
        #append
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (novaApiFrontendString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (novaApi1BackendString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (novaApi2BackendString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (novaApi3BackendString, haproxyConfFilePath))
        ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (novaApi4BackendString, haproxyConfFilePath))
        
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
        keystone_weight_counter = Nova.getWeightCounter()
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
    
    print 'hello openstack-icehouse:nova============'
    
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
    INSTALL_TAG_FILE = '/opt/novaapi_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-api installed####'
        print 'exit===='
        exit()
        pass
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-api installed####'
        print 'exit===='
        exit()
        pass
    
#     Nova.install()
#     Nova.configConfFile()
#     Nova.start()
    #
    NovaHA.install()
    NovaHA.configure()
    NovaHA.start()
    
    #mark: nova-api is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:nova-api#######'
    pass

