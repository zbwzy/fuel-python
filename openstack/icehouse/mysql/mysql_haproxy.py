
import sys
import os
import time
import yaml
debug =False 
# The real dir in which this project is deployed on PROD env.
PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
pass

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
class MySQL_haproxy(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/var/log/openstack_icehouse"
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def haproxy_init():
        #when mysql is installed,config file and the root password is None, init the db.
        #chkcofnig
        chkconfigCmd = "chkconfig mysql on"
	print "test"
	f = open('/etc/astute.yaml')
	data = yaml.load(f)
	length=len(data['nodes'])
	for x in data['nodes']:
		print 
       # ShellCmdExecutor.execCmd(chkconfigCmd)
        pass
    
if __name__ == '__main__':
    
    print 'hello mysql haproxy ha=========='
    print 'hello openstack-icehouse:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /opt/localip, these two files are generated in init.pp in site.pp.
    argv = sys.argv
    argv.pop(0)
    print "agrv=%s--" % argv
    LOCAL_IP = ''
    if len(argv) > 0 :
        LOCAL_IP = argv[0]
        pass
    else :
        print "ERROR:no params."
        pass
    
    ###############################
#    INSTALL_TAG_FILE = '/opt/msyqlha_installed'
    
 #   if os.path.exists(INSTALL_TAG_FILE) :
  #      print 'keystone installed####'
   #     print 'exit===='
    ##    exit()
     #   pass
        
    print 'start to install======='
    #add HA
    mysql_ip_list_file_path = '/opt/mysql_ip_list'
    haproxy_conf_file_path = '/etc/haproxy/haproxy.cfg'
    if not os.path.exists(mysql_ip_list_file_path):
        print 'mysql ip list not exist!'
        pass
    
    ShellCmdExecutor.execCmd('sudo chmod 777 %s' % mysql_ip_list_file_path)
    mysqlIPListContent = FileUtil.readContent(mysql_ip_list_file_path)
    mysqlIPListContent = mysqlIPListContent.strip()
    mysqlIPList = mysqlIPListContent.split(',')
    
    backendServerTemplate = 'server mysqldb-<INDEX> <SERVER_IP>:3309 weight 1'
    
    content = ''
    index = 1
    for ip in mysqlIPList :
        content += backendServerTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
        content += '\n'
        content += '       '
        index += 1
        pass
    
    if not os.path.exists(haproxy_conf_file_path) :
        print 'HAProxy conf file %s not exist!' % haproxy_conf_file_path
    else :
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxy_conf_file_path)
        FileUtil.replaceFileContent(haproxy_conf_file_path, '<MYSQL_SERVER_LIST>', content)
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxy_conf_file_path)
        pass
    
    print 'conetent===%s' % content
   # os.system('touch %s' % INSTALL_TAG_FILE)
    pass

