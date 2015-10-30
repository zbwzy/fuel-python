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

class DashboardHAProxy(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def configureKeystoneHAProxy():
        dashboard_vip = JSONUtility.getValue("dashboard_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        HAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (HAProxyTemplateFilePath, haproxyConfFilePath))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
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
        FileUtil.replaceFileContent(haproxyConfFilePath, '<DASHBOARD_LIST>', dashboardBackendString)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)


if __name__ == '__main__':
    DashboardHAProxy.configureKeystoneHAProxy()
    pass