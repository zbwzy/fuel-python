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

class KeystoneHAProxy(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def configureKeystoneHAProxy():
        keystone_vip = JSONUtility.getValue("keystone_vip")
        
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
        ##############new
        keystoneBackendAdminApiStringTemplate = '''
listen keystone_admin_cluster
  bind <KEYSTONE_VIP>:35357
  balance source
  <KEYSTONE_ADMIN_API_SERVER_LIST>
  '''
        keystoneBackendPublicApiStringTemplate = '''
listen keystone_public_internal_cluster
  bind <KEYSTONE_VIP>:5000
  <KEYSTONE_PUBLIC_API_SERVER_LIST>
  '''
        keystoneBackendAdminApiString = keystoneBackendAdminApiStringTemplate.replace('<KEYSTONE_VIP>', keystone_vip)
        keystoneBackendPublicApiString = keystoneBackendPublicApiStringTemplate.replace('<KEYSTONE_VIP>', keystone_vip)
        
        ################new
        keystone_ips = JSONUtility.getValue("keystone_ips")
        keystone_ip_list = keystone_ips.strip().split(',')
        
        serverKeystoneAdminAPIBackendTemplate   = 'server keystone-<INDEX> <SERVER_IP>:35357 check inter 2000 rise 2 fall 5'
        serverKeystonePublicAPIBackendTemplate  = 'server keystone-<INDEX> <SERVER_IP>:5000 check inter 2000 rise 2 fall 5'
        
        keystoneAdminAPIServerListContent = ''
        keystonePublicAPIServerListContent = ''
        
        index = 1
        for keystone_ip in keystone_ip_list:
            print 'keystone_ip=%s' % keystone_ip
            keystoneAdminAPIServerListContent += serverKeystoneAdminAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            keystonePublicAPIServerListContent += serverKeystonePublicAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            
            keystoneAdminAPIServerListContent += '\n'
            keystoneAdminAPIServerListContent += '  '
            
            keystonePublicAPIServerListContent += '\n'
            keystonePublicAPIServerListContent += '  '
            index += 1
            pass
        
        keystoneAdminAPIServerListContent = keystoneAdminAPIServerListContent.strip()
        keystonePublicAPIServerListContent = keystonePublicAPIServerListContent.strip()
        print 'keystoneAdminAPIServerListContent=%s--' % keystoneAdminAPIServerListContent
        print 'keystonePublicAPIServerListContent=%s--' % keystonePublicAPIServerListContent
        
        keystoneBackendAdminApiString = keystoneBackendAdminApiString.replace('<KEYSTONE_ADMIN_API_SERVER_LIST>', keystoneAdminAPIServerListContent)
        keystoneBackendPublicApiString = keystoneBackendPublicApiString.replace('<KEYSTONE_PUBLIC_API_SERVER_LIST>', keystonePublicAPIServerListContent)
        
        print 'keystoneBackendAdminApiString=%s--' % keystoneBackendAdminApiString
        print 'keystoneBackendPublicApiString=%s--' % keystoneBackendPublicApiString
        
        #append
        FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_ADMIN>', keystoneBackendAdminApiString)
        FileUtil.replaceFileContent(haproxyConfFilePath, '<KEYSTONE_PUBLIC>', keystoneBackendPublicApiString)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)



if __name__ == '__main__':
    KeystoneHAProxy.configureKeystoneHAProxy()
    pass
    
    
    pass