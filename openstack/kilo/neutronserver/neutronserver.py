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
        yumCmd = "yum install openstack-neutron openstack-neutron-ml2 python-neutronclient which -y"
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
        pass
    
    @staticmethod
    def importNeutronDBSchema():
        ######
        importNeutronDBSchemaCmd = 'su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf \
        --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron'
        output, exitcode = ShellCmdExecutor.execCmd(importNeutronDBSchemaCmd)
        print 'importNeutronSchemaOutput=%s--' % output
        ########
        
    @staticmethod
    def configNeutronConfFile():
        '''
        NEUTRON_DBPASS
        MYSQL_VIP
        RABBIT_HOSTS
        RABBIT_PASSWORD
        KEYSTONE_VIP
        KEYSTONE_NEUTRON_PASSWORD
        '''
        mysql_vip = JSONUtility.getValue("mysql_vip")
        neutron_dbpass = JSONUtility.getValue("neutron_dbpass")
        
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        nova_vip = JSONUtility.getValue("nova_vip")
        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        print 'mysql_vip=%s' % mysql_vip
        print 'rabbit_hosts=%s' % rabbit_hosts
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
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
#         FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(neutron_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
#         FileUtil.replaceFileContent(neutron_conf_file_path, '<NOVA_VIP>', nova_vip)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<NEUTRON_DBPASS>', neutron_dbpass)
        FileUtil.replaceFileContent(neutron_conf_file_path, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        
#         FileUtil.replaceFileContent(neutron_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("chmod 644 %s" % neutron_conf_file_path)
        ShellCmdExecutor.execCmd("chown -R neutron:neutron /etc/neutron/")
        pass
    
    @staticmethod
    def configML2():
        if os.path.exists(NeutronServer.NEUTRON_ML2_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd('rm -rf %s' % NeutronServer.NEUTRON_ML2_CONF_FILE_PATH)
            pass
        
        NEUTRON_ML2_CONF_DIR = '/etc/neutron/plugins/ml2/'
        if not os.path.exists(NEUTRON_ML2_CONF_DIR) :
            os.system("mkdir -p %s" % NEUTRON_ML2_CONF_DIR)
            pass
        
        neutron_server_ml2_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ml2_conf.ini')
        ShellCmdExecutor.execCmd('cp -r %s %s' % (neutron_server_ml2_template_file_path, NEUTRON_ML2_CONF_DIR))
        pass
    pass

    

if __name__ == '__main__':
    print 'openstack-kilo:neutron-server start============'
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/neutronserver_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'neutron-server installed####'
        print 'exit===='
        pass
    else :
#         Prerequisites.prepare()
        
        NeutronServer.install()
        
        NeutronServer.configConfFile()
        
        #import neutron server db schema
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        neutron_ips = JSONUtility.getValue("neutron_ips")
        neutron_ip_list = neutron_ips.split(',')
        
        first_neutron_launched_mark_file = '/opt/openstack_conf/tag/neutronserver0_launched'
        
        TIMEOUT = 1800 #0.5 hour for test
        if ServerSequence.getIndex(neutron_ip_list, localIP) == 0:
            firstKeystoneLaunchedTag = '/opt/openstack_conf/tag/keystone0_launched'
            timeout = TIMEOUT
            time_count = 0
            print 'test timeout==='
            while True:
                #all mysql are launched.
                flag = os.path.exists(firstKeystoneLaunchedTag)
                if flag == True :
                    print 'wait time: %s second(s).' % time_count
                    NeutronServer.importNeutronDBSchema()
                    
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                
                if time_count == timeout :
                    print 'Do nothing!timeout=%s.' % timeout
                    break
                pass
            
            if len(neutron_ip_list) > 1 :
                for neutron_ip in neutron_ip_list[1:] :
                    SSH.sendTagTo(neutron_ip, first_neutron_launched_mark_file)
                    pass
                pass
            
            NeutronServer.start()
            pass
        else :
            timeout = TIMEOUT
            time_count = 0
            print 'test timeout==='
            while True:
                #first neutron server is launched
                flag = os.path.exists(first_neutron_launched_mark_file)
                if flag == True :
                    print 'wait time: %s second(s).' % time_count
                    NeutronServer.start()
                    
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                
                if time_count == timeout :
                    print 'Do nothing!timeout=%s.' % timeout
                    break
                pass
            
            NeutronServer.start()
            pass
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'openstack-kilo:neutron-server done#######'
    pass

