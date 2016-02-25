'''
Created on Dec 15, 2015

@author: zhangbai
'''

'''
usage:

python initOSTF.py

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
from openstack.common.role import Role

    
if __name__ == '__main__':
    print 'hello openstack-icehouse:init ostf============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    if Role.isGlanceRole() :
        IMAGE_INSTALL_TAG_FILE = '/opt/initOSTFGlancePrivilege'
        if os.path.exists(IMAGE_INSTALL_TAG_FILE) :
            print 'ostf glance image privilege initted####'
            print 'exit===='
            pass
        else :
#             listImageFileCmd = 'ls /var/lib/glance/images/'
#             output, exitcode = ShellCmdExecutor.execCmd(listImageFileCmd)
#             output, exitcode = ShellCmdExecutor.execCmd('bash /opt/getDefaultImageID.sh')
#             imageFileName = output.strip()
#             imageFilePath = os.path.join('/var/lib/glance/images', imageFileName)
            
            time.sleep(5)
            imageFileDir = '/var/lib/glance/images/'
            output, exitcode = ShellCmdExecutor.execCmd('chown -R glance:glance %s' % imageFileDir)
            os.system('touch %s' % IMAGE_INSTALL_TAG_FILE)
            pass
        pass
    print 'hello ostf glance image privilege initted#######'
    pass


