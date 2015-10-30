'''
Created on Oct 29, 2015

@author: zhangbai
'''
# coding=UTF-8  
import sys
import os
import time

reload(sys)
sys.setdefaultencoding('utf8')

debug = True
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

#install PyYAML package
yamlPackagePath = os.path.join(PROJ_HOME_DIR, 'externals', 'PyYAML')
# yamlPackageSetupFilePath = os.path.join(yamlPackagePath, 'setup.py')
# yamlSetupCmd = 'sudo python {yamlPackageSetupFilePath} install'.format(yamlPackageSetupFilePath=yamlPackageSetupFilePath)
output, exitcode = ShellCmdExecutor.execCmd('cd {yamlPackagePath}; sudo python setup.py install'.format(yamlPackagePath=yamlPackagePath))
print 'installing pyyaml============================'
print 'output=%s' % output

import yaml

class YAMLUtil(object):
    '''
    classdocs
    '''
    ASTUTE_YAML_FILE_PATH = '/etc/astute.yaml'
    OPENSTACK_ROLES = ['mysql', 'rabbitmq', 'keystone', 'glance', 'nova-api', 'nova-compute', 'neutron-server', 'neutron', 'cinder', 'cinder-storage', 'ceilometer', 'heat']
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def getMap(yaml_file_path):
        dataMap = {}
        if not os.path.exists(yaml_file_path) :
            print 'ERROR:the yaml file %s NOT exist!' % yaml_file_path
            return dataMap
        
        f = open(yaml_file_path)  
        dataMap = yaml.load(f)  
        f.close() 
        return dataMap
    
    @staticmethod
    def getContent(file_path):
        json_file = open(file_path, 'r')
        lines = json_file.readlines()
        jsonContent = ""
        for line in lines:
            jsonContent += line
        json_file.close()
        return jsonContent
    
    #If you want to get mysql vip, set role = 'mysql', key = 'mysql_vip'
    @staticmethod
    def getValue(role, key):
        value = ''
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        if dataMap.has_key(component_name) :
            value = dataMap[component_name][key]
            pass
        else :
            print 'ERROR:not exist role %s in the file %s.' % (role, YAMLUtil.ASTUTE_YAML_FILE_PATH)
            pass
        
        return value
    
    @staticmethod
    def getNodesMap():
        nodesMap = {}
        nodesMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)['nodes']
        return nodesMap
    
    @staticmethod
    def getIPList(role):
        ipList = []
    
        nodesMap = YAMLUtil.getNodesMap()
        for nodeMap in nodesMap :
            if nodeMap['role'] == role :
                ipList.append(nodeMap['ip'])
                pass
            pass
        
        return ipList
    
    @staticmethod
    def writeIPList(role):
        #Default, in /opt/{role}_ip_list
        ipList = YAMLUtil.getIPList(role)
        ipListContent = ','.join(ipList)
        ip_list_file_path = '/opt/{role}_ip_list'.format(role=role)
        
        if os.path.exists(ip_list_file_path) :
            ShellCmdExecutor.execCmd('sudo rm -rf %s' % ip_list_file_path)
            pass
        
        FileUtil.writeContent(ip_list_file_path, ipListContent)
        pass
        
    
if __name__ == "__main__":
    print 'test yaml========================'
    yamlFilePath = os.path.join(PROJ_HOME_DIR, 'common', 'yaml', 'astute.yaml')
    component_name = 'mysql'
    key = 'mysql_vip'
    value = YAMLUtil.getValue(component_name, key)
    YAMLUtil.getNodesMap()
    print 'mysql_vip=%s------' % value
    print 'mysql_vip_interface=%s--------' % YAMLUtil.getValue(component_name, 'mysql_vip_interface')
    print 'mysql_ip_list=%s--' % YAMLUtil.getIPList('mysql')
    print YAMLUtil.writeIPList('mysql')
    YAMLUtil.writeIPList('mysql')
        
        
    