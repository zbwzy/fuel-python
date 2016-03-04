'''
Created on Dec 15, 2015

@author: zhangbai
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

from openstack.icehouse.neutronserver.neutronserver import NeutronServerHA
from openstack.common.role import Role

def foo(val1, val2):
    print 'value1=%s' % val1
    print 'value2=%s' % val2
    pass

if __name__ == '__main__':
    print 'hello pexpect test============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    foo('hello', 'beijing')
    #exit()
    #Test data
    ShellCmdExecutor.execCmd('touch /tmp/tt.txt')
    imageFilePath = '/tmp/tt.txt'
    ip = '10.20.0.192'

    scpCmd = 'scp {imageFilePath} root@{glance_ip}:/home/'.format(imageFilePath=imageFilePath, glance_ip=ip)
    print 'scpCmd=%s--' % scpCmd

    '''
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.20.0.192' (RSA) to the list of known hosts.
root@10.20.0.192's password:
    '''
    try:
        import pexpect

#         child = pexpect.spawn(scpCmd)
        child = pexpect.spawn('bash /opt/createNeutronUser.sh')
#         child.expect('Are you sure you want to continue connecting.*')

        password = "123456"
        child.expect('User Password:')

        child.sendline('123456')

        expect_pass_string = "root@{ip}'s password:".format(ip=ip)
        #password = "123456"
#         child.expect(expect_pass_string)
        child.expect('Repeat User Password:')
        child.sendline(password)

        while True :
            regex = "[\\s\\S]*"
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
        print 'Catch exception %s when sync glance image.' % OSError.strerror
        sys.exit(0)
        pass

    ###########################
    #ShellCmdExecutor.execCmd('rm -rf /tmp/tt.txt')
    print 'hello pexpect test#######'
    pass


    