'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python mongodb.py

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
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        Network.Prepare()
        
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
    pass

class Network(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def Prepare():
        Network.stopIPTables()
        Network.stopNetworkManager()
        pass
    
    @staticmethod
    def stopNetworkManager():
        stopCmd = "service NetworkManager stop"
        chkconfigOffCmd = "chkconfig NetworkManager off"
        
        ShellCmdExecutor.execCmd(stopCmd)
        ShellCmdExecutor.execCmd(chkconfigOffCmd)
        pass

class MongoDB(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/mongodb.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Mongodb.install start===='
        yumCmd = 'yum install mongodb-server mongodb -y'
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Mongodb.install done####'
        pass

    @staticmethod
    def restart():
        #restart cinder service
        ShellCmdExecutor.execCmd("service mongod restart")
        pass
    
    @staticmethod
    def start():        
        ShellCmdExecutor.execCmd("service mongod start")
        ShellCmdExecutor.execCmd("chkconfig mongod on")
        pass
    
    @staticmethod
    def configConfFile():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        mongodb_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mongodb', 'mongodb.conf')
        print 'mongodb_conf_template_file_path=%s' % mongodb_conf_template_file_path
        
        mongodb_conf_file_path = '/etc/mongodb.conf'
        if os.path.exists(mongodb_conf_file_path) :
            ShellCmdExecutor.execCmd("rm -rf %s" % mongodb_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/mongodb.conf' % mongodb_conf_template_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/mongodb.conf /etc/')
        ShellCmdExecutor.execCmd('rm -rf /tmp/mongodb.conf')
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % mongodb_conf_file_path)
        FileUtil.replaceFileContent(mongodb_conf_file_path, '<LOCAL_IP>', localIP)
        ShellCmdExecutor.execCmd("sudo chmod 755 %s" % mongodb_conf_file_path)
        
        pass
    
    @staticmethod
    def init():
        #only mongodb master, exec this method
        ceilometer_mongo_password = JSONUtility.getValue("ceilometer_mongo_password")
        
        initCmd = 'mongo --host controller --eval \'db = db.getSiblingDB("ceilometer");db.addUser({user: "ceilometer",pwd: "<CEILOMETER_DBPASS>",roles: [ "readWrite", "dbAdmin" ]})\''
        initCmd.replace('<CEILOMETER_DBPASS>', ceilometer_mongo_password)
        output, exitcode = ShellCmdExecutor.execCmd(initCmd)
        print 'output=%s--' % output
        pass
    pass


class MongoDBHA(object):
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def getIndex(): #get host index, the ips has been sorted ascended.
        print 'To get this host index of role %s==============' % "mongodb" 
        mongodb_ips = JSONUtility.getValue('mongodb_ips')
        mongodb_ip_list = mongodb_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'mongodb_ip_list=%s--------------' % mongodb_ip_list
        index = mongodb_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if MongoDBHA.getIndex() == 0 :
            return True
        
        return False

    
if __name__ == '__main__':
    print 'hello openstack-icehouse:mongodb============'
    print 'start time: %s' % time.ctime()
    
    debug = False
    if debug :
        print 'start to debug======'
        print 'end debug######'
        exit()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/mongodb_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'mongodb installed####'
        print 'exit===='
    else :
        MongoDB.install()
        MongoDB.configConfFile()
        MongoDB.start()
        
        isMasterNode = MongoDBHA.isMasterNode()
        if isMasterNode :
            print 'This is mongodb master node.'
            MongoDB.init()
            pass
        
        #mark: mongodb is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:mongodb#######'
    pass

