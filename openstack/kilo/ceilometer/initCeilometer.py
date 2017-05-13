'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python initCeilometer.py

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

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.icehouse.ceilometer.ceilometer import Ceilometer
from common.openfile.OpenFile import OpenFile


if __name__ == '__main__':
    
    print 'hello openstack-kilo:ceilometer============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/initCeilometer'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'ceilometer initted####'
        print 'exit===='
    else :
        #mark: ceilometer is installed
#         OpenFile.execModification('/usr/lib/systemd/system', 'openstack-')
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:ceilometer#######'
    pass

