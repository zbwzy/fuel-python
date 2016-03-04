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

OPENSTACK_VERSION_TAG = 'kilo'
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
        imageFilePath = "/etc/puppet/modules/glance/files/cirros-0.3.1-x86_64-disk.img"
        keystone_vip = JSONUtility.getValue('keystone_vip')
        if os.path.exists(imageFilePath) :
            import_image_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'import_image.sh')
            get_image_id_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'getDefaultImageID.sh')
            get_image_size_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'getDefaultImageFileSize.sh')
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/' % import_image_script_path)
            ShellCmdExecutor.execCmd('chmod 777 /opt/import_image.sh')
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/' % get_image_id_script_path)
            ShellCmdExecutor.execCmd('chmod 777 /opt/getDefaultImageID.sh')
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/' % get_image_size_script_path)
            ShellCmdExecutor.execCmd('chmod 777 /opt/getDefaultImageFileSize.sh')
            
            FileUtil.replaceFileContent('/opt/import_image.sh', '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent('/opt/getDefaultImageID.sh', '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent('/opt/getDefaultImageFileSize.sh', '<KEYSTONE_VIP>', keystone_vip)
            time.sleep(1)
            
            from openstack.common.role import Role
            if Role.isGlanceRole() and GlanceHA.isMasterNode():
#             if GlanceHA.isMasterNode() :
                imported_tag = False
                retry = 1
                while retry > 0 :
                    ShellCmdExecutor.execCmd('bash /opt/import_image.sh')
                    imageFileSize, exitcode = ShellCmdExecutor.execCmd('bash /opt/getDefaultImageFileSize.sh')
                    imageID, exitcode = ShellCmdExecutor.execCmd('bash /opt/getDefaultImageID.sh')
                    importedImageSizeCmd = "ls -lt /etc/puppet/modules/glance/files/ | grep cirros | awk '{print $5}'"
                    importedImageSize, exitcode = ShellCmdExecutor.execCmd(importedImageSizeCmd)
                    imageID = imageID.strip()
                    imageFileSize = imageFileSize.strip()
                    importedImageSize = importedImageSize.strip()
                    
                    if imageFileSize == importedImageSize :
                        imported_tag = True
                        break
                        pass
                    
                    retry -= 1
                    pass
                
                if imported_tag == True :
                    print 'Success to import image.'
                else :
                    print 'Fail to import image.'
                pass
            
            if Role.isGlanceRole() :
                listImageFileCmd = 'ls /var/lib/glance/images/'
                output, exitcode = ShellCmdExecutor.execCmd(listImageFileCmd)
                output = output.strip()
                
                existImageFlag = True
                if output == '' :
                    existImageFlag = False
                    pass
                
                if existImageFlag :
                    os.system('touch /opt/existGlanceFileOnHost')
                    pass
            
            os.system('touch %s' % INSTALL_TAG_FILE)
            pass
        else :
            print 'Do not exist file %s.' % imageFilePath
            pass
    
    print 'hello openstack-icehouse:importImageToGlance#######'
    pass

