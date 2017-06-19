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
from common.yaml.YAMLUtil import YAMLUtil

from openstack.common.role import Role
from openstack.kilo.common.net import Net

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
#         child.interact()
    except OSError:
        print 'Catch exception %s when sync glance image.' % OSError.strerror
        sys.exit(0)
        pass
    pass
    
if __name__ == '__main__':
    print 'hello openstack-kilo:init ostf============'
    print 'start time: %s' % time.ctime()
    #####
    #when execute script,exec: python <this file absolute path>
    ###############################    
    if Role.isGlanceRole() :
        #To sync image on glance hosts
        IMAGE_INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/initOSTFGlance'
        if os.path.exists(IMAGE_INSTALL_TAG_FILE) :
            print 'ostf glance image initted####'
            print 'exit===='
            pass
        else :
            print 'wait for 10 secs====='
#             time.sleep(10)
            
            if os.path.exists('/opt/openstack_conf/tag/install/existGlanceFileOnHost') :
                output, exitcode = ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/getDefaultImageID.sh')
                imageID = output.strip()
#                 listImageFileCmd = 'ls /var/lib/glance/images/ | grep %s' % imageID
#                 output, exitcode = ShellCmdExecutor.execCmd(listImageFileCmd)
#                 output = output.strip()
            
                imageFileName = imageID
                imageFilePath = os.path.join('/var/lib/glance/images', imageID)
                glance_params_dict = JSONUtility.getRoleParamsDict('glance')
                glance_ip_list = glance_params_dict["mgmt_ips"]
                
                local_ip = YAMLUtil.getManagementIP() 
                
                dest_glance_ip_list = []
                
                for e in glance_ip_list :
                    if(not e == local_ip) :
                        dest_glance_ip_list.append(e)
                        pass
                    pass
                
                for ip in dest_glance_ip_list :
                    scpCmd = 'scp {imageFilePath} root@{glance_ip}:/var/lib/glance/images/'.format(imageFilePath=imageFilePath, glance_ip=ip)
                    print 'scpCmd=%s--' % scpCmd
                    scp_image(scpCmd, imageFileName, ip)
                    pass
                pass
            
            
            
            from common.ntp.NTPService import NTPService
            
            ntp_enabled = YAMLUtil.getValue('ntp', 'enable')
            if ntp_enabled == False :
                #defaulty,choose the first keystone(uuid is  the smallest) as ntp server
                #set ntp client
                keystone_params_dict = JSONUtility.getRoleParamsDict('keystone')
                keystone_ip_list = keystone_params_dict['mgmt_ips']
                keystone_0_ip = keystone_ip_list[0]
                ntp_server_ip = keystone_0_ip
                if YAMLUtil.getManagementIP() != ntp_server_ip:
                    #Not ntp server
                    NTPService.setNTPClient(ntp_server_ip)
                    pass
                pass
            else :
                ntp_server_ip = YAMLUtil.getValue('ntp', 'ntp_server_ip')
                NTPService.setNTPClient(ntp_server_ip)
                pass
            
            ###############
            
            ###implement lldp
            Net.implement_lldp()
            
            from common.openfile.OpenFile import OpenFile
            OpenFile.execModification('/usr/lib/systemd/system', 'openstack-')
            
            os.system('touch %s' % IMAGE_INSTALL_TAG_FILE)
            pass
        pass
    print 'hello ostf initted#######'
    pass


