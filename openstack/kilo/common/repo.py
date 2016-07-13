'''
Created on Feb 29, 2016

@author: zhangbai
'''

'''
usage:

python bcrdb.py

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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.file.FileUtil import FileUtil

class Repo(object):
    '''
    classdocs
    '''
    useBCLinuxRepo = True
    BCLinuxRepoIP = '10.254.8.8'
    BCLinuxRepoDomainName = 'mirrors.bclinux.org'
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    #defaultly, use bclinux repo
    @staticmethod
    def setBCLinuxRepo():
        hostsFilePath = '/etc/hosts'
        hostsFileContent = FileUtil.readContent(hostsFilePath).strip()
        
        bclinuxRepoIPDNMappingString = Repo.BCLinuxRepoIP + ' ' + Repo.BCLinuxRepoDomainName
        
        content = hostsFileContent + '\n' + bclinuxRepoIPDNMappingString
        FileUtil.writeContent(hostsFilePath, content)
        
        #mv original yum repo file
        originalRepoFilePath = '/etc/yum.repos.d/nailgun.repo'
        if os.path.exists(originalRepoFilePath) :
            ShellCmdExecutor.execCmd('mv %s /tmp/' % originalRepoFilePath)
            pass
        
        #prepare yum files
        yumFilesPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'yum', '*.repo')
        cpCmd = 'cp %s /etc/yum.repos.d/' % yumFilesPath
        ShellCmdExecutor.execCmd(cpCmd)
        
        ShellCmdExecutor.execCmd('yum clean all && yum makecache')
        pass
    
    @staticmethod
    def resetBCLinuxRepo():
        #mv original yum repo file
        originalRepoFilePath = '/etc/yum.repos.d/nailgun.repo'
        if os.path.exists(originalRepoFilePath) :
            ShellCmdExecutor.execCmd('mv %s /tmp/' % originalRepoFilePath)
            pass
        
        #prepare yum files
        yumFilesPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'yum', '*.repo')
        cpCmd = 'cp %s /etc/yum.repos.d/' % yumFilesPath
        ShellCmdExecutor.execCmd(cpCmd)
        
        ShellCmdExecutor.execCmd('yum clean all && yum makecache')
        pass
    
    @staticmethod
    def setFuelRepo():
        #Before component deployment,the fuel repo file nailgun.repo has been moved to the dir /tmp/.
        if os.path.exists('/tmp/nailgun.repo') :
            ShellCmdExecutor.execCmd('rm -rf /etc/yum.repos.d/*')
            ShellCmdExecutor.execCmd('mv /tmp/nailgun.repo /etc/yum.repos.d/')
            pass
        
        ShellCmdExecutor.execCmd('yum clean all && yum makecache')
        pass
    
    
    
    
    
    

if __name__ == '__main__':
    pass
