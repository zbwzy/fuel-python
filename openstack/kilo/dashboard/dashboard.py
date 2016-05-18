'''
Created on Sep 29, 2015

@author: zhangbai
'''

'''
Note:
Defaultly,on localhost, dashboard is listened on port 8080.

usage:

python dashboard.py

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

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
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

class Dashboard(object):
    '''
    classdocs
    '''
    DASHBOARD_CONF_FILE_PATH = "/etc/openstack-dashboard/local_settings"
    HTTPD_CONF_FILE_PATH = '/etc/httpd/conf/httpd.conf'
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Dashboard.install start===='
        yumCmd = "yum install openstack-dashboard httpd mod_wsgi memcached python-memcached -y"
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Dashboard.install done####'
        pass
    
    @staticmethod
    def configure():
        Dashboard.configConfFile()
        
        #assign network connect
        ShellCmdExecutor.execCmd("setsebool -P httpd_can_network_connect on")
        
        #Due to a packaging bug, the dashboard CSS fails to load properly. 
        #Run the following command to resolve this issue:
        ShellCmdExecutor.execCmd("chown -R apache:apache /usr/share/openstack-dashboard/static")
        
#         Dashboard.configHttpdConfFile()
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("systemctl enable httpd.service")
        ShellCmdExecutor.execCmd("systemctl restart httpd.service", timeout=15)
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd("systemctl restart httpd.service", timeout=15)
        pass
    
    
    @staticmethod
    def configConfFile():
        '''
        LOCAL_MANAGEMENT_IP
        KEYSTONE_VIP
        '''
        localSettingsFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'dashboard', 'local_settings')
        dashboardConfFileDir = '/etc/openstack-dashboard/'
        
        if os.path.exists(Dashboard.DASHBOARD_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("rm -rf %s" % Dashboard.DASHBOARD_CONF_FILE_PATH)
            pass
        else :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % dashboardConfFileDir)
            pass
        
        print 'localSettingsFileTemplatePath=%s--' % localSettingsFileTemplatePath
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % dashboardConfFileDir)
        ####NEW
        ShellCmdExecutor.execCmd('cat %s > /tmp/local_settings' % localSettingsFileTemplatePath)
        ShellCmdExecutor.execCmd('cp -r /tmp/local_settings %s' % dashboardConfFileDir)
        ShellCmdExecutor.execCmd('rm -rf /tmp/local_settings')
        
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        print "keystone_vip=%s" % keystone_vip
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        localIP = output.strip()
        
        dashboard_ips_string = JSONUtility.getValue("dashboard_ips")
        dashboard_ip_list = dashboard_ips_string.split(',')
        memcached_service_list = []
        for ip in dashboard_ip_list:
            memcached_service_list.append(ip.strip() + ':11211')
            pass
        
        memcached_service_string = ','.join(memcached_service_list)
        print 'memcached_service_string=%s--' % memcached_service_string
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % Dashboard.DASHBOARD_CONF_FILE_PATH)
        FileUtil.replaceFileContent(Dashboard.DASHBOARD_CONF_FILE_PATH, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(Dashboard.DASHBOARD_CONF_FILE_PATH, '<LOCAL_MANAGEMENT_IP>', localIP)
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % Dashboard.DASHBOARD_CONF_FILE_PATH)
        
        #Assign rights: can be accessed
        DIR_PATH = '/usr/share/openstack-dashboard/openstack_dashboard/local'
        if os.path.exists(DIR_PATH) :
            ShellCmdExecutor.execCmd('sudo chmod 777 %s' % DIR_PATH)
            pass
        pass
    
    @staticmethod
    def configHttpdConfFile():
        httpdConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'dashboard', 'httpd.conf')
        if os.path.exists(Dashboard.HTTPD_CONF_FILE_PATH) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % Dashboard.HTTPD_CONF_FILE_PATH)
            pass
        
        httpdConfFileDir = os.path.dirname(Dashboard.HTTPD_CONF_FILE_PATH)
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (httpdConfFileTemplatePath, httpdConfFileDir))
        ShellCmdExecutor.execCmd("cat %s > /tmp/httpd.conf" % httpdConfFileTemplatePath)
        ShellCmdExecutor.execCmd("mv /tmp/httpd.conf /etc/httpd/conf/")
        
        #configure openstack-dashboard.conf
        dashboardConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'dashboard', 'openstack-dashboard.conf')
        if not os.path.exists('/etc/httpd/conf.d') :
            ShellCmdExecutor.execCmd('mkdir -p /etc/httpd/conf.d')
            pass
        
#         ShellCmdExecutor.execCmd("cp -r %s /etc/httpd/conf.d/" % dashboardConfFileTemplatePath)
        pass
    
    @staticmethod
    def configureDashboardRights():
#         if os.path.exists("/var/lib/openstack-dashboard") :
#             ShellCmdExecutor.execCmd("chmod 777 /var/lib/openstack-dashboard")
#             pass
#         
#         if os.path.exists("/usr/share/openstack-dashboard/openstack_dashboard/local") :
#             ShellCmdExecutor.execCmd("chmod 777 /usr/share/openstack-dashboard/openstack_dashboard/local")
#             pass
        pass
    pass

    
if __name__ == '__main__':
    
    print 'hello openstack-kilo:dashboard============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /etc/puppet/localip, these two files are generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/dashboard_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'dashboard installed####'
        print 'exit===='
        pass
    else :
        Dashboard.install()
        Dashboard.configure()
        
    #     Dashboard.start()
    #    
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:dashboard installed#######'
    pass

