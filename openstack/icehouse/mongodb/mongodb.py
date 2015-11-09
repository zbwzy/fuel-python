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

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        Network.Prepare()
        
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
    pass

class Network(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def Prepare():
        Network.stopIPTables()
        Network.stopNetworkManager()
        pass
    
    @staticmethod
    def stopNetworkManager():
        stopCmd = "service NetworkManager stop"
        chkconfigOffCmd = "chkconfig NetworkManager off"
        
        ShellCmdExecutor.execCmd(stopCmd)
        ShellCmdExecutor.execCmd(chkconfigOffCmd)
        pass

class CinderStorage(object):
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
        print 'Cinder-storage.install start===='
        yumCmd = 'yum install lvm2 -y'
        ShellCmdExecutor.execCmd(yumCmd)
        
        ShellCmdExecutor.execCmd("service lvm2-lvmetad start")
        ShellCmdExecutor.execCmd("chkconfig lvm2-lvmetad on")
        
        #Default create volume
        #Create the LVM physical volume /dev/sdb1:
        createCmd = 'pvcreate /dev/sdb1' 
        ShellCmdExecutor.execCmd(createCmd)
        
        createCmd = 'vgcreate cinder-volumes /dev/sdb1'
        ShellCmdExecutor.execCmd(createCmd)
       
        yumCmd = 'yum install openstack-cinder targetcli python-oslo-db MySQL-python -y'
        ShellCmdExecutor.execCmd(yumCmd)
        
        print 'Cinder-storage.install done####'
        pass

    @staticmethod
    def restart():
        #restart cinder service
        ShellCmdExecutor.execCmd("service openstack-cinder-volume restart")
        pass
    
    @staticmethod
    def start():        
        ShellCmdExecutor.execCmd("service openstack-cinder-volume start")
        ShellCmdExecutor.execCmd("chkconfig openstack-cinder-volume on")
        pass
    
    @staticmethod
    def configConfFile():
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
        rabbit_host = JSONUtility.getValue("rabbit_host")
        
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        glance_vip = JSONUtility.getValue("glance_vip")
        cinder_mysql_password = JSONUtility.getValue("cinder_mysql_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_host=%s' % rabbit_host
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        cinder_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder-storage', 'cinder.conf')
        print 'cinder_conf_template_file_path=%s' % cinder_conf_template_file_path
        
        cinderConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'CINDER_CONF_DIR')
        print 'cinderConfDir=%s' % cinderConfDir #/etc/cinder
        
        cinder_conf_file_path = os.path.join(cinderConfDir, 'cinder.conf')
        print 'cinder_conf_file_path=%s' % cinder_conf_file_path
        
        if not os.path.exists(cinderConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % cinderConfDir)
            pass
        
        if os.path.exists(cinder_conf_file_path) :
            ShellCmdExecutor.execCmd("rm -rf %s" % cinder_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd("chmod 777 /etc/cinder")
        ShellCmdExecutor.execCmd('cat %s > /tmp/cinder.conf' % cinder_conf_template_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/cinder.conf /etc/cinder')
        ShellCmdExecutor.execCmd('rm -rf /tmp/cinder.conf')
#         ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (cinder_conf_template_file_path, cinderConfDir))
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % cinder_conf_file_path)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<CINDER_MYSQL_PASSWORD>', cinder_mysql_password)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<GLANCE_VIP>', glance_vip)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % cinder_conf_file_path)
        
        #If add filter, if necessary, modify /etc/lvm/lvm.conf
        '''
        filter = [ "a/sda/", "a/sdb/", "r/.*/"]
        '''
        pass

    
if __name__ == '__main__':
    print 'hello openstack-icehouse:mongodb============'
    print 'start time: %s' % time.ctime()
    
    debug = False
    if debug :
        print 'start to debug======'
        
        print 'end debug######'
        exit()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/mongodb_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'mongodb installed####'
        print 'exit===='
    else :
        CinderStorage.install()
        CinderStorage.configConfFile()
    #     CinderStorage.start()
        
        #mark: cinder is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:mongodb#######'
    pass

