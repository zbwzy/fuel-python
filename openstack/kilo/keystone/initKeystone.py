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
from common.yaml.YAMLUtil import YAMLUtil

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
        InitKeystone.initKeystoneUser()
        InitKeystone.initKeystone()
        
        InitKeystone.initGlanceUser()
        InitKeystone.initGlance()
        
        InitKeystone.initNovaUser()
        InitKeystone.initNova()
        
        InitKeystone.initNeutronUser()
        InitKeystone.initNeutron()
        
        InitKeystone.initCinderUser()
        InitKeystone.initCinderInternalTenantUser()
        InitKeystone.initCinder()
        
        if YAMLUtil.hasRoleInNodes('ceilometer') :
            InitKeystone.initCeilometerUser()
            InitKeystone.initGnocchiUser()
            
            InitKeystone.initCeilometer()
            InitKeystone.initGnocchi()
            
        pass
        
    
    @staticmethod
    def initOpenstackComponentToKeystone(scriptPath, userPassword):
        #for the cmd: 
        '''
openstack user create --password-prompt <USER_NAME>
User Password:
Repeat User Password:
        '''
        try:
            import pexpect
            #To make the interact string: Are you sure you want to continue connecting.* always appear
            cmd = 'bash %s' % scriptPath
            child = pexpect.spawn(cmd)
              
            #When do the first shell cmd execution, this interact message is appeared on shell.
            child.expect('User Password:')
            child.sendline(userPassword)
              
            child.expect('Repeat User Password:')
            child.sendline(userPassword)
      
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
    def initKeystoneUser(): #init all component's user/password/project/endpoint in keystone
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
 
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_ip = YAMLUtil.getManagementIP() 
        if Keystone.getServerIndex() == 0 :
            initKeystoneScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'initKeystoneUser.sh')
            if not os.path.exists('/opt/openstack_conf/scripts') :
                os.system('mkdir -p /opt/openstack_conf/scripts')
                pass
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % initKeystoneScriptPath)
            
            initKeystoneDestFilePath = '/opt/openstack_conf/scripts/initKeystoneUser.sh'
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<KEYSTONE_IP>', keystone_ip)
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            time.sleep(3)
#             output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initKeystoneDestFilePath)
            InitKeystone.initOpenstackComponentToKeystone(initKeystoneDestFilePath, keystone_admin_password)
    
    @staticmethod
    def initGlanceUser():
        #to replace in template: KEYSTONE_ADMIN_PASSWORD KEYSTONE_VIP KEYSTONE_GLANCE_PASSWORD GLANCE_VIP
        print 'to init glance user here==================='
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_glance_password = JSONUtility.getValue('keystone_glance_password')
        
        glance_vip = vipParamsDict["glance_vip"]
        
        initGlanceScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'initGlanceUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initGlanceScriptTemplatePath, openstackScriptDirPath))
        
        initGlanceScriptPath = os.path.join(openstackScriptDirPath, 'initGlanceUser.sh')
        FileUtil.replaceFileContent(initGlanceScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<GLANCE_VIP>', glance_vip)
#         output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initGlanceScriptPath)
        print 'to init glance user============'
        InitKeystone.initOpenstackComponentToKeystone(initGlanceScriptPath, keystone_glance_password)
        print 'end to init glance user#####'
        pass
    
    @staticmethod
    def initNovaUser():
        #to replace in template: KEYSTONE_ADMIN_PASSWORD KEYSTONE_VIP KEYSTONE_NOVA_PASSWORD NOVA_VIP
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        
        keystone_nova_password = JSONUtility.getValue('keystone_nova_password')
        
        
        nova_vip = vipParamsDict["nova_vip"]
        initNovaScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'initNovaUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initNovaScriptTemplatePath, openstackScriptDirPath))
        
        initNovaScriptPath = os.path.join(openstackScriptDirPath, 'initNovaUser.sh')
        FileUtil.replaceFileContent(initNovaScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initNovaScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initNovaScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initNovaScriptPath, '<NOVA_VIP>', nova_vip)
#         ShellCmdExecutor.execCmd('bash %s' % initNovaScriptPath)
        InitKeystone.initOpenstackComponentToKeystone(initNovaScriptPath, keystone_nova_password)
        pass
    
    @staticmethod
    def initNeutronUser():
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict['keystone_vip']
        keystone_neutron_password = JSONUtility.getValue('keystone_neutron_password')
        neutron_vip = vipParamsDict['neutron_vip']
        
        initNeutronScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'initNeutronUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initNeutronScriptTemplatePath, openstackScriptDirPath))
        
        initNeutronScriptPath = os.path.join(openstackScriptDirPath, 'initNeutronUser.sh')
        FileUtil.replaceFileContent(initNeutronScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initNeutronScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initNeutronScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initNeutronScriptPath, '<NEUTRON_VIP>', neutron_vip)
#         output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initNeutronScriptPath)
        InitKeystone.initOpenstackComponentToKeystone(initNeutronScriptPath, keystone_neutron_password)
        pass
    
    @staticmethod
    def initCinderUser():
        admin_token = JSONUtility.getValue('admin_token')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_cinder_password = JSONUtility.getValue('keystone_cinder_password')
        cinder_vip = vipParamsDict['cinder_vip']
        
        initCinderScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'initCinderUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initCinderScriptTemplatePath, openstackScriptDirPath))
        
        initCinderScriptPath = os.path.join(openstackScriptDirPath, 'initCinderUser.sh')
        FileUtil.replaceFileContent(initCinderScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initCinderScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initCinderScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initCinderScriptPath, '<CINDER_VIP>', cinder_vip)
#         ShellCmdExecutor.execCmd('bash %s' % initCinderScriptPath)
        InitKeystone.initOpenstackComponentToKeystone(initCinderScriptPath, keystone_cinder_password)
        pass
    
    @staticmethod
    def initCinderInternalTenantUser():
        admin_token = JSONUtility.getValue('admin_token')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_cinder_internal_tenant_password = JSONUtility.getValue('keystone_cinder_internal_tenant_password')
        cinder_vip = vipParamsDict['cinder_vip']
        
        initCinderScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'initCinderInternalTenantUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initCinderScriptTemplatePath, openstackScriptDirPath))
        
        initCinderScriptPath = os.path.join(openstackScriptDirPath, 'initCinderInternalTenantUser.sh')
        FileUtil.replaceFileContent(initCinderScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initCinderScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initCinderScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initCinderScriptPath, '<CINDER_VIP>', cinder_vip)
#         ShellCmdExecutor.execCmd('bash %s' % initCinderScriptPath)
        InitKeystone.initOpenstackComponentToKeystone(initCinderScriptPath, keystone_cinder_internal_tenant_password)
        pass
    
    @staticmethod
    def initCeilometerUser():
        admin_token = JSONUtility.getValue('admin_token')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_ceilometer_password = JSONUtility.getValue('keystone_ceilometer_password')
        ceilometer_vip = vipParamsDict['ceilometer_vip']
        
        initCeilometerScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'initCeilometerUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initCeilometerScriptTemplatePath, openstackScriptDirPath))
        
        initCeilometerScriptPath = os.path.join(openstackScriptDirPath, 'initCeilometerUser.sh')
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<CEILOMETER_VIP>', ceilometer_vip)
#         ShellCmdExecutor.execCmd('bash %s' % initCinderScriptPath)
        InitKeystone.initOpenstackComponentToKeystone(initCeilometerScriptPath, keystone_ceilometer_password)
        pass
    
    @staticmethod
    def initGnocchiUser():
        admin_token = JSONUtility.getValue('admin_token')
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_gnocchi_password = JSONUtility.getValue('keystone_gnocchi_password')
        gnocchi_vip = vipParamsDict['gnocchi_vip']
        
        initGnocchiScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'initGnocchiUser.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initGnocchiScriptTemplatePath, openstackScriptDirPath))
        
        initGnocchiScriptPath = os.path.join(openstackScriptDirPath, 'initGnocchiUser.sh')
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        InitKeystone.initOpenstackComponentToKeystone(initGnocchiScriptPath, keystone_gnocchi_password)
        pass
    
    ######
    @staticmethod
    def initKeystone(): #init all component's user/password/project/endpoint in keystone
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_vip = vipParamsDict['keystone_vip']
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_ip = YAMLUtil.getManagementIP() 
        if Keystone.getServerIndex() == 0 :
            initKeystoneScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone', 'initKeystone.sh')
            if not os.path.exists('/opt/openstack_conf/scripts') :
                os.system('mkdir -p /opt/openstack_conf/scripts')
                pass
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % initKeystoneScriptPath)
            
            initKeystoneDestFilePath = '/opt/openstack_conf/scripts/initKeystone.sh'
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<KEYSTONE_VIP>', keystone_vip)
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<ADMIN_TOKEN>', admin_token)
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<KEYSTONE_IP>', keystone_ip)
            FileUtil.replaceFileContent(initKeystoneDestFilePath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
            time.sleep(1)
            output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initKeystoneDestFilePath)
            print 'initKeystone.output=%s' % output
            pass
        pass
    
    @staticmethod
    def initGlance():
        #to replace in template: KEYSTONE_ADMIN_PASSWORD KEYSTONE_VIP KEYSTONE_GLANCE_PASSWORD GLANCE_VIP
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_glance_password = JSONUtility.getValue('keystone_glance_password')
        glance_vip = vipParamsDict['glance_vip']
        
        initGlanceScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'initGlance.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initGlanceScriptTemplatePath, openstackScriptDirPath))
        
        initGlanceScriptPath = os.path.join(openstackScriptDirPath, 'initGlance.sh')
        FileUtil.replaceFileContent(initGlanceScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initGlanceScriptPath, '<GLANCE_VIP>', glance_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initGlanceScriptPath)
        print 'output=%s' % output
        pass
    
    @staticmethod
    def initNova():
        #to replace in template: KEYSTONE_ADMIN_PASSWORD KEYSTONE_VIP KEYSTONE_NOVA_PASSWORD NOVA_VIP
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_nova_password = JSONUtility.getValue('keystone_nova_password')
        nova_vip = vipParamsDict['nova_vip']
        
        initNovaScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-api', 'initNova.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initNovaScriptTemplatePath, openstackScriptDirPath))
        
        initNovaScriptPath = os.path.join(openstackScriptDirPath, 'initNova.sh')
        FileUtil.replaceFileContent(initNovaScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initNovaScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initNovaScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initNovaScriptPath, '<NOVA_VIP>', nova_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initNovaScriptPath)
        print 'output=%s' % output
        pass
    
    @staticmethod
    def initNeutron():
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_neutron_password = JSONUtility.getValue('keystone_neutron_password')
        neutron_vip = vipParamsDict["neutron_vip"]
        
        initNeutronScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'initNeutron.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initNeutronScriptTemplatePath, openstackScriptDirPath))
        
        initNeutronScriptPath = os.path.join(openstackScriptDirPath, 'initNeutron.sh')
        FileUtil.replaceFileContent(initNeutronScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initNeutronScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initNeutronScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initNeutronScriptPath, '<NEUTRON_VIP>', neutron_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initNeutronScriptPath)
        print 'output=%s' % output
        pass
    
    @staticmethod
    def initCinder():
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_cinder_password = JSONUtility.getValue('keystone_cinder_password')
        cinder_vip = vipParamsDict["cinder_vip"]
        
        initCinderScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'initCinder.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initCinderScriptTemplatePath, openstackScriptDirPath))
        
        initCinderScriptPath = os.path.join(openstackScriptDirPath, 'initCinder.sh')
        FileUtil.replaceFileContent(initCinderScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initCinderScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initCinderScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initCinderScriptPath, '<CINDER_VIP>', cinder_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initCinderScriptPath)
        print 'output=%s' % output
        pass
    
    @staticmethod
    def initCeilometer():
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_ceilometer_password = JSONUtility.getValue('keystone_ceilometer_password')
        ceilometer_vip = vipParamsDict["ceilometer_vip"]
        
        initCeilometerScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'initCeilometer.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initCeilometerScriptTemplatePath, openstackScriptDirPath))
        
        initCeilometerScriptPath = os.path.join(openstackScriptDirPath, 'initCeilometer.sh')
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initCeilometerScriptPath, '<CEILOMETER_VIP>', ceilometer_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initCeilometerScriptPath)
        print 'output=%s' % output
        pass
    
    @staticmethod
    def initGnocchi():
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_gnocchi_password = JSONUtility.getValue('keystone_gnocchi_password')
        gnocchi_vip = vipParamsDict["gnocchi_vip"]
        
        initGnocchiScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'initGnocchi.sh')
        ##
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackScriptDirPath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_SCRIPT_DIR')
        if os.path.exists(openstackScriptDirPath) :
            os.system('mkdir -p %s' % openstackScriptDirPath)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (initGnocchiScriptTemplatePath, openstackScriptDirPath))
        
        initGnocchiScriptPath = os.path.join(openstackScriptDirPath, 'initGnocchi.sh')
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(initGnocchiScriptPath, '<GNOCCHI_VIP>', gnocchi_vip)
        output, exitcode = ShellCmdExecutor.execCmd('bash %s' % initGnocchiScriptPath)
        print 'output=%s' % output
        pass


