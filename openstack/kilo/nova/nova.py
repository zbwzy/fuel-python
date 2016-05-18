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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from openstack.kilo.ssh.SSH import SSH 
from openstack.common.serverSequence import ServerSequence

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
        yumCmd = "yum install openstack-nova-api openstack-nova-cert openstack-nova-conductor \
        openstack-nova-console openstack-nova-novncproxy openstack-nova-scheduler \
        python-novaclient -y"
        ShellCmdExecutor.execCmd(yumCmd)
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
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-api.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-cert.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-consoleauth.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-scheduler.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-conductor.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-novncproxy.service")
        
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-api.service")
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-cert.service")
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-consoleauth.service")
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-scheduler.service")
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-conductor.service") 
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-novncproxy.service")
        pass
    
    @staticmethod
    def configConfFile():
        #use conf template file to replace 
        '''
        MEMCACHED_LIST
        LOCAL_MANAGEMENT_IP
        GLANCE_VIP
        KEYSTONE_VIP
        KEYSTONE_NOVA_PASSWORD
        METADATA_SECRET
        NEUTRON_VIP
        KEYSTONE_NEUTRON_PASSWORD
        RABBIT_HOSTS
        RABBIT_PASSWORD
        NOVA_DBPASS
        MYSQL_VIP
        '''
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"] 

        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
#         rabbit_userid = rabbit_params_dict["rabbit_userid"]
        
        vipParamsDict = JSONUtility.getValue('vip')
        cinder_vip = vipParamsDict["cinder_vip"]
        glance_vip = vipParamsDict["glance_vip"]
        neutron_vip = vipParamsDict["neutron_vip"]
       
        keystone_nova_password = JSONUtility.getValue("keystone_nova_password")
        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        metadata_secret = '123456' #JSONUtility.getValue("metadata_secret")    #the same with dhcp.ini in neutron
        
        nova_dbpass = JSONUtility.getValue("nova_dbpass")
        
        nova_ips = JSONUtility.getValue('nova_ips')
        nova_ip_list = nova_ips.strip().split(',')
        memcached_service_list = []
        for ip in nova_ip_list:
            memcached_service_list.append(ip.strip() + ':11211')
            pass
        
        memcached_service_string = ','.join(memcached_service_list)
        print 'memcached_service_string=%s--' % memcached_service_string
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH') 
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'rabbit_hosts=%s' % rabbit_hosts
#         print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'glance_vip=%s' % glance_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        nova_api_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'nova.conf')
        print 'nova_api_conf_template_file_path=%s' % nova_api_conf_template_file_path
        
        nova_controller_restart_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'startNova.conf')
        ShellCmdExecutor.execCmd("cp -r %s /opt/openstack_conf/scripts/" % nova_controller_restart_file_path)
        
        novaConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'NOVA_CONF_DIR')
        print 'novaConfDir=%s' % novaConfDir #/etc/nova
        
        nova_conf_file_path = os.path.join(novaConfDir, 'nova.conf')
        print 'nova_conf_file_path=%s' % nova_conf_file_path
        
        if not os.path.exists(novaConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % novaConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % novaConfDir)
        
        if os.path.exists(nova_conf_file_path) :
            #REFACTOR
            ShellCmdExecutor.execCmd("sudo cp -r %s /etc/nova/nova.conf.bak" % nova_conf_file_path)
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % nova_conf_file_path)
            pass
        
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (nova_api_conf_template_file_path, novaConfDir))
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/nova.conf" % nova_api_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/nova.conf /etc/nova/")
        ShellCmdExecutor.execCmd("rm -rf /tmp/nova.conf")
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % nova_conf_file_path)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<MEMCACHED_LIST>', memcached_service_string)
        FileUtil.replaceFileContent(nova_conf_file_path, '<LOCAL_MANAGEMENT_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<GLANCE_VIP>', glance_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_NOVA_PASSWORD>', keystone_nova_password)
        FileUtil.replaceFileContent(nova_conf_file_path, '<METADATA_SECRET>', metadata_secret)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NEUTRON_VIP>', neutron_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NOVA_DBPASS>', nova_dbpass)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % nova_conf_file_path)
        
        #special handling
        PYTHON_SITE_PACKAGE_DIR = '/usr/lib/python2.7/site-packages'
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
        pass
    
    @staticmethod
    def importNovaDBSchema():
        importCmd = 'su -s /bin/sh -c "nova-manage db sync" nova'
        ShellCmdExecutor.execCmd(importCmd)
        pass
    
    @staticmethod
    def getServerIndex():
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        local_management_ip = output.strip()
        nova_ips = JSONUtility.getValue('nova_ips')
        nova_ip_list = nova_ips.split(',')
        index = ServerSequence.getIndex(nova_ip_list, local_management_ip)
        return index
    
if __name__ == '__main__':
    
    print 'hello openstack-kilo:nova-controller============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
    
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/novacontroller_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-api installed####'
        print 'exit===='
        pass
    
    else :
        Nova.install()
        Nova.configConfFile()
        
        ###########
        #import nova db schema
#         output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
#         localIP = output.strip()
#         nova_ips = JSONUtility.getValue("nova_ips")
#         nova_ip_list = nova_ips.strip().split(',')
#         
#         first_nova_launched_mark_file = '/opt/openstack_conf/tag/nova0_launched'
#         
#         TIMEOUT = 1800 #0.5 hour for test
#         if ServerSequence.getIndex(nova_ip_list, localIP) == 0:
#             firstKeystoneLaunchedTag = '/opt/openstack_conf/tag/keystone0_launched'
#             timeout = TIMEOUT
#             time_count = 0
#             print 'test timeout==='
#             while True:
#                 #all mysql are launched.
#                 flag = os.path.exists(firstKeystoneLaunchedTag)
#                 if flag == True :
#                     print 'wait time: %s second(s).' % time_count
#                     Nova.importNovaDBSchema()
#                     
#                     break
#                 else :
#                     step = 1
#         #             print 'wait %s second(s)......' % step
#                     time_count += step
#                     time.sleep(1)
#                     pass
#                 
#                 if time_count == timeout :
#                     print 'Do nothing!timeout=%s.' % timeout
#                     break
#                 pass
#             
#             if len(nova_ip_list) > 1 :
#                 for nova_ip in nova_ip_list[1:] :
#                     SSH.sendTagTo(nova_ip, first_nova_launched_mark_file)
#                     pass
#                 pass
#             
#             Nova.start()
#             pass
#         else :
#             timeout = TIMEOUT
#             time_count = 0
#             print 'test timeout==='
#             while True:
#                 #first nova controller is launched
#                 flag = os.path.exists(first_nova_launched_mark_file)
#                 if flag == True :
#                     print 'wait time: %s second(s).' % time_count
#                     Nova.start()
#                     
#                     break
#                 else :
#                     step = 1
#         #             print 'wait %s second(s)......' % step
#                     time_count += step
#                     time.sleep(1)
#                     pass
#                 
#                 if time_count == timeout :
#                     print 'Do nothing!timeout=%s.' % timeout
#                     break
#                 pass
#             pass
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        #mark: nova-api is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:nova-controller#######'
    pass

