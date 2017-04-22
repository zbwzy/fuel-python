'''
Created on Sep 29, 2015

@author: zhangbai
'''

'''
usage:

python nova.py

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
from common.yaml.YAMLUtil import YAMLUtil


class NovaComputeExtend(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/nova/nova.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def configConfFile():
        ####
        from openstack.kilo.novacompute.novacompute import NovaCompute
        from openstack.kilo.novacompute.extend_compute import ExtendNovaCompute
        NovaCompute.reconfigLibvirtd()
        ####
        vipParamsDict = ExtendNovaCompute.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        
        glance_vip = vipParamsDict["glance_vip"]
        nova_vip = vipParamsDict["nova_vip"]
        keystone_vip = vipParamsDict["keystone_vip"]
        neutron_vip = vipParamsDict["neutron_vip"]

        keystone_neutron_password = ExtendNovaCompute.getValue("keystone_neutron_password")
        keystone_nova_password = ExtendNovaCompute.getValue("keystone_nova_password")
        
        nova_compute_params_dict = JSONUtility.getRoleParamsDict('nova-compute')
        virt_type = nova_compute_params_dict["virt_type"]
        
        localIP = YAMLUtil.getManagementIP() 
        
        print 'nova compute configuration========='
        print 'mysql_vip=%s' % mysql_vip
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'nova_vip=%s' % nova_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        nova_api_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'nova.conf')
        print 'nova_api_conf_template_file_path=%s' % nova_api_conf_template_file_path
        
        novaConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'NOVA_CONF_DIR')
        print 'novaConfDir=%s' % novaConfDir #/etc/nova
        
        nova_conf_file_path = os.path.join(novaConfDir, 'nova.conf')
        print 'nova_conf_file_path=%s' % nova_conf_file_path
        
        if not os.path.exists(novaConfDir) :
            ShellCmdExecutor.execCmd("mkdir %s" % novaConfDir)
            pass
        
        ShellCmdExecutor.execCmd("chmod 777 %s" % novaConfDir)
        
        if os.path.exists(nova_conf_file_path) :
            #Refactor
            ShellCmdExecutor.execCmd('cp -r %s /etc/nova/nova.conf.bak' % nova_conf_file_path)
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % nova_conf_file_path)
            pass
        
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (nova_api_conf_template_file_path, novaConfDir))
        ShellCmdExecutor.execCmd("cat %s > /tmp/nova.conf" % nova_api_conf_template_file_path)
        ShellCmdExecutor.execCmd("mv /tmp/nova.conf /etc/nova/")
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % nova_conf_file_path)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
#         FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(nova_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NEUTRON_VIP>', neutron_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_NOVA_PASSWORD>', keystone_nova_password)
        FileUtil.replaceFileContent(nova_conf_file_path, '<KEYSTONE_NEUTRON_PASSWORD>', keystone_neutron_password)
        
        FileUtil.replaceFileContent(nova_conf_file_path, '<GLANCE_VIP>', glance_vip)
        FileUtil.replaceFileContent(nova_conf_file_path, '<VIRT_TYPE>', virt_type)
        FileUtil.replaceFileContent(nova_conf_file_path, '<LOCAL_MANAGEMENT_IP>', localIP)
        FileUtil.replaceFileContent(nova_conf_file_path, '<NOVA_VIP>', nova_vip)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % nova_conf_file_path)
        
        #configure libvirtd.conf
#         libvirtd_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'nova-compute', 'libvirtd.conf')
#         libvirtd_conf_file_path = '/etc/libvirt/libvirtd.conf'
#         print "libvirtd_conf_template_file_path=%s--" % libvirtd_conf_template_file_path
#         
#         if os.path.exists(libvirtd_conf_file_path) :
#             ShellCmdExecutor.execCmd("rm -rf %s" % libvirtd_conf_file_path)
#             pass
#         
#         ShellCmdExecutor.execCmd('cat %s > /tmp/libvirtd.conf' % libvirtd_conf_template_file_path)
#         ShellCmdExecutor.execCmd('mv /tmp/libvirtd.conf /etc/libvirt/')
        
        #special handling
        PYTHON_SITE_PACKAGE_DIR = '/usr/lib/python2.7/site-packages'
        if os.path.exists(PYTHON_SITE_PACKAGE_DIR) :
            ShellCmdExecutor.execCmd('chmod 777 %s' % PYTHON_SITE_PACKAGE_DIR)
            pass
            
        LIB_NOVA_DIR = '/var/lib/nova'
        if os.path.exists(LIB_NOVA_DIR) :
            ShellCmdExecutor.execCmd('chown -R nova:nova %s' % LIB_NOVA_DIR)
            pass
        pass
    
    
if __name__ == '__main__':
    
    print 'hello openstack-kilo:nova-compute============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.

    ###############################
    if not os.path.exists('/opt/openstack_conf/tag/install/') :
        os.system('mkdir -p /opt/openstack_conf/tag/install/')
        pass
    
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/novacompute_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-compute installed####'
        print 'exit===='
        pass
    else :
        
        NovaComputeExtend.configConfFile()
#         NovaCompute.start()
        #
        #patch
        from openstack.kilo.common.patch import Patch
        Patch.patchOsloDbApi()
        
        #do ssh trust for nova user
        from openstack.kilo.ssh.SSH import SSH
#         SSH.sshNovaUserTrust()
        
        #mark: nova-compute is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:nova-compute#######'
    pass

