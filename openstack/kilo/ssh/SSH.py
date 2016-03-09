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
        ShellCmdExecutor.execCmd('rm -rf /root/.ssh/')
        ShellCmdExecutor.execCmd('mkdir /root/.ssh/')
        
        root_ssh_dir_path = '/root/.ssh'
        id_rsa_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'id_rsa')
        id_rsa_pub_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'id_rsa.pub')
        authorized_keys_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'authorized_keys')
        sshd_config_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ssh', 'sshd_config')
        ShellCmdExecutor.execCmd('cp -r %s %s' % (id_rsa_file_path, root_ssh_dir_path))
        ShellCmdExecutor.execCmd('cp -r %s %s' % (id_rsa_pub_file_path, root_ssh_dir_path))
        ShellCmdExecutor.execCmd('cp -r %s %s' % (authorized_keys_file_path, root_ssh_dir_path))
        ShellCmdExecutor.execCmd('cp -r %s /etc/ssh/' % sshd_config_file_path)
        
        ShellCmdExecutor.execCmd('chmod 700 /root/.ssh/')
        ShellCmdExecutor.execCmd('chown -R root:root /root/.ssh/')
        ShellCmdExecutor.execCmd('/bin/systemctl restart sshd.service')
        pass
    
    
if __name__ == '__main__':
    print 'start to construct ssh mutual trust=========='
    SSH.sshMutualTrust()
    print 'done to construct ssh mutual trust######'
    pass

