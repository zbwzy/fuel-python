'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python glance.py <LOCAL_IP>

NOTE: the params is from conf/params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time

debug = True
if debug :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-api.conf')
SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-registry.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    pass

class Glance(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Glance node install start========'
        #Enable later
#         yumCmd = "yum install openstack-glance python-glanceclient -y"
        yumCmd = "ls -lt"
        output, exitcode = ShellCmdExecutor.execCmd(yumCmd)
        print 'output=\n%s--' % output
        Glance.configConfFile()
        Glance.start()
        
        print 'Glance node install done####'
        pass
    
    @staticmethod
    def start():
        print "start glance========="
        
        print "start glance done####"
#         ShellCmdExecutor.execCmd("glance")
        pass
    
    @staticmethod
    def configConfFile():
        print "configure glance conf file======"
        glance_vip = JSONUtility.getValue("glance_vip")
        print "glance_vip=%s" % glance_vip
        glance_ips = JSONUtility.getValue("glance_ips")
        print "glance_ips=%s" % glance_ips
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        glanceConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'GLANCE_CONF_DIR')
        print 'glanceConfDir=%s' % glanceConfDir #/etc/glance
        
        glance_api_conf_file_path = os.path.join(glanceConfDir, 'glance-api.conf')
        glance_registry_conf_file_path = os.path.join(glanceConfDir, 'glance-registry.conf')
        
        if not os.path.exists(glanceConfDir) :
            os.system("sudo mkdir -p %s" % glanceConfDir)
            pass
        #if exist, remove original conf files
        if os.path.exists(glance_api_conf_file_path) :
            os.system("sudo rm -rf %s" % glance_api_conf_file_path)
            pass
        
        if os.path.exists(glance_registry_conf_file_path) :
            os.system("sudo rm -rf %s" % glance_registry_conf_file_path)
            pass
        
        os.system("sudo cp -rf %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        os.system("sudo cp -rf %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        pass
    
    
    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:glance============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path> LOCAL_IP GLANCE_USER_EMAIL NOVA_USER_EMAIL
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
    
    Glance.install()
    Glance.configConfFile()
    print 'LOCAL_IP=%s' % LOCAL_IP
    print 'hello openstack-icehouse:glance#######'
    pass

