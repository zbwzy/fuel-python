'''
Created on Oct 8, 2015

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

class Cinder(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/cinder/cinder.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Cinder.install start===='
        yumCmd = 'yum install openstack-cinder python-cinderclient python-oslo-db -y'
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Cinder.install done####'
        pass

    @staticmethod
    def restart():
        #restart cinder service
        ShellCmdExecutor.execCmd("service openstack-cinder-api restart")
        ShellCmdExecutor.execCmd("service openstack-cinder-scheduler restart")
        pass
    
    @staticmethod
    def start():        
        ShellCmdExecutor.execCmd("service openstack-cinder-api start")
        ShellCmdExecutor.execCmd("service openstack-cinder-scheduler start")
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
        
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        glance_vip = JSONUtility.getValue("glance_vip")
        keystone_vip = JSONUtility.getValue("keystone_vip")
        nova_api_vip = JSONUtility.getValue("nova_api_vip")
        
        virt_type = JSONUtility.getValue("virt_type")
        
        #controller: Horizon, Neutron-server
        controller_vip = JSONUtility.getValue("controller_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('sudo cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'ddddddddddddddd========='
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'nova_api_vip=%s' % nova_api_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        nova_api_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'nova.conf')
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
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NOVA_API_VIP>', keystone_vip)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<GLANCE_HOST>', glance_vip)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<VIRT_TYPE>', virt_type)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<LOCAL_IP>', localIP)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<PUBLIC_LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<MANAGEMENT_LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NEUTRON_SERVER_VIP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % nova_conf_file_path)
        pass
    
    @staticmethod
    def configDB():
        pass

    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:cinder============'
    
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
    INSTALL_TAG_FILE = '/opt/cinder_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'cinder installed####'
        print 'exit===='
        exit()
        pass
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'cinder installed####'
        print 'exit===='
        exit()
        pass
    
    Cinder.install()
    Cinder.configConfFile()
    Cinder.start()
    #
    #mark: nova-compute is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:cinder#######'
    pass

