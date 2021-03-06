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
        
        Dashboard.configHttpdConfFile()
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("service httpd start")
        ShellCmdExecutor.execCmd("service memcached start")
        ShellCmdExecutor.execCmd("chkconfig httpd on")
        ShellCmdExecutor.execCmd("chkconfig memcached on")
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd("service httpd restart")
        ShellCmdExecutor.execCmd("service memcached restart")
        pass
    
    
    @staticmethod
    def configConfFile():
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
        ShellCmdExecutor.execCmd('mv /tmp/local_settings %s' % dashboardConfFileDir)
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % Dashboard.DASHBOARD_CONF_FILE_PATH)
        FileUtil.replaceFileContent(Dashboard.DASHBOARD_CONF_FILE_PATH, '<KEYSTONE_VIP>', keystone_vip)
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
        
        ShellCmdExecutor.execCmd("cp -r %s /etc/httpd/conf.d/" % dashboardConfFileTemplatePath)
        pass
    
    @staticmethod
    def configureDashboardRights():
        if os.path.exists("/var/lib/openstack-dashboard") :
            ShellCmdExecutor.execCmd("chmod 777 /var/lib/openstack-dashboard")
            pass
        
        if os.path.exists("/usr/share/openstack-dashboard/openstack_dashboard/local") :
            ShellCmdExecutor.execCmd("chmod 777 /usr/share/openstack-dashboard/openstack_dashboard/local")
            pass
        pass
    pass


class DashboardHA(object):
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
        if DashboardHA.isExistVIP(vip, interface) :
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
        result = DashboardHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not DashboardHA.isExistVIP(vip, interface) :
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
        result = DashboardHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if DashboardHA.isExistVIP(vip, interface) :
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
            if not DashboardHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not DashboardHA.isHAProxyInstalled() :
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
                
                ShellCmdExecutor.execCmd('sudo chmod 777 /etc/haproxy')
#                 ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (haproxyTemplateFilePath, os.path.dirname(haproxyConfFilePath)))
                ShellCmdExecutor.execCmd('cat %s > /tmp/haproxy.cfg' % haproxyTemplateFilePath)
                ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
                pass
            pass
        pass
    
    @staticmethod
    def configure():
        DashboardHA.configureHAProxy()
        DashboardHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        dashboard_vip = JSONUtility.getValue("dashboard_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        HAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 /etc/haproxy')
        
        if not os.path.exists(haproxyConfFilePath) :
#             ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (HAProxyTemplateFilePath, '/etc/haproxy'))
            
            ShellCmdExecutor.execCmd('cat %s > /tmp/haproxy.cfg' % HAProxyTemplateFilePath)
            ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        ####
        ##############new
#         dashboardBackendStringTemplate = '''
# listen  localhost <DASHBOARD_VIP>:80
#   mode http
#   stats   uri  /haproxy
#   balance roundrobin
#   cookie  JSESSIONID prefix
#   stats   hide-version
#   option  httpclose
#   <DASHBOARD_SERVER_LIST>
#   '''
        
        dashboardBackendStringTemplate = '''
listen dashboard_cluster
  bind <DASHBOARD_VIP>:80
  balance source
  option tcpka
  option httpchk
  option tcplog
  <DASHBOARD_SERVER_LIST>
        '''
        ###############
        dashboardBackendString = dashboardBackendStringTemplate.replace('<DASHBOARD_VIP>', dashboard_vip)
        
        ################new
        dashboard_ips = JSONUtility.getValue("dashboard_ips")
        dashboard_ip_list = dashboard_ips.strip().split(',')
        serverDashboardBackendTemplate = 'server dashboard-<INDEX> <SERVER_IP>:8080 weight 3 check inter 2000 rise 2 fall 3'
        
        dashboardServerListContent = ''
        index = 1
        for dashboard_ip in dashboard_ip_list:
            print 'dashboard_ip=%s' % dashboard_ip
            dashboardServerListContent += serverDashboardBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', dashboard_ip)
            
            dashboardServerListContent += '\n'
            dashboardServerListContent += '  '

            index += 1
            pass
        
        dashboardServerListContent = dashboardServerListContent.strip()
        print 'dashboardServerListContent=%s--' % dashboardServerListContent
        
        dashboardBackendString = dashboardBackendString.replace('<DASHBOARD_SERVER_LIST>', dashboardServerListContent)
        
        print 'dashboardBackendString=%s--' % dashboardBackendString
        
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
        
        haproxyContent += dashboardBackendString
        
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
        
        ShellCmdExecutor.execCmd('chmod 777 /etc/keepalived')
        #configure haproxy check script in keepalived
        checkHAProxyScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (checkHAProxyScriptPath, '/etc/keepalived'))
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/check_haproxy.sh' % checkHAProxyScriptPath)
        ShellCmdExecutor.execCmd('mv /tmp/check_haproxy.sh /etc/keepalived/')
        
        if os.path.exists(keepalivedConfFilePath) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % keepalivedConfFilePath)
            pass
        
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (keepalivedTemplateFilePath, keepalivedConfFilePath))
        ShellCmdExecutor.execCmd('cat %s > /tmp/keepalived.conf' % keepalivedTemplateFilePath)
        ShellCmdExecutor.execCmd('mv /tmp/keepalived.conf /etc/keepalived/')
        
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
        dashboard_vip = JSONUtility.getValue("dashboard_vip")
        dashboard_vip_interface = JSONUtility.getValue("dashboard_vip_interface")
        
        weight_counter = 300
        
        ######
        if DashboardHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = DashboardHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass

        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', dashboard_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', dashboard_vip)
        
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
        print 'To get this host index of role %s==============' % "dashboard" 
        dashboard_ips = JSONUtility.getValue('dashboard_ips')
        dashboard_ip_list = dashboard_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'dashboard_ip_list=%s--------------' % dashboard_ip_list
        index = dashboard_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if DashboardHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            dashboard_vip_interface = JSONUtility.getValue("dashboard_vip_interface")
            dashboard_vip = JSONUtility.getValue("dashboard_vip")
            
            DashboardHA.addVIP(dashboard_vip, dashboard_vip_interface)
            
            if DashboardHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
#             DashboardHA.deleteVIP(dashboard_vip, dashboard_vip_interface)
            
            if DashboardHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            #Ensure only one VIP exists.
            isMasterNode = DashboardHA.isMasterNode()
            if isMasterNode == True :
                DashboardHA.restart()
                pass
            else :
                DashboardHA.deleteVIP(dashboard_vip, dashboard_vip_interface)
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
    
    print 'hello openstack-icehouse:dashboard============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /etc/puppet/localip, these two files are generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/dashboard_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'dashboard installed####'
        print 'exit===='
        exit()
        pass
    
    Dashboard.install()
    Dashboard.configure()
    
#     Dashboard.start()
# 
#     DashboardHA.install()
#     DashboardHA.configure()
#     DashboardHA.start()
    #
    ShellCmdExecutor.execCmd('service haproxy restart')
    #mark: dashboard is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:dashboard installed#######'
    pass

