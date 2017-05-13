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
    useFuelRepo = False
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
        #ntp update
        fuel_master_ip = str(YAMLUtil.getValue('global', 'fuel_master_ip'))
        os.system('/usr/sbin/ntpdate -u %s' % fuel_master_ip)
        
        ShellCmdExecutor.execCmd('yum install -y rabbitmq-server')
        
        ShellCmdExecutor.execCmd('rabbitmq-plugins enable rabbitmq_management')
        pass
    
    @staticmethod
    def config():
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        
        rabbitmq_config_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'rabbitmq.config')
        rabbitmq_env_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'rabbitmq-env.conf')
        rabbitmq_service_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'rabbitmq-server.service')
        
        rabbitmq_config_file_path = '/etc/rabbitmq/rabbitmq.config'
#         if os.path.exists(rabbitmq_config_file_path) :
#             os.system("rm -rf %s" % rabbitmq_config_file_path)
#             pass
        
        rabbitmq_env_conf_file_path = '/etc/rabbitmq/rabbitmq-env.conf'
#         if os.path.exists(rabbitmq_env_conf_file_path) :
#             os.system("rm -rf %s" % rabbitmq_env_conf_file_path)
#             pass
        
        rabbitmq_service_conf_file_path = '/usr/lib/systemd/system/rabbitmq-server.service'
        
        ShellCmdExecutor.execCmd('cp -r %s /etc/rabbitmq/' % rabbitmq_config_template_file_path)
        ShellCmdExecutor.execCmd('cp -r %s /etc/rabbitmq/' % rabbitmq_env_conf_template_file_path)
        
        management_ip = YAMLUtil.getManagementIP()
        print 'management_ip=%s--' % management_ip
        print ''
        FileUtil.replaceFileContent(rabbitmq_env_conf_file_path, '<MANAGEMENT_IP>', management_ip)
        FileUtil.replaceFileContent(rabbitmq_config_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(rabbitmq_config_file_path, '<RABBIT_PASS>', rabbit_password)

        ShellCmdExecutor.execCmd('chown -R rabbitmq:rabbitmq /etc/rabbitmq')
        ShellCmdExecutor.execCmd('chown -R rabbitmq:rabbitmq %s' % rabbitmq_config_file_path)
        ShellCmdExecutor.execCmd('chown -R rabbitmq:rabbitmq %s' % rabbitmq_env_conf_template_file_path)
        #rabbitmq cookie
        erlang_cookie_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'erlang.cookie')
        erlang_cookie_dest_file_path = '/var/lib/rabbitmq/.erlang.cookie'
        if os.path.exists(erlang_cookie_dest_file_path) :
            os.system('rm -rf %s' % erlang_cookie_dest_file_path)
            pass
        
        if os.path.exists(rabbitmq_service_conf_file_path) :
            os.system('rm -rf %s' % rabbitmq_service_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd('cp -r %s /usr/lib/systemd/system/' % rabbitmq_service_conf_template_file_path)
        ShellCmdExecutor.execCmd('cp -r %s /var/lib/rabbitmq/' % erlang_cookie_template_file_path)
        ShellCmdExecutor.execCmd('mv /var/lib/rabbitmq/erlang.cookie %s' % erlang_cookie_dest_file_path)
        
        ShellCmdExecutor.execCmd('chown -R rabbitmq:rabbitmq /var/lib/rabbitmq/')
        ShellCmdExecutor.execCmd('chmod 400 %s' % erlang_cookie_dest_file_path)
        pass
    
    @staticmethod
    def start():
        ShellCmdExecutor.execCmd('systemctl enable rabbitmq-server.service')
        ShellCmdExecutor.execCmd('systemctl start rabbitmq-server.service')
        
        #open limits file & restart always
        from common.openfile.OpenFile import OpenFile
        OpenFile.execModification('/usr/lib/systemd/system', 'rabbitmq-server')
        
        TIMEOUT = 10
        time_count = 0
        while True :
            check_rabbitmq_process = 'ps aux  | grep rabbitmq | grep erlang | grep rabbitmq_server | wc -l'
            output, exitcode = ShellCmdExecutor.execCmd(check_rabbitmq_process)
            rabbitmq_process_num = output.strip()
            if rabbitmq_process_num == '0' :
                ShellCmdExecutor.execCmd('systemctl start rabbitmq-server.service')
                pass
            else :
                print 'rabbitmq is launched####'
                break
            
            print 'retry==='
            print 'time_count=%d' % time_count
            
            time_count += 1
            if time_count == TIMEOUT :
                print 'when launch rabbitmq, timeout=%d' % TIMEOUT
                break
            
            time.sleep(1)
            pass
        
#         output, exitcode = ShellCmdExecutor.execCmd('ps aux | grep rabbitmq_server | grep erlang | grep -v grep | wc -l')
#         
#         if not output.strip() == '1' :
#             startRabbitmqScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'startRabbitmq.sh')
#             ShellCmdExecutor.execCmd('bash %s' % startRabbitmqScriptPath)
#             pass
        
        localIP = YAMLUtil.getManagementIP()

        rabbitmq_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbitmq_ip_list = rabbitmq_params_dict['mgmt_ips']
        rabbit_user_id = rabbitmq_params_dict['rabbit_userid']
        rabbit_password = rabbitmq_params_dict['rabbit_password']
        
        if not os.path.exists('/opt/openstack_conf/scripts') :
            ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/scripts')
            pass
        
        from openstack.common.serverSequence import ServerSequence
        if ServerSequence.getIndex(rabbitmq_ip_list, localIP) == 0:
            init_script_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'initRabbitmqCluster.sh')
            '''
            <RABBIT_USER_ID> <RABBIT_PASS>
            '''
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % init_script_template_file_path)
            
            init_script_path = '/opt/openstack_conf/scripts/initRabbitmqCluster.sh'
            FileUtil.replaceFileContent(init_script_path, '<RABBIT_USER_ID>', rabbit_user_id)
            FileUtil.replaceFileContent(init_script_path, '<RABBIT_PASS>', rabbit_password)
            time.sleep(3)
            output,exitcode = ShellCmdExecutor.execCmd('bash %s' % init_script_path)
            if len(rabbitmq_ip_list) > 1 :
                from openstack.kilo.ssh.SSH import SSH
                retry = 3
                while retry > 0 :
                    for rabbitmq_ip in rabbitmq_ip_list[1:] :
                        SSH.sendTagTo(rabbitmq_ip, 'rabbitmq_0_launched')
                        pass
                    retry -= 1
                pass
            pass
        else :
            re_init_script_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'rabbitmq', 'reInitRabbitmqCluster.sh')
            '''
            <RABBIT_USER_ID> <RABBIT_PASS> <RABBITMQ_MASTER>
            '''
            
            ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts' % re_init_script_template_file_path)
            
            re_init_script_path = '/opt/openstack_conf/scripts/reInitRabbitmqCluster.sh'
            rabbitmq_master_node = YAMLUtil.getNodeNameByManagementIP(rabbitmq_ip_list[0])
            FileUtil.replaceFileContent(re_init_script_path, '<RABBITMQ_MASTER>', rabbitmq_master_node)
            FileUtil.replaceFileContent(re_init_script_path, '<RABBIT_USER_ID>', rabbit_user_id)
            FileUtil.replaceFileContent(re_init_script_path, '<RABBIT_PASS>', rabbit_password)
            time.sleep(3)
            #######
            TIMEOUT = 600
            timeout = TIMEOUT
            time_count = 0
            while True:
                cmd = 'ls -lt /opt/openstack_conf/tag/ | grep rabbitmq_0_launched | wc -l' 
                output, exitcode = ShellCmdExecutor.execCmd(cmd)
                file_tag = output.strip()
                if str(file_tag) == "1" :
                    time.sleep(2)
                    print 'wait time: %s second(s).' % time_count
                    print 'xxxxxxxxxx==='
                    print 'cd /opt/openstack_conf/scripts/; bash reInitRabbitmqCluster.sh'
                    output,exitcode = ShellCmdExecutor.execCmd('cd /opt/openstack_conf/scripts/; bash reInitRabbitmqCluster.sh')
                    '''
rabbitmqctl stop_app
sleep 3
rabbitmqctl join_cluster rabbit@kilo5
rabbitmqctl start_app
sleep 2
rabbitmqctl set_policy ha-all '^(?!amq\.).*' '{"ha-mode": "all"}'
sleep 2
rabbitmqctl add_user nova 68ed25e3a0c3be79ec83
sleep 2
rabbitmqctl  set_permissions -p / nova '.*' '.*' '.*'
                    '''
