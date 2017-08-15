'''
Created on May 30, 2017

@author: zhangbai
'''
import sys
import os
import time

#DEBUG
debug = False
if debug == True :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python-icbc-dev'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class NTPService(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    
    @staticmethod
    def setNTPServer():
        ShellCmdExecutor.execCmd('yum install -y ntp')
        ntp_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ntp', 'ntp.conf.server')
        if os.path.exists('/etc/ntp.conf') :
            ShellCmdExecutor.execCmd('rm -rf /etc/ntp.conf')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /etc' % ntp_template_file_path)
        ShellCmdExecutor.execCmd('mv /etc/ntp.conf.server /etc/ntp.conf')
        ShellCmdExecutor.execCmd('hwclock --systohc')
        ShellCmdExecutor.execCmd('service ntpd restart')
        pass
    
    @staticmethod
    def setNTPClient(ntp_server_ip):
        ShellCmdExecutor.execCmd('cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
        ShellCmdExecutor.execCmd('yum install -y ntp')
        ntp_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ntp', 'ntp.conf.client')
        if os.path.exists('/etc/ntp.conf') :
            ShellCmdExecutor.execCmd('rm -rf /etc/ntp.conf')
            pass
        ShellCmdExecutor.execCmd('cp -r %s /etc' % ntp_template_file_path)
        FileUtil.replaceFileContent('/etc/ntp.conf.client', '<NTP_SERVER_IP>', ntp_server_ip)
        ShellCmdExecutor.execCmd('mv /etc/ntp.conf.client /etc/ntp.conf')
        ShellCmdExecutor.execCmd('service ntpd stop')
        update_cmd = 'ntpdate -u %s' % ntp_server_ip
        output, exitcode = ShellCmdExecutor.execCmd(update_cmd)
        print 'setNTPClient.output=%s--' % output
        ShellCmdExecutor.execCmd('hwclock --systohc')
        ShellCmdExecutor.execCmd('service ntpd restart')
        pass
    
    
if __name__ == '__main__':
    print 'hello ntp============'
    print 'start time: %s' % time.ctime()
    
    argv_list = sys.argv
    if len(argv_list) <= 1 :
        print "=================================================="
        print 'Usage:'
        print "python UpdateNTPService.py <ntp_server_ip>"
        print "=================================================="
        pass
    else :
        tag_file = "/opt/openstack_conf/tag/init_ntp"
        if not os.path.exists('/opt/openstack_conf/tag/') :
            os.system('mkdir -p /opt/openstack_conf/tag/')
            pass
        
        if os.path.exists(tag_file) :
            print 'NTP is done####'
            pass
        else :
            ntp_server_ip = sys.argv[1]
            print 'ntp_server_ip=%s--' % ntp_server_ip
            print 'start to update ntp service==========='
            NTPService.setNTPClient(ntp_server_ip)
            print 'done to update ntp service#####'
            os.system('touch %s' % tag_file)
            pass
        pass
    pass
