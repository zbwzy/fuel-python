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

class NovaCompute(object):
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
    def sshMutualTrust():
        print 'SSH mutual trust for user nova: start===='
        if os.path.exists('/var/lib/nova/.ssh') :
            os.system('rm -rf /var/lib/nova/.ssh')
            pass
        
        os.system('mkdir -p /var/lib/nova/.ssh')
        #On the first compute node: ssh-keygen -t rsa -f /var/lib/nova/.ssh/id_rsa -P ""
        ShellCmdExecutor.execCmd('ssh-keygen -t rsa -f /var/lib/nova/.ssh/id_rsa -P ""')
        ShellCmdExecutor.execCmd('cp -r /var/lib/nova/.ssh/id_rsa.pub /var/lib/nova/.ssh/authorized_keys')
        ShellCmdExecutor.execCmd('chown -R nova:nova /var/lib/nova/.ssh')
        
        nova_compute_ips = YAMLUtil.getRoleManagementIPList('nova-compute')
        print 'nova_compute_ips=%s--' % nova_compute_ips
        if len(nova_compute_ips) > 1 :
            for nova_compute_ip in nova_compute_ips[1:] :
                scpCmd = 'scp -r /var/lib/nova/.ssh root@{dest_ip}:/var/lib/nova/'.format(dest_ip=nova_compute_ip)
                try:
                    import pexpect
                    #To make the interact string: Are you sure you want to continue connecting.* always appear
                    if os.path.exists('/root/.ssh/known_hosts') :
                        os.system('rm -rf /root/.ssh/known_hosts')
                        pass
            
                    child = pexpect.spawn(scpCmd)
                    
                    #When do the first shell cmd execution, this interact message is appeared on shell.
                    child.expect('Are you sure you want to continue connecting.*')
                    child.sendline('yes')
            
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
                
                #assign rights
                chownCmd = 'ssh root@{dest_ip} chown -R nova:nova /var/lib/nova/'.format(dest_ip=nova_compute_ip)
                os.system(chownCmd)
            print ''
            
        print 'SSH mutual trust for user nova: done####'
        pass
    
    @staticmethod
    def getServerIndex():
        from openstack.common.serverSequence import ServerSequence
        local_management_ip = YAMLUtil.getManagementIP() 
        nova_compute_params_dict = JSONUtility.getRoleParamsDict('nova-compute')
        nova_compute_ip_list = nova_compute_params_dict['mgmt_ips']
        index = ServerSequence.getIndex(nova_compute_ip_list, local_management_ip)
        return index
    
    @staticmethod
    def install():
        print 'Nova-compute.install start===='
        ShellCmdExecutor.execCmd('yum install sysfsutils libvirt* device-mapper* -y')
        
        yumCmd = 'yum install openstack-nova-compute sysfsutils -y'
        ShellCmdExecutor.execCmd(yumCmd)
#         NovaCompute.configConfFile()
        
#         ShellCmdExecutor.execCmd("keystone service-create --name=nova --type=compute --description=\"OpenStack Compute\"")
#         ShellCmdExecutor.execCmd("keystone endpoint-create --service-id=$(keystone service-list | awk '/ compute / {print $2}') --publicurl=http://192.168.122.80:8774/v2/%\(tenant_id\)s  --internalurl=http://192.168.122.80:8774/v2/%\(tenant_id\)s --adminurl=http://192.168.122.80:8774/v2/%\(tenant_id\)s")
#         
#         NovaCompute.start()
        
        #After Network node configuration done
