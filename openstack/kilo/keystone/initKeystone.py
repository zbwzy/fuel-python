'''
Created on Aug 26, 2015

@author: zhangbai
'''

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

from openstack.kilo.keystone.keystone import Keystone

class InitKeystone(object):
    '''
    classdocs
    '''
    TIMEOUT = 600 #unit:second
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def init():
        InitKeystone.initKeystone()
        InitKeystone.initGlance()
        pass
    
    @staticmethod
    def initKeystone():
        admin_token = JSONUtility.getValue('admin_token')
        keystone_vip = JSONUtility.getValue('keystone_vip')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        if Keystone.getServerIndex() == 0 :
            output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
            keystone_ip = output.strip()
            
            initKeystoneScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'initKeystone.sh')
            
            if not os.path.exists('/opt/openstack_conf/scripts') :
                os.system('mkdir -p /opt/openstack_conf/scripts')
                pass
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % initKeystoneScriptPath)
            
            try:
                import pexpect
                #To make the interact string: Are you sure you want to continue connecting.* always appear
                if os.path.exists('/root/.ssh/known_hosts') :
                    os.system('rm -rf /root/.ssh/known_hosts')
                    pass
        
        #         child = pexpect.spawn(scpCmd)
                cmd = 'bash %s' % initKeystoneScriptPath
                child = pexpect.spawn(cmd)
                
                #When do the first shell cmd execution, this interact message is appeared on shell.
                child.expect('User Password:')
                child.sendline(keystone_admin_password)
                
                child.expect('Repeat User Password:')
                child.sendline(keystone_admin_password)
        
                while True :
                    regex = "[\\s\\S]*" #match any
                    index = child.expect([regex , pexpect.EOF, pexpect.TIMEOUT])
                    if index == 0:
                        break
                    elif index == 1:
                        pass   #continue to wait
                    elif index == 2:
                        pass   #continue to wait
        
                child.sendline('exit')
                child.sendcontrol('c')
                #child.interact()
            except OSError:
                print 'Catch exception %s when send tag.' % OSError.strerror
                sys.exit(0)
            pass
        
        pass
    
    @staticmethod
    def initGlance():
        #to replace in template: KEYSTONE_ADMIN_PASSWORD KEYSTONE_VIP KEYSTONE_GLANCE_PASSWORD GLANCE_VIP
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = JSONUtility.getValue('keystone_vip')
        keystone_glance_password = JSONUtility.getValue('keystone_glance_password')
        glance_vip = JSONUtility.getValue('glance_vip')
        
        initGlanceScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'initGlance.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initGlanceScriptTemplatePath, openstackScriptDirPath))
        
        initGlanceScriptPath = os.path.join(openstackScriptDirPath, 'initGlance.sh')
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_GLANCE_PASSWORD>', keystone_glance_password)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<GLANCE_VIP>', glance_vip)
        ShellCmdExecutor.execCmd('bash %s' % initGlanceScriptPath)
        pass


if __name__ == '__main__':
    
    print 'hello openstack-kilo:keystone============'
    
    print 'start time: %s' % time.ctime()
    InitKeystone.initGlance()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/initKeystone'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'keystone initted####'
        print 'exit===='
    else :
        
        #mark: keystone is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:keystone#######'
    pass

