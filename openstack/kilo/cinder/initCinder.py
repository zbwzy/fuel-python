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


from openstack.kilo.cinder.cinder import Cinder
    
if __name__ == '__main__':
    print 'hello openstack-kilo:cinder============'
    print 'start time: %s' % time.ctime()
#     dbSchema_init_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'cinder_dbschema_init.sh')
#     print 'dbSchema_init_script_path=%s' % dbSchema_init_script_path
#     ShellCmdExecutor.execCmd('cp -r %s /opt/' % dbSchema_init_script_path)
#     ShellCmdExecutor.execCmd('bash /opt/cinder_dbschema_init.sh')
#     exit()
    
    debug = False
    if debug :
        print 'start to debug======'
        print 'end debug######'
        exit()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/init_cinder'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'cinder initted####'
        print 'exit===='
        pass
    else :
    #     Cinder.install()
    #     Cinder.configConfFile()
    
        #Cinder DB Schema
#         if CinderHA.isMasterNode() :
#             dbSchema_init_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'cinder_dbschema_init.sh')
#             ShellCmdExecutor.execCmd('cp -r %s /opt/' % dbSchema_init_script_path)
# #             ShellCmdExecutor.execCmd('bash /opt/cinder_dbschema_init.sh')
#             pass
        if Cinder.getServerIndex() == 0:
            Cinder.importCinderDBSchema()
            pass
        
        Cinder.start()
    #     os.system("service openstack-cinder-api start")
    #     os.system("service openstack-cinder-scheduler start")
    #     os.system("service haproxy restart")
        #mark: cinder is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello cinder initted#######'
    pass