#         NovaCompute.configAfterNetworkNodeConfiguration()
#         NovaCompute.restart()
        print 'Nova-compute.install done####'
        pass
    
    @staticmethod
    def configAfterNetworkNodeConfiguration():
        '''
1.on Controller node: moidfy /etc/nova/nova.conf, enabled metadata:

[DEFAULT]
service_neutron_metadata_proxy=true
neutron_metadata_proxy_shared_secret=123456

2. on Controller node: moidfy /etc/nova/nova.conf:to support VMs creation if vif_plug fails
vif_plugging_is_fatal=false
vif_plugging_timeout=0

        '''
        pass
    
    @staticmethod
    def restart():
        #restart nova-compute service
        ShellCmdExecutor.execCmd("systemctl enable libvirtd.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-compute.service")
        ShellCmdExecutor.execCmd("systemctl restart libvirtd.service")
        ShellCmdExecutor.execCmd("systemctl restart openstack-nova-compute.service")
        pass
    
    @staticmethod
    def start():        
        ShellCmdExecutor.execCmd("systemctl enable libvirtd.service")
        ShellCmdExecutor.execCmd("systemctl enable openstack-nova-compute.service")
        ShellCmdExecutor.execCmd("systemctl restart libvirtd.service")
        ShellCmdExecutor.execCmd("systemctl start openstack-nova-compute.service")
        pass
    
    @staticmethod
    def reconfigLibvirtd():
        ###libvirtd :  /etc/libvirt/libvirtd.conf
        ### /etc/sysconfig/libvirtd
        libvirtdConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'libvirtd', 'libvirtd.conf')
        libvirtdFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'libvirtd', 'libvirtd.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/libvirt/' % libvirtdConfFileTemplatePath)
        ShellCmdExecutor.execCmd('cp -r %s /etc/sysconfig/' % libvirtdFileTemplatePath)
        
        ShellCmdExecutor.execCmd('chown -R root:root /etc/libvirt/libvirtd.conf')
        ShellCmdExecutor.execCmd('chown -R root:root /etc/sysconfig/libvirtd')
        
        ShellCmdExecutor.execCmd('systemctl restart libvirtd.service')
        pass
    
    @staticmethod
    def configConfFile():
        '''
        MYSQL_VIP
        LOCAL_MANAGEMENT_IP
        GLANCE_VIP
        KEYSTONE_VIP
        KEYSTONE_NOVA_PASSWORD
        NEUTRON_VIP
        KEYSTONE_NEUTRON_PASSWORD
        RABBIT_PASSWORD
        RABBIT_HOSTS
        '''
        #use conf template file to replace <CONTROLLER_IP>
        '''
        #modify nova.conf:

[database]
connection=mysql://nova:123456@controller/nova

[DEFAULT]
rpc_backend=rabbit
rabbit_host=<CONTROLLER_IP>
rabbit_password=123456
my_ip=<CONTROLLER_IP>
vncserver_listen=<CONTROLLER_IP>
vncserver_proxyclient_address=<CONTROLLER_IP>
#########
#
rpc_backend=rabbit
rabbit_host=<CONTROLLER_IP>
rabbit_password=123456
my_ip=<CONTROLLER_IP>
vncserver_listen=<CONTROLLER_IP>
vncserver_proxyclient_address=<CONTROLLER_IP>

5).modify nova.conf: set the auth info of keystone:

[DEFAULT]
auth_strategy=keystone

[keystone_authtoken]
auth_uri=http://controller:5000
auth_host=<CONTROLLER_IP>
auth_protocal=http
auth_port=35357
admin_tenant_name=service
admin_user=nova
admin_password=123456
        '''
        '''
        MYSQL_VIP
        LOCAL_MANAGEMENT_IP
        GLANCE_VIP
        KEYSTONE_VIP
        KEYSTONE_NOVA_PASSWORD
        NEUTRON_VIP
        KEYSTONE_NEUTRON_PASSWORD
        RABBIT_PASSWORD
        RABBIT_HOSTS
        NOVA_VIP
        '''
        ####
        NovaCompute.reconfigLibvirtd()
        ####
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        
        glance_vip = vipParamsDict["glance_vip"]
        nova_vip = vipParamsDict["nova_vip"]
        keystone_vip = vipParamsDict["keystone_vip"]
        neutron_vip = vipParamsDict["neutron_vip"]

        keystone_neutron_password = JSONUtility.getValue("keystone_neutron_password")
        keystone_nova_password = JSONUtility.getValue("keystone_nova_password")
        
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
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/novacompute_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-compute installed####'
        print 'exit===='
        pass
    else :
#         Prerequisites.prepare()
        NovaCompute.install()
        NovaCompute.configConfFile()
#         NovaCompute.start()
        #
        #patch
        from openstack.kilo.common.patch import Patch
        Patch.patchOsloDbApi()
        
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        #mark: nova-compute is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:nova-compute#######'
    pass

