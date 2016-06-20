'''
Created on Feb 26, 2016

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
from common.yaml.YAMLUtil import YAMLUtil
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil
from openstack.common.serverSequence import ServerSequence

class BCRDB(object):
    '''
    classdocs
    '''
    ROLE = 'mysql'
    TIMEOUT = 600 #unit:second
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        #dependency
        from openstack.kilo.common.repo import Repo
#         Repo.setFuelRepo()
        ShellCmdExecutor.execCmd('yum install perl-DBD-MySQL socat percona-xtrabackup -y')
#         Repo.resetBCLinuxRepo()
        
        rdb_package_name = 'BC-RDB-2.2.0-el7.x86_64.tar.gz'
        bcrdb_source_dir = '/etc/puppet/modules/mysql/files/BC-RDB-2.2.0-el7.x86_64.tar.gz'
        cp_cmd = 'cp -r %s /opt/' % bcrdb_source_dir
        ShellCmdExecutor.execCmd(cp_cmd)
        
        extract_cmd = 'cd /opt/; tar zvxf %s' % rdb_package_name
        ShellCmdExecutor.execCmd(extract_cmd)
        pass
    
    @staticmethod
    def config():
        #rm /etc/my.cnf
        if os.path.exists('/etc/my.cnf') :
            ShellCmdExecutor.execCmd('rm -rf /etc/my.cnf')
            pass
        
        SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')
        RDB_DEPLOY_DIR = '/opt/bcrdb'
        DEST_RDB_CONF_DIR = os.path.join(RDB_DEPLOY_DIR, 'conf')
        RDB_CONF_FILE_PATH = os.path.join(DEST_RDB_CONF_DIR, 'my.cnf')
        EXECUTE_MYSQL_PATH = os.path.join(RDB_DEPLOY_DIR, 'bin', 'mysql')
        MYSQLADMIN_BIN_PATH = os.path.join(RDB_DEPLOY_DIR, 'bin', 'mysqladmin')
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (SOURCE_RDB_CONF_FILE_TEMPLATE_PATH, DEST_RDB_CONF_DIR))
        
        mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
        mysql_ip_list = mysql_params_dict['mgmt_ips']
        print 'mysql_ip_list=%s--' % mysql_ip_list
        local_management_ip = YAMLUtil.getManagementIP()
        
        mysql_ip_list1 = [] #The rest mysql except itself
        for ip in mysql_ip_list :
            if ip.strip() != local_management_ip :
                mysql_ip_list1.append(ip)
                pass
            pass
        
        print 'mysql_ip_list1=%s--' % mysql_ip_list1
        mysql_ip_list_string = ','.join(mysql_ip_list1)
        print 'mysql_ip_list_string=%s--' % mysql_ip_list_string
        
        FileUtil.replaceFileContent(RDB_CONF_FILE_PATH, '<MYSQL_IP_LIST>', mysql_ip_list_string)
        
        mysql_dir_rights_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'mysql_dir_rights.sh')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/scripts/' % mysql_dir_rights_script_path)
        ShellCmdExecutor.execCmd('bash /opt/openstack_conf/scripts/mysql_dir_rights.sh')
        
        #cp mysql to /usr/bin
        ShellCmdExecutor.execCmd('cp -r %s /usr/bin/' % EXECUTE_MYSQL_PATH)
        
        ShellCmdExecutor.execCmd('cp -r %s /usr/bin/' % MYSQLADMIN_BIN_PATH)
        
        ShellCmdExecutor.execCmd('useradd bcrdb')
        ShellCmdExecutor.execCmd('chown -R bcrdb:bcrdb /opt/bcrdb')
        pass
    
    @staticmethod
    def reDeploy():
        if os.path.exists('/opt/bcrdb') :
            ShellCmdExecutor.execCmd('rm -rf /opt/bcrdb')
            pass
        
        rdb_package_name = 'BC-RDB-2.2.0-el7.x86_64.tar.gz'
        destTarFilePath = os.path.join('/opt', rdb_package_name) 
        if os.path.exists(destTarFilePath) :
            ShellCmdExecutor.execCmd('rm -rf %s' % destTarFilePath)
            pass
        
        bcrdb_source_dir = '/etc/puppet/modules/mysql/files/BC-RDB-2.2.0-el7.x86_64.tar.gz'
        cp_cmd = 'cp -r %s /opt/' % bcrdb_source_dir
        ShellCmdExecutor.execCmd(cp_cmd)
        
        extract_cmd = 'cd /opt/; tar zvxf %s' % rdb_package_name
        ShellCmdExecutor.execCmd(extract_cmd)
        
        ######re-config
        BCRDB.config()
        pass
    
    @staticmethod
    def start():
        from openstack.common.serverSequence import ServerSequence
        
        mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
        mysql_ip_list = mysql_params_dict['mgmt_ips']
        print 'mysql_ip_list=%s--' % mysql_ip_list
        
        local_management_ip = YAMLUtil.getManagementIP()
        
        index = ServerSequence.getIndex(mysql_ip_list, local_management_ip)
        print 'mysql index=%s--' % str(index)
        #Judge master
        if not os.path.exists('/opt/openstack_conf/tag/') :
            ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/tag/')
            pass
        
        start_cmd = ''
        start_cmd_template = '/opt/bcrdb/support-files/mysql.server {action}'
        if index == 0 :
            start_cmd = start_cmd_template.format(action='bootstrap')
            ShellCmdExecutor.execCmd(start_cmd)
            
            print 'retry to bootstrap bcrdb==========='
            retry = 3
            while retry > 0 :
                print 'retry=%d' % retry
                
                check_mysql_cmd = 'ps aux | grep mysqld | grep wsrep | grep 3306 | grep -v grep'
                process_num, exitcode = ShellCmdExecutor.execCmd(check_mysql_cmd)
                process_num = process_num.strip()
                if process_num != '0' :
                    print 'break to bootstrap bcrdb====='
                    break
                else :
                    print 'retry=%d' % retry
                    ShellCmdExecutor.execCmd(start_cmd)
                    pass
                
                retry -= 1
                pass
            
            #send tag to other mysql server, mark that: 
            #the first mysql server has been launched.
            if len(mysql_ip_list) > 1:
                retry = 3
                while retry > 0 :
                    for mysql_ip in mysql_ip_list[1:] :
                        from openstack.kilo.ssh.SSH import SSH
                        SSH.sendTagTo(mysql_ip, 'bcrdb_0_launched')
                        pass
                    
                    retry -= 1
                    pass
                pass
                        
            time.sleep(15)
            check_mysql_cmd = 'ps aux | grep mysqld | grep wsrep | grep 3306 | grep -v grep'
            process_num, exitcode = ShellCmdExecutor.execCmd(check_mysql_cmd)
            if process_num != '0' :
                print 'to init db===='
                from openstack.kilo.mysql.initDB import MySQL
                MySQL.init()
                pass
            else :
                print 'rdb is not launched.'
                pass
            pass
        else :
            start_cmd = start_cmd_template.format(action='start')
            
            #####
            TIMEOUT = 600
            timeout = TIMEOUT
            time_count = 0
            while True:
                cmd = 'ls -lt /opt/openstack_conf/tag/ | grep bcrdb_0_launched | wc -l' 
                output, exitcode = ShellCmdExecutor.execCmd(cmd)
                file_tag = output.strip()
                if str(file_tag) == "1" :
                    time.sleep(5)
                    print 'wait time: %s second(s).' % time_count
                     
                    ShellCmdExecutor.execCmd(start_cmd)
                     
                    check_mysql_cmd = 'ps aux | grep mysqld | grep wsrep | grep 3306 | grep -v grep | wc -l'
                    process_num, exitcode = ShellCmdExecutor.execCmd(check_mysql_cmd)
                    process_num = process_num.strip()
                    if process_num == '0' :
                        print 'start bcrdb again===='
                        ShellCmdExecutor.execCmd(start_cmd)
                        pass
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                 
                if time_count == timeout :
                    print 'Timeout %d when wait for the first mysql server launched.' % TIMEOUT
                    print 'Do nothing!timeout=%s.' % timeout
                    break
                pass
            #####
            pass
        pass
    
    @staticmethod
    def start1():
        from openstack.common.serverSequence import ServerSequence
        
        mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
        mysql_ip_list = mysql_params_dict['mgmt_ips']
        print 'mysql_ip_list=%s--' % mysql_ip_list
        
        local_management_ip = YAMLUtil.getManagementIP()
        
        index = ServerSequence.getIndex(mysql_ip_list, local_management_ip)
        print 'mysql index=%s--' % str(index)
        #Judge master
        if not os.path.exists('/opt/openstack_conf/tag/') :
            ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/tag/')
            pass
        
        from openstack.kilo.ssh.SSH import SSH
        if index == 0 :
            print 'start to launch mysql master==============='
            start_cmd = '/opt/bcrdb/support-files/mysql.server bootstrap'
            ShellCmdExecutor.execCmd(start_cmd)
            
            #Mutual trust has been established when execute prerequisites.py, then send tag to the rest bcrdb servers
            #to mark that the first bcrdb server has been launched.
            tag_file_name = 'bcrdb_0' #The first server of bcrdb cluster
            #mark master
            mark_cmd = 'touch /opt/openstack_conf/tag/{file}'.format(file=tag_file_name)
            os.system(mark_cmd)
            #mark slave
            slave_mysql_server_list = mysql_ip_list[1:]
            for slave_ip in slave_mysql_server_list :
                SSH.sendTagTo(slave_ip, tag_file_name)
                pass
            #whether keystone exists in the cluster
            if YAMLUtil.hasRole('keystone') :
                keystone_params_dict = JSONUtility.getRoleParamsDict('keystone')
                keystone_ip_list = keystone_params_dict['mgmt_ips']
                #send tag to first server of keystone cluster
                SSH.sendTagTo(keystone_ip_list[0], tag_file_name)
                pass
            pass
        else :
            print 'start to launch mysql slave================'
            #wait bcrdb first server launched
            file_path = '/opt/openstack_conf/tag/bcrdb_0'
            time_count = 0
            while True:
                flag = os.path.exists(file_path)
                if flag == True :
                    print 'wait time: %s second(s).' % time_count
                    print 'If first mysql is launched,then start mysql slave========='
                    start_cmd = '/opt/bcrdb/support-files/mysql.server start'
                    ShellCmdExecutor.execCmd(start_cmd)
                    print 'done to start mysql slave######'
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                
                if time_count == BCRDB.TIMEOUT :
                    print 'Do nothing!timeout=%s.' % BCRDB.TIMEOUT
                    break
                pass
            
            #send tag to the first server of keystone cluster:
            #when all servers are launched,keystone is used to register info to RDB.
            index = ServerSequence.getIndex(mysql_ip_list, local_management_ip)
            tag_file_name = 'bcrdb_{index}'.format(index=str(index))
            print 'slave mysql tag_file_name=%s' % tag_file_name
            if YAMLUtil.hasRole('keystone') :
                SSH.sendTagTo(keystone_ip_list[0], tag_file_name)
                pass
            
            print 'send tag to first mysql===='
            SSH.sendTagTo(mysql_ip_list[0], tag_file_name)
            print 'done to send tag to first mysql####'
            pass
        pass
    
    @staticmethod
    def start2():
        from openstack.common.serverSequence import ServerSequence
        
        mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
        mysql_ip_list = mysql_params_dict['mgmt_ips']
        print 'mysql_ip_list=%s--' % mysql_ip_list
        
        local_management_ip = YAMLUtil.getManagementIP()
        
        index = ServerSequence.getIndex(mysql_ip_list, local_management_ip)
        print 'mysql index=%s--' % str(index)
        #Judge master
        if not os.path.exists('/opt/openstack_conf/tag/') :
            ShellCmdExecutor.execCmd('mkdir -p /opt/openstack_conf/tag/')
            pass
        
        start_cmd = ''
        start_cmd_template = '/opt/bcrdb/support-files/mysql.server {action}'
        if index == 0 :
            start_cmd = start_cmd_template.format(action='bootstrap')
#             ShellCmdExecutor.execCmd(start_cmd)
            
            print 'retry to bootstrap bcrdb==========='
            retry = 3
            while retry > 0 :
                print 'retry=%d' % retry
                
                check_mysql_cmd = 'ps aux | grep mysqld | grep wsrep | grep 3306 | grep -v grep'
                process_num, exitcode = ShellCmdExecutor.execCmd(check_mysql_cmd)
                process_num = process_num.strip()
                if process_num != '0' :
                    print 'break to bootstrap bcrdb====='
                    break
                else :
                    print 'retry=%d' % retry
                    BCRDB.reDeploy()
                    ShellCmdExecutor.execCmd(start_cmd)
                    pass
                
                retry -= 1
                pass
            
            #send tag to other mysql server, mark that: 
            #the first mysql server has been launched.
            if len(mysql_ip_list) > 1:
                retry = 3
                while retry > 0 :
                    for mysql_ip in mysql_ip_list[1:] :
                        from openstack.kilo.ssh.SSH import SSH
                        SSH.sendTagTo(mysql_ip, 'bcrdb_0_launched')
                        pass
                    
                    retry -= 1
                    pass
                pass
            pass
        else :
            start_cmd = start_cmd_template.format(action='start')
            #####
            TIMEOUT = 10
            timeout = TIMEOUT
            time_count = 0
            while True:
                cmd = 'ls -lt /opt/openstack_conf/tag/ | grep bcrdb_0_launched | wc -l' 
                output, exitcode = ShellCmdExecutor.execCmd(cmd)
                file_tag = output.strip()
                if str(file_tag) == "1" :
                    time.sleep(1)
                    print 'wait time: %s second(s).' % time_count
                    
                    retry = 3
                    while retry > 0:
                        check_mysql_cmd = 'ps aux | grep mysqld | grep wsrep | grep 3306 | grep -v grep | wc -l'
                        process_num, exitcode = ShellCmdExecutor.execCmd(check_mysql_cmd)
                        process_num = process_num.strip()
                        if process_num == '0' :
                            print 'start bcrdb again===='
                            BCRDB.reDeploy()
                            ShellCmdExecutor.execCmd(start_cmd)
                            pass
                        else :
                            break
                        
                        retry -= 1
                        pass
                    
                    break
                else :
                    step = 1
        #             print 'wait %s second(s)......' % step
                    time_count += step
                    time.sleep(1)
                    pass
                
                if time_count == timeout :
                    print 'Timeout %d when wait for the first mysql server launched.' % TIMEOUT
                    print 'Do nothing!timeout=%s.' % timeout
                    break
                pass
            pass
        pass
    pass
    

if __name__ == '__main__':
        
    print 'hello openstack-kilo:rdb======='
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/initBCRDB'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'bcrdb cluster initted####'
        print 'exit===='
        pass
    else :
        BCRDB.install()
        BCRDB.config()
        BCRDB.start()
        
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:rdb installed#######'
    pass

