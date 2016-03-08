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
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil

class BCRDB(object):
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
    def install():
        #dependency
        ShellCmdExecutor.execCmd('yum install perl-DBD-MySQL socat -y')
        
        rdb_package_name = 'BC-RDB-2.2.0-el7.x86_64.tar.gz'
        bcrdb_source_dir = '/etc/puppet/modules/mysql/files/BC-RDB-2.2.0-el7.x86_64.tar.gz'
        cp_cmd = 'cp -r %s /opt/' % bcrdb_source_dir
        ShellCmdExecutor.execCmd(cp_cmd)
        
        extract_cmd = 'cd /opt/; tar zvxf %s' % rdb_package_name
        ShellCmdExecutor.execCmd(extract_cmd)
        pass
    
    @staticmethod
    def config():
        SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')
        RDB_DEPLOY_DIR = '/opt/bcrdb'
        DEST_RDB_CONF_DIR = os.path.join(RDB_DEPLOY_DIR, 'conf')
        RDB_CONF_FILE_PATH = os.path.join(DEST_RDB_CONF_DIR, 'my.cnf')
        EXECUTE_MYSQL_PATH = os.path.join(RDB_DEPLOY_DIR, 'bin', 'mysql')
        
        ShellCmdExecutor.execCmd('cp -r %s %s' % (SOURCE_RDB_CONF_FILE_TEMPLATE_PATH, DEST_RDB_CONF_DIR))
        mysql_ips = JSONUtility.getValue("mysql_ips")
        print 'mysql_ips=%s---' % mysql_ips
        mysql_ip_list = mysql_ips.strip().split(',')
        print 'mysql_ip_list=%s--' % mysql_ip_list
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        local_management_ip = output.strip()
        
        mysql_ip_list1 = []
        for ip in mysql_ip_list :
            if ip.strip() != local_management_ip :
                mysql_ip_list1.append(ip)
                pass
            pass
        
        print 'mysql_ip_list1=%s--' % mysql_ip_list1
        mysql_ip_list_string = ','.join(mysql_ip_list1)
        print 'mysql_ip_list_string=%s--' % mysql_ip_list_string
        
        FileUtil.replaceFileContent(RDB_CONF_FILE_PATH, '<MYSQL_IP_LIST>', mysql_ip_list_string)
        
        #add user bcrdb
        ShellCmdExecutor.execCmd('useradd bcrdb')
        #assign rights
        ShellCmdExecutor.execCmd('chown -R bcrdb:bcrdb /opt/bcrdb')
        
        #cp mysql to /usr/bin
        ShellCmdExecutor.execCmd('cp -r %s /usr/bin/' % EXECUTE_MYSQL_PATH)
        pass
    
    @staticmethod
    def start():
        from openstack.common.serverSequence import ServerSequence
        mysql_ips = JSONUtility.getValue("mysql_ips")
        print 'mysql_ips=%s---' % mysql_ips
        mysql_ip_list = mysql_ips.strip().split(',')
        print 'mysql_ip_list=%s--' % mysql_ip_list
        
        output, exitcode = ShellCmdExecutor.execCmd('cat /opt/localip')
        local_management_ip = output.strip()
        
        index = ServerSequence.getIndex(mysql_ip_list, local_management_ip)
        #Judge master
        if index == 0 :
            start_cmd = '/opt/bcrdb/support-files/mysql.server bootstrap'
            ShellCmdExecutor.execCmd(start_cmd)
            pass
        else :
            start_cmd = '/opt/bcrdb/support-files/mysql.server start'
            ShellCmdExecutor.execCmd(start_cmd)
            pass
        pass
    pass

if __name__ == '__main__':
        
    print 'hello openstack-kilo:rdb======='
    BCRDB.install()
    BCRDB.config()
    print 'hello openstack-kilo:rdb installed#######'
    pass

