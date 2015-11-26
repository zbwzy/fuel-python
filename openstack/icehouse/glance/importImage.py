'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

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
SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-api.conf')
SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance-registry.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.icehouse.glance.glance import Glance
from openstack.icehouse.glance.glance import GlanceHA

    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:importImageToGlance============'
    
    print 'start time: %s' % time.ctime()
    
    INSTALL_TAG_FILE = '/opt/imageImported'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'image imported####'
        print 'exit===='
        pass
    else :
        print 'start to import image======='
        imageFilePath = "/opt/openstack_image/cirros-0.3.0-x86_64-disk.img"
        keystone_vip = JSONUtility.getValue('keystone_vip')
        if os.path.exists(imageFilePath) :
            if GlanceHA.isMasterNode() :
                import_image_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'import_image.sh')
                ShellCmdExecutor.execCmd('cp -r %s /opt/' % import_image_script_path)
                
                FileUtil.replaceFileContent('/opt/import_image.sh', '<KEYSTONE_VIP>', keystone_vip)
                ShellCmdExecutor.execCmd('bash /opt/import_image.sh')
                pass
            pass
        else :
            print 'Do not exist file %s.' % imageFilePath
            pass
    
    print 'hello openstack-icehouse:importImageToGlance#######'
    pass

