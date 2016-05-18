'''
Created on Feb 29, 2016

@author: zhangbai
'''

'''
usage:

python bcrdb.py

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
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil
from openstack.common.serverSequence import ServerSequence

class AdminOpenrc(object):
    '''
    classdocs
    '''
    ROLE = 'mysql'
    TIMEOUT = 600 #unit:second
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def prepareAdminOpenrc():
        adminOpenrcTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'admin-openrc.sh')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf' % adminOpenrcTemplateFilePath)
        
        admin_token = JSONUtility.getValue('admin_token')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        
        FileUtil.replaceFileContent('/opt/openstack_conf/admin-openrc.sh', '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent('/opt/openstack_conf/admin-openrc.sh', '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent('/opt/openstack_conf/admin-openrc.sh', '<KEYSTONE_VIP>', keystone_vip)
        pass
    
    

if __name__ == '__main__':
        
    print 'hello openstack-kilo:cp admin-openrc======='
   
    print 'hello openstack-kilo:cp admin-openrc#######'
    pass

