'''
Created on Feb 26, 2016

@author: zhangbai
'''

import sys
import os

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
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility

class SSH(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def sshMutualTrust():
        fuel_ip = JSONUtility.getValue('fuel_ip')
        ShellCmdExecutor.execCmd('cp -r /root/.ssh/authorized_keys /root/.ssh/id_rsa.pub')
#         ShellCmdExecutor.execCmd('mkdir /root/.ssh/')
        
#         root_ssh_dir_path = '/root/.ssh'
#         id_rsa_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'id_rsa')
#         id_rsa_pub_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'id_rsa.pub')
#         authorized_keys_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'authorized_keys')

        #scp key from fuel master:
        #Why do like this way? 
        #Because this way will not affect the action : on fuel master, ssh to any node without password.
        scp_cmd = 'scp root@{fuel_ip}:/root/.ssh/id_rsa /root/.ssh/'.format(fuel_ip=fuel_ip)
        try:
            import pexpect
    
            child = pexpect.spawn(scp_cmd)
            
            #When do the first shell cmd execution, this interact message is appeared on shell.
            child.expect('Are you sure you want to continue connecting.*')
            child.sendline('yes')
            
            expect_pass_string = "root@{fuel_ip}'s password:".format(fuel_ip=fuel_ip)
            fuel_root_password = "r00tme"
            child.expect(expect_pass_string)
            child.sendline(fuel_root_password)
            while True :
                regex = "[\\s\\S]*" #match any
                index = child.expect([regex , pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:
                    break
                elif index == 1:
                    pass   #continue to wait
                elif index == 2:
                    pass    #continue to wait
    
            child.sendline('exit')
            child.sendcontrol('c')
            #child.interact()
        except OSError:
            print 'Catch exception %s when send tag.' % OSError.strerror
            sys.exit(0)
            pass
        
        sshd_config_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'sshd_config')
        ShellCmdExecutor.execCmd('cp -r %s /etc/ssh/' % sshd_config_file_path)
        
        ShellCmdExecutor.execCmd('chmod 700 /root/.ssh/')
        ShellCmdExecutor.execCmd('chmod 400 /root/.ssh/authorized_keys')
        ShellCmdExecutor.execCmd('chmod 400 /root/.ssh/id_rsa')
        ShellCmdExecutor.execCmd('chmod 400 /root/.ssh/id_rsa.pub')
        ShellCmdExecutor.execCmd('chown -R root:root /root/.ssh/')
        ShellCmdExecutor.execCmd('/bin/systemctl restart sshd.service')
        pass
    
    #Example: 
    #To tell the rest of bcrdb servers: mysql service is started on the first bcrdb server.
    @staticmethod
    def sendTagTo(server_management_ip, tag_file_name): # The file <tag_file_name> is produced in /opt/openstack_conf/tag/.
        try:
            import pexpect
            #To make the interact string: Are you sure you want to continue connecting.* always appear
            if os.path.exists('/root/.ssh/known_hosts') :
                os.system('rm -rf /root/.ssh/known_hosts')
                pass
    
    #         child = pexpect.spawn(scpCmd)
            cmd = 'ssh root@{ip} "mkdir -p /opt/openstack_conf/tag/;\
            touch /opt/openstack_conf/tag/{file}"'.format(ip=server_management_ip, 
                                                          file=tag_file_name)
            child = pexpect.spawn(cmd)
            
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
        pass
    pass
    
    
if __name__ == '__main__':
    print 'start to construct ssh mutual trust=========='
    #TEST CODE
    SSH.sshMutualTrust()
#     SSH.sendTagTo('10.20.0.86', 'bcrdb_0')
    print 'done to construct ssh mutual trust######'
    pass

