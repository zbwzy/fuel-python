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

OPENSTACK_VERSION_TAG = 'newton'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil
from openstack.newton.ssh.SSH import SSH 
from openstack.common.serverSequence import ServerSequence

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def prepare():
        Network.Prepare()
        
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
    pass


class Cinder(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/cinder/cinder.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Cinder.install start===='
        yumCmd = 'yum install openstack-cinder python-cinderclient -y'
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Cinder.install done####'
        pass

    @staticmethod
    def restart():
        #restart cinder service
        ShellCmdExecutor.execCmd("service openstack-cinder-api restart")
        ShellCmdExecutor.execCmd("service openstack-cinder-scheduler restart")
        pass
    
    @staticmethod
    def start():
        cinderRestartScriptTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'restartCinder.sh')
        os.system('cp -r %s /opt/openstack_conf/scripts' % cinderRestartScriptTemplatePath)
        
        ShellCmdExecutor.execCmd('systemctl enable openstack-cinder-api.service')
        ShellCmdExecutor.execCmd('systemctl enable openstack-cinder-scheduler.service')
        
        ShellCmdExecutor.execCmd('systemctl start openstack-cinder-api.service')
        ShellCmdExecutor.execCmd('systemctl start openstack-cinder-scheduler.service')
        pass
    
    @staticmethod
    def configConfFile():
        '''
        LOCAL_MANAGEMENT_IP
        CINDER_DBPASS
        MYSQL_VIP
        KEYSTONE_VIP
        KEYSTONE_CINDER_PASSWORD
        RABBIT_HOSTS
        RABBIT_PASSWORD
        '''
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]
        
        cinder_dbpass = JSONUtility.getValue("cinder_dbpass")
        keystone_cinder_password = JSONUtility.getValue("keystone_cinder_password")
        
        rabbitmq_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbitmq_params_dict["rabbit_hosts"]
#         rabbit_userid = rabbitmq_params_dict["rabbit_userid"]
        rabbit_password = rabbitmq_params_dict["rabbit_password"]
        
        keystone_vip = vipParamsDict["keystone_vip"]
        glance_vip = vipParamsDict["glance_vip"]
        rabbit_vip = vipParamsDict["rabbit_vip"]
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        
        if Cinder.isCinderStorageNode() :
            cinder_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'cinder.conf.merge')
        else :
            cinder_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder', 'cinder.conf')
            pass
        
        print 'cinder_conf_template_file_path=%s' % cinder_conf_template_file_path
        
        cinderConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'CINDER_CONF_DIR')
        print 'cinderConfDir=%s' % cinderConfDir #/etc/cinder
        
        cinder_conf_file_path = os.path.join(cinderConfDir, 'cinder.conf')
        print 'cinder_conf_file_path=%s' % cinder_conf_file_path
        
        if not os.path.exists(cinderConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % cinderConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % cinderConfDir)
        
        if os.path.exists(cinder_conf_file_path) :
            #REFACTOR
            ShellCmdExecutor.execCmd("cp -r %s /etc/cinder/cinder.conf.bak" % cinder_conf_file_path)
            ShellCmdExecutor.execCmd("rm -rf %s" % cinder_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/cinder.conf' % cinder_conf_template_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/cinder.conf /etc/cinder/')
        ShellCmdExecutor.execCmd('rm -rf /tmp/cinder.conf')
        
#         ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (cinder_conf_template_file_path, cinderConfDir))
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % cinder_conf_file_path)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<LOCAL_MANAGEMENT_IP>', localIP)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<GLANCE_VIP>', glance_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<CINDER_DBPASS>', cinder_dbpass)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<KEYSTONE_CINDER_PASSWORD>', keystone_cinder_password)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_VIP>', rabbit_vip)
        
        ShellCmdExecutor.execCmd("chmod 644 %s" % cinder_conf_file_path)
        ShellCmdExecutor.execCmd("chown -R cinder:cinder /etc/cinder/")
        pass
    
    @staticmethod
    def importCinderDBSchema():
        print 'start to importCinderDBSchema======='
        importCmd = 'su -s /bin/sh -c "cinder-manage db sync" cinder'
        output, exitcode = ShellCmdExecutor.execCmd(importCmd)
        print 'output=%s--' % output
        print 'done to importCinderDBSchema######'
        pass
    
    @staticmethod
    def getServerIndex():
        local_management_ip = YAMLUtil.getManagementIP()
        cinder_params_dict = JSONUtility.getRoleParamsDict('cinder-api')
        cinder_ip_list = cinder_params_dict["mgmt_ips"]
        index = ServerSequence.getIndex(cinder_ip_list, local_management_ip)
        return index
    
    
    @staticmethod
    def isCinderStorageNode():
        cinderStorageNodeMgmtIPList = YAMLUtil.getRoleManagementIPList('cinder-storage')
        localMgmtIP = YAMLUtil.getManagementIP()
        print 'cinderStorageNodeMgmtIPList=%s--' % cinderStorageNodeMgmtIPList
        print 'localMgmtIP=%s--' % localMgmtIP
        if localMgmtIP in cinderStorageNodeMgmtIPList :
            return True
        else :
            return False
        pass
    pass

    
    
if __name__ == '__main__':
    print 'hello openstack-newton:cinder============'
    print 'start time: %s' % time.ctime()
    
    debug = False
    if debug :
        print 'start to debug======'
        
        print 'end debug######'
        exit()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/cinder_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'cinder installed####'
        print 'exit===='
        pass
    else :
        Cinder.install()
        Cinder.configConfFile()
        
        #import cinder db schema
        
        from openstack.newton.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        #mark: cinder is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-newton:cinder#######'
    pass