if __name__ == '__main__':
    
    print 'hello openstack-kilo:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/init_keystone'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'keystone initted####'
        print 'exit===='
    else :
        from openstack.kilo.keystone.keystone import Keystone
        if Keystone.getServerIndex() == 0 :
            Keystone.importKeystoneDBSchema()
            Keystone.start()
            time.sleep(10)
            InitKeystone.init()
            #set ntp server
            time.sleep(1)
            
            from common.ntp.NTPService import NTPService
            ntp_enabled = YAMLUtil.getValue('ntp', 'enable')
            if ntp_enabled == False :
                #defaulty,choose the first keystone(uuid is  the smallest) as ntp server
                #set ntp server
                NTPService.setNTPServer()
                pass
            else :
                ntp_server_ip = YAMLUtil.getValue('ntp', 'ntp_server_ip')
                NTPService.setNTPClient(ntp_server_ip)
                pass
            pass
        else :
            ShellCmdExecutor.execCmd('chmod 777 /etc/keystone')
            
            #wait the file /etc/keystone/fernet-keys produced on first keystone
            '''
            /opt/openstack_conf/tag/keystone_0_fernet
            '''
            Keystone.scpFernetKeys()
            time.sleep(5)
#             TIMEOUT = 600
#             timeout = TIMEOUT
#             time_count = 0
#             while True:
# #                 launchedMysqlServerNum = Keystone.getLaunchedRDBServersNum()
#                 cmd = 'ls -lt /opt/openstack_conf/tag/ | grep keystone_0_fernet | wc -l'
#                 output, exitcode = ShellCmdExecutor.execCmd(cmd)
#                 fernet_file_tag = output.strip()
#                 if str(fernet_file_tag) == "1" :
#                     print 'wait time: %s second(s).' % time_count
#                     Keystone.scpSSL()
#                     time.sleep(5)
#                     break
#                 else :
#                     step = 1
#         #             print 'wait %s second(s)......' % step
#                     time_count += step
#                     time.sleep(1)
#                     pass
#                  
#                 if time_count == timeout :
#                     print 'Do nothing!timeout=%s.' % timeout
#                     break
#                 pass
            
            cmd1 = 'chown -R keystone:keystone /var/log/keystone'
            cmd2 = 'chown -R keystone:keystone /etc/keystone/fernet-keys'
            cmd3 = 'chmod -R o-rwx /etc/keystone/fernet-keys'
            ShellCmdExecutor.execCmd(cmd1)
            ShellCmdExecutor.execCmd(cmd2)
            ShellCmdExecutor.execCmd(cmd3)
            
            Keystone.start()
            pass
        
        from common.openfile.OpenFile import OpenFile
        OpenFile.execModificationBy('/usr/lib/systemd/system', 'httpd.service')
        #mark: keystone is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:keystone#######'
    pass

