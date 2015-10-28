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
        Dashboard.configConfFile()
        
        #assign network connect
        ShellCmdExecutor.execCmd("setsebool -P httpd_can_network_connect on")
        Dashboard.start()
        print 'Dashboard.install done####'
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd("service httpd restart")
        ShellCmdExecutor.execCmd("service memcached restart")
        ShellCmdExecutor.execCmd("chkconfig httpd on")
        ShellCmdExecutor.execCmd("chkconfig memcached on")
        pass
    
    
    @staticmethod
    def configConfFile():
        '''
CACHES = {
'default': {
'BACKEND' : 'django.core.cache.backends.memcached.MemcachedCache',
'LOCATION' : '127.0.0.1:11211'
}
}
ALLOWED_HOSTS = ['localhost','my-desktop','*','0.0.0.0']
OPENSTACK_HOST = "controller"
        '''
        pass
    pass

    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:dashboard============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /etc/puppet/localip, these two files are generated in init.pp in site.pp.
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
    INSTALL_TAG_FILE = '/opt/dashboard_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'dashboard installed####'
        print 'exit===='
        exit()
        pass
    
    Dashboard.install()
    #
    #mark: nova-compute is installed
    os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:dashboard installed#######'
    pass

