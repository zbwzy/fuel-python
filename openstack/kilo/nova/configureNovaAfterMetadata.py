'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python cinder.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time

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


if __name__ == '__main__':
    print 'hello openstack-icehouse:confiugre nova after metadata agent============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    TAG_FILE = '/opt/configureNovaAfterMetadata'
    if os.path.exists(TAG_FILE) :
        print 'When configure metadata-agent on neutron-agent, nova configured####'
        print 'exit===='
        pass
    else :
        print 'When configure metadata-agent on neutron-agent, start to configure nova-api========='
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        neutron_vip = vipParamsDict["neutron_vip"]
        
        network_node_params_dict = JSONUtility.getRoleParamsDict('network')
        metadata_secret = network_node_params_dict["metadata_secret"]
        
        #MetadataConfiguration
        metadata_configuration = '''
service_metadata_proxy = True
metadata_proxy_shared_secret = <METADATA_SECRET>
        '''
        
        metadata_configuration = metadata_configuration.strip()
        metadata_configuration = metadata_configuration.replace('<METADATA_SECRET>', metadata_secret)
        
        NOVA_API_CONF_FILE_PATH = '/etc/nova/nova.conf'
        FileUtil.replaceFileContent(NOVA_API_CONF_FILE_PATH, '#MetadataConfiguration', metadata_configuration)
        ShellCmdExecutor.execCmd('service openstack-nova-api restart')
        
        os.system('touch %s' % TAG_FILE)
        pass
    print 'Nova is configured after metadata configured#######'
    pass

