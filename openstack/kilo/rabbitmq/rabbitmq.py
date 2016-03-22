'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python rabbitmq.py

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
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil

class RabbitMQ(object):
    '''
    classdocs
    '''
    ROLE = 'rabbitmq'
    ERLANG_COOKIE= 'YOKOWXQREETZSHFNTPEY'
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def produceIPList():
        YAMLUtil.writeIPList(RabbitMQ.ROLE)
        pass
    
    @staticmethod
    def install():
        ShellCmdExecutor.execCmd('yum install -y rabbitmq-server')
        ShellCmdExecutor.execCmd('rabbitmq-plugins enable rabbitmq_management')
        pass
    
    @staticmethod
    def config():
        rabbitmq_config_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'rabbitmq.config')
        rabbitmq_env_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'rabbitmq-env.conf')
        
        rabbitmq_config_file_path = '/etc/rabbitmq/rabbitmq.config'
#         if os.path.exists(rabbitmq_config_file_path) :
#             os.system("rm -rf %s" % rabbitmq_config_file_path)
#             pass
        
        rabbitmq_env_conf_file_path = '/etc/rabbitmq/rabbitmq-env.conf'
#         if os.path.exists(rabbitmq_env_conf_file_path) :
#             os.system("rm -rf %s" % rabbitmq_env_conf_file_path)
#             pass
        
        ShellCmdExecutor.execCmd('cp -r %s /etc/rabbitmq/' % rabbitmq_config_template_file_path)
        ShellCmdExecutor.execCmd('cp -r %s /etc/rabbitmq/' % rabbitmq_env_conf_template_file_path)
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        management_ip = output.strip()
        print 'management_ip=%s--' % management_ip
        print ''
        FileUtil.replaceFileContent(rabbitmq_config_file_path, '<MANAGEMENT_IP>', management_ip)
        rabbitmq_ips = JSONUtility.getValue('rabbitmq_ips')
        rabbit_at_ip_list = []
        rabbitmq_ip_list = rabbitmq_ips.split(',')
        for ip in rabbitmq_ip_list:
            rabbit_at_ip_list.append("'"+'rabbit@'+ip+"'")
            pass
         
        rabbitmq_cluster_string = ','.join(rabbit_at_ip_list)
        FileUtil.replaceFileContent(rabbitmq_config_file_path, '<RABBITMQ_CLUSTER>', rabbitmq_cluster_string)
        ShellCmdExecutor.execCmd('chown -R root:root /etc/rabbitmq')
         
        #rabbitmq cookie
        erlang_cookie_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'erlang.cookie')
        erlang_cookie_dest_file_path = '/var/lib/rabbitmq/.erlang.cookie'
        if os.path.exists(erlang_cookie_dest_file_path) :
            os.system('rm -rf %s' % erlang_cookie_dest_file_path)
            pass
         
        ShellCmdExecutor.execCmd('cp -r %s /var/lib/rabbitmq/' % erlang_cookie_template_file_path)
        ShellCmdExecutor.execCmd('mv /var/lib/rabbitmq/erlang.cookie %s' % erlang_cookie_dest_file_path)
        ShellCmdExecutor.execCmd('chown -R rabbitmq:rabbitmq /var/lib/rabbitmq/')
        ShellCmdExecutor.execCmd('chmod 400 %s' % erlang_cookie_dest_file_path)
        pass
    
    @staticmethod
    def start():
        init_script_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'initRabbitmqCluster.sh')
        '<RABBIT_USER_ID> <RABBIT_PASS>'
        if not os.path.exists('/opt/openstack_conf/') :
            ShellCmdExecutor.execCmd('mkdir /opt/openstack_conf')
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/' % init_script_template_file_path)
        
        init_script_path = '/opt/openstack_conf/initRabbitmqCluster.sh'
        rabbit_user_id = 'nova'
        rabbit_password = JSONUtility.getValue('rabbit_password')
        FileUtil.replaceFileContent(init_script_path, '<RABBIT_USER_ID>', rabbit_user_id)
        FileUtil.replaceFileContent(init_script_path, '<RABBIT_PASS>', rabbit_password)
        time.sleep(3)
        output,exitcode = ShellCmdExecutor.execCmd('bash %s' % init_script_path)
        pass
    pass



if __name__ == '__main__':
    print 'start to install rabbitmq========'
    RabbitMQ.install()
    RabbitMQ.config()
    RabbitMQ.start()
    print 'done to install rabbitmq######'
    pass

