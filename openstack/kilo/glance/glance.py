'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python glance.py

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
SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'glance-api.conf')
SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'glance', 'glance-registry.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil
from openstack.common.serverSequence import ServerSequence
from openstack.kilo.ssh.SSH import SSH


class Glance(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Glance node install start========'
        #Enable 
        if debug == True:
            print 'DEBUG is True.On local dev env, do test====='
            yumCmd = "ls -lt"
        else :
            yumCmd = "yum install openstack-glance python-glance python-glanceclient -y"
            
        output, exitcode = ShellCmdExecutor.execCmd(yumCmd)
        print 'output=\n%s--' % output
        Glance.configConfFile()
        
        print 'Glance node install done####'
        pass
    
    @staticmethod
    def start():
        print "start glance========="
        ShellCmdExecutor.execCmd('chown -R glance:glance /etc/glance/')
        
        if debug == True :
            print 'DEBUG=True.On local dev env, do test===='
            pass
        else :
            ShellCmdExecutor.execCmd('systemctl enable openstack-glance-api.service')
            ShellCmdExecutor.execCmd('systemctl enable openstack-glance-registry.service')
            ShellCmdExecutor.execCmd('systemctl start openstack-glance-api.service')
            ShellCmdExecutor.execCmd('systemctl start openstack-glance-registry.service')
        print "start glance done####"
        pass
    
    @staticmethod
    def restart():
        print "restart glance========="
        if debug == True :
            print 'DEBUG=True.On local dev env, do test===='
            pass
        else :
            ShellCmdExecutor.execCmd('systemctl restart openstack-glance-api.service')
            ShellCmdExecutor.execCmd('systemctl restart openstack-glance-registry.service')
            pass
        
        print "restart glance done####"
        pass
    
    @staticmethod
    def configConfFile():
        #RABBIT_HOSTS RABBIT_PASSWORD GLANCE_VIP GLANCE_DBPASS MYSQL_VIP KEYSTONE_VIP KEYSTONE_GLANCE_PASSWORD 
        print "configure glance conf file======"
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]
        glance_vip = vipParamsDict["glance_vip"]
        print "glance_vip=%s" % glance_vip
        glance_dbpass = JSONUtility.getValue("glance_dbpass")
        keystone_glance_password = JSONUtility.getValue("keystone_glance_password")
        
        keystone_vip = vipParamsDict["keystone_vip"]
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        glanceConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'GLANCE_CONF_DIR')
        print 'glanceConfDir=%s' % glanceConfDir #/etc/glance
        
        glance_api_conf_file_path = os.path.join(glanceConfDir, 'glance-api.conf')
        glance_registry_conf_file_path = os.path.join(glanceConfDir, 'glance-registry.conf')
        
        if not os.path.exists(glanceConfDir) :
            os.system("sudo mkdir -p %s" % glanceConfDir)
            pass
        #if exist, remove original conf files
        if os.path.exists(glance_api_conf_file_path) :
            os.system("sudo cp -r %s /etc/glance/glance-api.conf.bak" % glance_api_conf_file_path)
            os.system("sudo rm -rf %s" % glance_api_conf_file_path)
            pass
        
        if os.path.exists(glance_registry_conf_file_path) :
            print 'tttttttt====='
            print 'glance_registry_conf_file_path=%s' % glance_registry_conf_file_path
            os.system("sudo cp -r %s /etc/glance/glance-registry.conf.bak" % glance_registry_conf_file_path)
            os.system("sudo rm -rf %s" % glance_registry_conf_file_path)
            pass
        
#         os.system("sudo cp -r %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
#         os.system("sudo cp -r %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glanceConfDir)
        
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
#         ShellCmdExecutor.execCmd("sudo cp -r %s %s" % (SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH, glanceConfDir))
        
        ######NEW
        
        ShellCmdExecutor.execCmd("cat %s > /tmp/glance-api.conf" % SOURCE_GLANE_API_CONF_FILE_TEMPLATE_PATH)
        ShellCmdExecutor.execCmd("cat %s > /tmp/glance-registry.conf" % SOURCE_GLANE_REGISTRY_CONF_FILE_TEMPLATE_PATH)
        
        ShellCmdExecutor.execCmd("mv /tmp/glance-api.conf /etc/glance/")
        ShellCmdExecutor.execCmd("mv /tmp/glance-registry.conf /etc/glance/")
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % glance_registry_conf_file_path)

        localIP = YAMLUtil.getManagementIP() 
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<LOCAL_IP>', localIP)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<LOCAL_IP>', localIP)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<GLANCE_VIP>', glance_vip)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<GLANCE_DBPASS>', glance_dbpass)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<GLANCE_DBPASS>', glance_dbpass)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<KEYSTONE_GLANCE_PASSWORD>', keystone_glance_password)
        FileUtil.replaceFileContent(glance_registry_conf_file_path, '<KEYSTONE_GLANCE_PASSWORD>', keystone_glance_password)
        
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(glance_api_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)    
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % glance_api_conf_file_path)
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % glance_registry_conf_file_path)
        pass
    
    @staticmethod
    def importGlaceDBSchema():
        print 'start to importGlaceDBSchema======='
        importCmd = 'su -s /bin/sh -c "glance-manage db_sync" glance'
        output, exitcode = ShellCmdExecutor.execCmd(importCmd)
        print 'output=%s--' % output
        print 'done to importGlaceDBSchema#######'
        pass
    
    @staticmethod
    def getServerIndex():
        local_management_ip = YAMLUtil.getManagementIP()
        glance_params_dict = JSONUtility.getRoleParamsDict('glance')
        glance_ip_list = glance_params_dict["mgmt_ips"]
        index = ServerSequence.getIndex(glance_ip_list, local_management_ip)
        return index

    
if __name__ == '__main__':
    
    print 'hello openstack-icehouse:glance============'
    
    print 'start time: %s' % time.ctime()
    
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/glance_installed'
    
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'glance installed####'
        print 'exit===='
        pass
    else :
        print 'start to install======='
        #
        Glance.install()
        Glance.configConfFile()
        
#         first_glance_launched_mark_file = '/opt/openstack_conf/tag/glance0_launched'
#         #when first keystone is launched, to import glance db schema
#         if Glance.getServerIndex() == 0 :
#             #######
#             TIMEOUT = 1800 #0.5 hour for test
#             timeout = TIMEOUT
#             time_count = 0
#             print 'test timeout==='
#             while True:
#                 file_path = '/opt/openstack_conf/tag/keystone0_launched'
#                 flag = os.path.exists(file_path)
#                 if flag == True :
#                     print 'wait time: %s second(s).' % time_count
#                     #when keystone0 is launched, then import glance db schema
#                     Glance.importGlaceDBSchema()
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
#             
#             Glance.start()
#             
#             #To send to the rest glance
#             glance_params_dict = JSONUtility.getRoleParamsDict('glance')
#             glance_ip_list = glance_params_dict["mgmt_ips"] 
#             
#             if len(glance_ip_list) > 1 :
#                 for glance_ip in glance_ip_list[1:] :
#                     SSH.sendTagTo(glance_ip, first_glance_launched_mark_file)
#                     pass
#                 pass
#             
#             ###########
#             pass
#         else :
#             TIMEOUT = 1800 #0.5 hour for test
#             timeout = TIMEOUT
#             time_count = 0
#             print 'test timeout==='
#             while True:
#                 flag = os.path.exists(first_glance_launched_mark_file)
#                 if flag == True :
#                     print 'wait time: %s second(s).' % time_count
#                     Glance.start()
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
#             pass
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        #mark: glance is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    
    print 'hello openstack-icehouse:glance#######'
    pass

