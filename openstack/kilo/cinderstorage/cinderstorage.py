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
    def stopIPTables():
        stopCmd = "service iptables stop"
        ShellCmdExecutor.execCmd(stopCmd)
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
        #KEYSTONE_ADMIN_PASSWORD
        print 'Cinder-storage.install start===='
        #
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict["keystone_vip"]
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        print 'start to install prerequisites============='
        script_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 
                                                      'cinder-storage', 
                                                      'cinder_storage_service.sh')
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts/' % script_file_path)
        cinder_storage_service_script_path = '/opt/openstack_conf/scripts/cinder_storage_service.sh'
        ShellCmdExecutor.execCmd('chmod 777 %s' % cinder_storage_service_script_path)
        FileUtil.replaceFileContent(cinder_storage_service_script_path, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(cinder_storage_service_script_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(cinder_storage_service_script_path, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        ShellCmdExecutor.execCmd('bash %s' % cinder_storage_service_script_path)
        
        ShellCmdExecutor.execCmd("systemctl restart lvm2-lvmetad.service")
        
        #Default create volume
        #Create the LVM physical volume /dev/sdb1:
#         createCmd = 'pvcreate /dev/sdb1' 
#         ShellCmdExecutor.execCmd(createCmd)
        
#         createCmd = 'vgcreate cinder-volumes /dev/sdb1'
#         ShellCmdExecutor.execCmd(createCmd)
       
        yumCmd = 'yum install openstack-cinder targetcli python-oslo-db python-oslo-log MySQL-python scsi-target-utils -y'
        ShellCmdExecutor.execCmd(yumCmd)
        
        print 'Cinder-storage.install done####'
        pass

    @staticmethod
    def restart():
#         ShellCmdExecutor.execCmd('/etc/init.d/lvm2-lvmetad restart')
#         ShellCmdExecutor.execCmd('/etc/init.d/tgtd restart')
#         ShellCmdExecutor.execCmd("service openstack-cinder-volume restart")
        initCinderVolumeStorageFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder-storage', 'init_cinder_storage_service.sh')
        print 'initCinderVolumeStorageFilePath=%s---' % initCinderVolumeStorageFilePath
        ShellCmdExecutor.execCmd("bash %s" % initCinderVolumeStorageFilePath)
        pass
    
    @staticmethod
    def start(): 
        ShellCmdExecutor.execCmd('systemctl enable openstack-cinder-volume.service') 
        ShellCmdExecutor.execCmd('systemctl enable target.service')
        ShellCmdExecutor.execCmd('systemctl enable tgtd.service')
        
        ShellCmdExecutor.execCmd('systemctl start tgtd.service')
        ShellCmdExecutor.execCmd('systemctl start openstack-cinder-volume.service')
        ShellCmdExecutor.execCmd('systemctl start target.service')
        pass
    
    @staticmethod
    def configConfFile():
        '''
        LOCAL_MANAGEMENT_IP
        GLANCE_VIP
        CINDER_DBPASS
        MYSQL_VIP
        KEYSTONE_VIP
        KEYSTONE_CINDER_PASSWORD
        RABBIT_PASSWORD
        RABBIT_HOSTS
        '''
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]

        cinder_dbpass = JSONUtility.getValue("cinder_dbpass")
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        
        keystone_vip = vipParamsDict["keystone_vip"]
        glance_vip = vipParamsDict["glance_vip"]
        keystone_cinder_password = JSONUtility.getValue('keystone_cinder_password')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        cinder_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder-storage', 'cinder.conf')
        print 'cinder_conf_template_file_path=%s' % cinder_conf_template_file_path
        tgtd_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'cinder-storage', 'tgtd.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/tgt/' % tgtd_conf_template_file_path)
        
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
        ShellCmdExecutor.execCmd('mv /tmp/cinder.conf /etc/cinder/')
        ShellCmdExecutor.execCmd('rm -rf /tmp/cinder.conf')
#         ShellCmdExecutor.execCmd('sudo cp -rf %s %s' % (cinder_conf_template_file_path, cinderConfDir))
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % cinder_conf_file_path)
        
        FileUtil.replaceFileContent(cinder_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<CINDER_DBPASS>', cinder_dbpass)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<KEYSTONE_CINDER_PASSWORD>', keystone_cinder_password)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<GLANCE_VIP>', glance_vip)
        FileUtil.replaceFileContent(cinder_conf_file_path, '<LOCAL_MANAGEMENT_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % cinder_conf_file_path)
        ShellCmdExecutor.execCmd("chown -R cinder:cinder /etc/cinder/")
        
        #special handling
        if not os.path.exists('/var/lock/cinder') :
            os.system('mkdir -p /var/lock/cinder')
            pass
        
        ShellCmdExecutor.execCmd("chown -R cinder:cinder /var/lock/cinder/")
        
        #If add filter, if necessary, modify /etc/lvm/lvm.conf
        '''
        filter = [ "a/sda/", "a/sdb/", "r/.*/"]
        '''
        pass

    
if __name__ == '__main__':
    print 'hello openstack-kilo:cinder-storage============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/cinder_stoarge_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'cinder-storage installed####'
        print 'exit===='
        pass
    else :
#         Prerequisites.prepare()
        CinderStorage.install()
        CinderStorage.configConfFile()
    #     CinderStorage.start()
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        #mark: cinder is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:cinder-storage#######'
    pass

