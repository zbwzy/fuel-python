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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class GlanceHAProxy(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def configureKeystoneHAProxy():
        glance_vip = JSONUtility.getValue("glance_vip")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        glanceHAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (glanceHAProxyTemplateFilePath, haproxyConfFilePath))
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        glance_ips = JSONUtility.getValue("glance_ips")
        glance_ip_list = glance_ips.strip().split(',')
        
        glanceBackendApiStringTemplate = '''
listen glance_api_cluster
  bind <GLANCE_VIP>:9292
  balance source
  <GLANCE_API_SERVER_LIST>
  '''
        glanceBackendRegistryApiStringTemplate = '''
listen glance_registry_cluster
  bind <GLANCE_VIP>:9191
  balance source
  <GLANCE_REGISTRY_API_SERVER_LIST>
        '''
        
        glanceBackendApiString = glanceBackendApiStringTemplate.replace('<GLANCE_VIP>', glance_vip)
        
        glanceBackendRegistryApiString = glanceBackendRegistryApiStringTemplate.replace('<GLANCE_VIP>', glance_vip)
        ###############
        
        serverGlanceRegistryAPIBackendTemplate = 'server glance-<INDEX> <SERVER_IP>:9191 check inter 2000 rise 2 fall 5'
        serverGlanceAPIBackendTemplate         = 'server glance-<INDEX> <SERVER_IP>:9292 check inter 2000 rise 2 fall 5'
        
        glanceRegistryAPIServerListContent = ''
        glanceAPIServerListContent = ''
        
        index = 1
        for glance_ip in glance_ip_list:
            print 'glance_ip=%s' % glance_ip
            glanceRegistryAPIServerListContent += serverGlanceRegistryAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            glanceAPIServerListContent += serverGlanceAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            
            glanceRegistryAPIServerListContent += '\n'
            glanceRegistryAPIServerListContent += '  '
            
            glanceAPIServerListContent += '\n'
            glanceAPIServerListContent += '  '
            
            index += 1
            pass
        
        glanceRegistryAPIServerListContent = glanceRegistryAPIServerListContent.strip()
        glanceAPIServerListContent = glanceAPIServerListContent.strip()
        print 'glanceRegistryAPIServerListContent=%s--' % glanceRegistryAPIServerListContent
        print 'glanceAPIServerListContent=%s--' % glanceAPIServerListContent
        
        glanceBackendRegistryApiString = glanceBackendRegistryApiString.replace('<GLANCE_REGISTRY_API_SERVER_LIST>', glanceRegistryAPIServerListContent)
        
        glanceBackendApiString = glanceBackendApiString.replace('<GLANCE_API_SERVER_LIST>', glanceAPIServerListContent)
        #append
        FileUtil.replaceFileContent(haproxyConfFilePath, '<GLANCE_API>', glanceBackendApiString)
        FileUtil.replaceFileContent(haproxyConfFilePath, '<GLANCE_REGISTRY>', glanceBackendRegistryApiString)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)



if __name__ == '__main__':
    GlanceHAProxy.configureKeystoneHAProxy()
    pass
    
    
