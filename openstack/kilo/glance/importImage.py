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

from openstack.kilo.glance.glance import Glance

    
if __name__ == '__main__':
    
    print 'hello openstack-kilo:importImageToGlance============'
    
    print 'start time: %s' % time.ctime()
    
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/imageImported'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'image imported####'
        print 'exit===='
        pass
    else :
        print 'start to import image======='
        imageFilePath = "/etc/puppet/modules/glance/files/cirros-0.3.4-x86_64-disk.img"
        admin_token = JSONUtility.getValue('admin_token')
        keystone_vip = JSONUtility.getValue('keystone_vip')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        
        if os.path.exists(imageFilePath) :
            import_image_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'import_image.sh')
            get_image_id_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'getDefaultImageID.sh')
            get_image_size_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'getDefaultImageFileSize.sh')
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts/' % import_image_script_path)
            ShellCmdExecutor.execCmd('chmod 777 /opt/openstack_conf/scripts/import_image.sh')
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % get_image_id_script_path)
            ShellCmdExecutor.execCmd('chmod 777 /opt/openstack_conf/scripts/getDefaultImageID.sh')
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts/' % get_image_size_script_path)
            ShellCmdExecutor.execCmd('chmod 777 /opt/openstack_conf/scripts/getDefaultImageFileSize.sh')
            
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/import_image.sh', '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/import_image.sh', '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/import_image.sh', '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/getDefaultImageID.sh', '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/getDefaultImageID.sh', '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/getDefaultImageID.sh', '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/getDefaultImageFileSize.sh', '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/getDefaultImageFileSize.sh', '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent('/opt/openstack_conf/scripts/getDefaultImageFileSize.sh', '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            time.sleep(1)
            
            from openstack.common.role import Role
            from openstack.common.serverSequence import ServerSequence
            glance_ips = JSONUtility.getValue('glance_ips')
            glance_ip_list = glance_ips.strip().split(',')
            output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
            localIP = output.strip()
            if Role.isGlanceRole() and ServerSequence.getIndex(glance_ip_list, localIP) == 0 :
                imported_tag = False
                retry = 1
                while retry > 0 :
                    ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/import_image.sh')
                    imageFileSize, exitcode = ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/getDefaultImageFileSize.sh')
                    imageID, exitcode = ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/getDefaultImageID.sh')
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
                    os.system('touch /opt/openstack_conf/tag/install/existGlanceFileOnHost')
                    pass
            
            os.system('touch %s' % INSTALL_TAG_FILE)
            pass
        else :
            print 'Do not exist file %s.' % imageFilePath
            pass
    
    print 'hello openstack-kilo:importImageToGlance#######'
    pass