#                     ShellCmdExecutor.execCmd('rabbitmqctl stop_app')
#                     ShellCmdExecutor.execCmd('rabbitmqctl join_cluster rabbit@kilo5')
#                     ShellCmdExecutor.execCmd('rabbitmqctl start_app')
#                     ShellCmdExecutor.execCmd('rabbitmqctl set_policy ha-all \'^(?!amq\.).*\' \'{"ha-mode": "all"}\'')
#                     ShellCmdExecutor.execCmd('rabbitmqctl add_user nova 68ed25e3a0c3be79ec83')
#                     ShellCmdExecutor.execCmd('rabbitmqctl  set_permissions -p / nova \'.*\' \'.*\' \'.*\'')
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                
                if time_count == timeout :
                    print 'Timeout %d when wait for the first rabbitmq server launched.' % TIMEOUT
                    print 'Do nothing!timeout=%s.' % timeout
                    break
                pass
            pass
        pass
    
    @staticmethod
    def start1():
        TIMEOUT = 10
        time_count = 0
        while True :
            check_rabbitmq_process = 'ps aux  | grep rabbitmq | grep erlang | grep rabbitmq_server | wc -l'
            output, exitcode = ShellCmdExecutor.execCmd(check_rabbitmq_process)
            rabbitmq_process_num = output.strip()
            if rabbitmq_process_num == '0' :
                ShellCmdExecutor.execCmd('systemctl start rabbitmq-server.service')
                pass
            else :
                print 'rabbitmq is launched####'
                break
            
            print 'time_count=%d' % time_count
            
            time_count += 1
            if time_count == TIMEOUT :
                print 'when launch rabbitmq, timeout=%d' % TIMEOUT
                break
            
            time.sleep(1)
            pass
        
        localIP = YAMLUtil.getManagementIP()

        rabbitmq_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbitmq_ip_list = rabbitmq_params_dict['mgmt_ips']
        
        from openstack.common.serverSequence import ServerSequence
        if ServerSequence.getIndex(rabbitmq_ip_list, localIP) == 0:
            print 'On rabbitmq master, do nothing!'
            pass
        else :
            re_init_script_template_file_path = '/opt/openstack_conf/scripts/reInitRabbitmqCluster.sh'
            output, exitcode = ShellCmdExecutor.execCmd('bash %s' % re_init_script_template_file_path)
            print 'when init rabbitmq cluster, output=\n%s--' % output.strip()
            pass
        pass
    pass



if __name__ == '__main__':
    print 'start to install rabbitmq========'
    RabbitMQ.install()
    RabbitMQ.config()
    RabbitMQ.start()
    print 'done to install rabbitmq######'
    pass

