'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python keystone.py

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

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil

class HA(object):
    '''
    classdocs
    '''
    ROLE = 'mysql'
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def test():
        haproxyConfFilePath = '/etc/haproxy/haproxy.cfg'
        if os.path.exists(haproxyConfFilePath) :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % haproxyConfFilePath)
        else :
            output = '''
global
  daemon
  group haproxy
  log /dev/log local0
  maxconn 16000
  pidfile /var/run/haproxy.pid
  stats socket /var/lib/haproxy/stats
  user haproxy

defaults
  log global
  maxconn 8000
  mode http
  retries 3
  stats enable
  timeout http-request 10s
  timeout queue 1m
  timeout connect 10s
  timeout client 1m
  timeout server 1m
  timeout check 10s

            '''
            pass
        
        print 'nativecontent=%s-----' % output
        haproxyNativeContent = output.strip()
        
        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        
        haproxyContent += 'hello'
        haproxyContent += '\n'
        haproxyContent += 'world'
        
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        ShellCmdExecutor.execCmd('sudo cp -rf /tmp/haproxy.cfg /etc/haproxy')
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)
        pass
    pass



if __name__ == '__main__':
        
    print 'test======='
    HA.test()
    
    print 'done test#######'
    pass


