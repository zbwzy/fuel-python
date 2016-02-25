import sys
import os
import time
import yaml


reload(sys)
sys.setdefaultencoding('utf8')

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
    
if __name__ == '__main__':
    
    print 'hello mysql haproxy ha=========='
    print 'hello openstack-icehouse:keystone============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json & /etc/puppet/localip, these two files are generated in init.pp in site.pp.
    print 'start to install======='
    #add HA
    mysql_ip_list_file_path = '/opt/mysql_ip_list'
    haproxy_conf_file_path = '/etc/haproxy/haproxy.cfg'
    haproxy_conf = '/etc/haproxy'
    haproxy_conf = '/etc/haproxy'

    keepalived_conf_file_path = '/etc/keepalived/keepalived.conf'
    keepalived_conf = '/etc/keepalived'
    if not os.path.exists(mysql_ip_list_file_path):
        print 'mysql ip list not exist!'
        pass
    rabbit_vip=JSONUtility.getValue('rabbit_vip')
    print rabbit_vip+">>>>>>>>>>>>>>>>>>>>>>"
    ShellCmdExecutor.execCmd('sudo chmod 777 %s' % mysql_ip_list_file_path)
    mysqlIPListContent = FileUtil.readContent(mysql_ip_list_file_path)
    mysqlIPListContent = mysqlIPListContent.strip()
    mysqlIPList = mysqlIPListContent.split(',')
    
    backendServerTemplate = 'server rabbit-<INDEX> <SERVER_IP>:5672 weight 1'
    
    content = '''
listen rabbitmq_cluster
  bind <RABBIT_VIP>:5672
  mode tcp
  balance roundrobin
  <SERVER_LIST>
    '''
    
    content = content.replace('<RABBIT_VIP>', rabbit_vip)
    index = 1
    server_list = ''
    for ip in mysqlIPList :
        server_list += backendServerTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
        server_list += '\n'
        server_list += '  '
        index += 1
        pass
    
    content = content.replace("<SERVER_LIST>", server_list)
    if not os.path.exists(haproxy_conf_file_path) :
        ShellCmdExecutor.execCmd('yum -y install haproxy')
        haproxy_templete = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        ShellCmdExecutor.execCmd('cp -f %s %s' % (haproxy_templete, haproxy_conf))
        haproxyContent = FileUtil.readContent(haproxy_conf_file_path)
        content = haproxyContent + content
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxy_conf_file_path)
        # FileUtil.replaceFileContent(haproxy_conf_file_path, '#RABBIT_SERVER_LIST', content)
        FileUtil.writeContent(haproxy_conf_file_path, content)
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxy_conf_file_path)
        ##############install keepalived
        ShellCmdExecutor.execCmd('yum -y install keepalived')
        keepalived_template = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keepalived.conf')
        ShellCmdExecutor.execCmd('cp -f %s %s' % (keepalived_template, keepalived_conf))
        keep_sh_template = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
        ShellCmdExecutor.execCmd('cp -f %s %s' % (keep_sh_template, keepalived_conf))
        FileUtil.replaceFileContent(keepalived_conf_file_path,'<WEIGHT>','99')
        FileUtil.replaceFileContent(keepalived_conf_file_path,'<STATE>','MASTER')
        FileUtil.replaceFileContent(keepalived_conf_file_path,'<INTERFACE>','eth0')
        FileUtil.replaceFileContent(keepalived_conf_file_path,'<VIRTURL_IPADDR>',rabbit_vip)
    else :
        haproxyContent = FileUtil.readContent(haproxy_conf_file_path)
        content = haproxyContent + content
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxy_conf_file_path)
        # FileUtil.replaceFileContent(haproxy_conf_file_path, '#RABBIT_SERVER_LIST', content)
        FileUtil.writeContent(haproxy_conf_file_path, content)
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxy_conf_file_path)
        pass
    
    print 'conetent===%s' % content
    # os.system('touch %s' % INSTALL_TAG_FILE)
    pass
