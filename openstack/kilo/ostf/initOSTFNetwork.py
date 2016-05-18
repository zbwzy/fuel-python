'''
Created on Dec 15, 2015

@author: zhangbai
'''

'''
usage:

python initOSTF.py

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

from openstack.common.role import Role

#install pexpect package
# pexpectPackagePath = os.path.join(PROJ_HOME_DIR, 'externals', 'pexpect-3.3')
# output, exitcode = ShellCmdExecutor.execCmd('cd {packagePath}; python setup.py install'.format(packagePath=pexpectPackagePath))
# print 'installing pexpect============================'
# print 'output=%s' % output

def scp_image(scpCmd, image_file_name, ip):
    try:
        import pexpect
        #key line
        os.system('rm -rf /root/.ssh/known_hosts')
        
        '''
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.20.0.192' (RSA) to the list of known hosts.
root@10.20.0.192's password: 
'''
        child = pexpect.spawn(scpCmd)
        child.expect('Are you sure you want to continue connecting.*')
        child.sendline('yes')
        
#         expect_pass_string = "root@{ip}'s password:".format(ip=ip)
#         password = "r00tme"
#         child.expect(expect_pass_string)
#         child.sendline(password)

        while True :
#             regex = "[\\s\\S]*" #match any
#             index = child.expect([regex, pexpect.EOF, pexpect.TIMEOUT])
            index = child.expect(['%s.*' % image_file_name, pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                break
            elif index == 1:
                pass   #continue to wait 
            elif index == 2:
                pass    #continue to wait 
            
        time.sleep(5)
        child.sendline('exit')
        child.sendcontrol('c')
        child.interact()
    except OSError:
        print 'Catch exception %s when sync glance image.' % OSError.strerror
        sys.exit(0)
        pass
    pass
    
if __name__ == '__main__':
    print 'hello openstack-kilo:init ostf network============'
    print 'start time: %s' % time.ctime()
    #####
    #when execute script,exec: python <this file absolute path>
    ###############################
    if Role.isNeutronServerRole() :
        NETWORK_INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/initOSTFNetwork'
        if os.path.exists(NETWORK_INSTALL_TAG_FILE) :
            print 'ostf network initted####'
            print 'exit===='
            pass
        else :
            from openstack.common.serverSequence import ServerSequence
            neutron_server_ips = JSONUtility.getValue('neutron_ips')
            neutron_ip_list = neutron_server_ips.strip().split(',')
            output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
            localIP = output.strip()
            if ServerSequence.getIndex(neutron_ip_list, localIP) == 0:
                network_init_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'ostf_network_init.sh')
                ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % network_init_script_path)
                ############
                vipParamsDict = JSONUtility.getValue('vip')
                keystone_vip = vipParamsDict["keystone_vip"]
                admin_token = JSONUtility.getValue('admin_token')
                keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
                 
                ShellCmdExecutor.execCmd('chmod 777 /opt/openstack_conf/scripts/ostf_network_init.sh')
                FileUtil.replaceFileContent('/opt/openstack_conf/scripts/ostf_network_init.sh', '<KEYSTONE_VIP>', keystone_vip)
                FileUtil.replaceFileContent('/opt/openstack_conf/scripts/ostf_network_init.sh', '<ADMIN_TOKEN>', admin_token)
                FileUtil.replaceFileContent('/opt/openstack_conf/scripts/ostf_network_init.sh', '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
                 
                ###########
                ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/ostf_network_init.sh')
                pass
            else :
                print 'This is not the first neutron-server.Do not need to init OSTF network.'
                pass
     
            #mark: OSTF network is installed
            os.system('touch %s' % NETWORK_INSTALL_TAG_FILE)
            pass
        pass
    
    
    print 'hello ostf network initted#######'
    pass


