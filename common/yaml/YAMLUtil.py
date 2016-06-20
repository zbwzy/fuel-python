'''
Created on Oct 29, 2015

@author: zhangbai
'''
# coding=UTF-8  
import sys
import os
import time
import string

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
# yamlSetupCmd = 'python {yamlPackageSetupFilePath} install'.format(yamlPackageSetupFilePath=yamlPackageSetupFilePath)
output, exitcode = ShellCmdExecutor.execCmd('cd {yamlPackagePath}; python setup.py install'.format(yamlPackagePath=yamlPackagePath))
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
    def hasRole(role):
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        if dataMap.has_key(role) :
            return True
        
        return False
    
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
        if dataMap.has_key(role) :
            if dataMap[role].has_key(key) :
                value = dataMap[role][key]
            else :
                print 'No key %s.' % key
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
        print 'len.nodeMap=%s' % len(nodesMap)
        for nodeMap in nodesMap :
            print 'nodeMap.role=%s--,type=%s--' % (nodeMap['role'], type(nodeMap['role']))
            print 'role=%s--, type=%s--' % (role, type(role))
            print nodeMap['role'] == role
            if nodeMap['role'] == role :
                ipList.append(nodeMap['ip'])
                pass
            pass
        
        return ipList
    
    @staticmethod
    def writeIPList(role):
        #Default, in /opt/{role}_ip_list
        ipList = YAMLUtil.getRoleManagementIPList(role)
        ipListContent = ','.join(ipList)
        ip_list_file_path = '/opt/{role}_ip_list'.format(role=role).replace('-', '_')
        
        if os.path.exists(ip_list_file_path) :
            ShellCmdExecutor.execCmd('rm -rf %s' % ip_list_file_path)
            pass
        
        FileUtil.writeContent(ip_list_file_path, ipListContent)
        pass
    
    
    @staticmethod
    def getRoleManagementIPList(role): #acsend by role uid
        nodesMap = YAMLUtil.getNodesMap()
        uid_list = []
        node_map_list = []
        number = 1
        for nodeMap in nodesMap :
            print number
            print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrole=%s--, type=%s--' % (role, type(role))
            print 'nodeMapRole=%s--, type=%s--' % (nodeMap['role'], type(nodeMap['role']))
            print nodeMap['role'] == role
            
            if nodeMap['role'].strip() == role.strip() :
                print 'xxxxxxxxxxxxxxxxx======'
                uid = string.atoi(nodeMap['uid'])
                print 'yyyyyyyyyyyyyyyyyy'
                uid_list.append(uid)
                node_map_list.append(nodeMap)
                pass
            number += 1
            print ''
            pass
        
        uid_list.sort()
        sorted_role_ip_list = [] #ascend by role uid
        for uid in uid_list :
            for nodeMap in node_map_list :
                if nodeMap['uid'] == str(uid) :
                    if role == 'rabbitmq' :
                        sorted_role_ip_list.append("'"+'rabbit@'+nodeMap['name']+"'")
                    else :
                        sorted_role_ip_list.append(nodeMap['internal_address'])
                    pass
                pass
            pass
        
        return sorted_role_ip_list
    
    @staticmethod
    def getRoleStorageIPList(role): #acsend by role uid
        nodesMap = YAMLUtil.getNodesMap()
        uid_list = []
        node_map_list = []
        number = 1
        for nodeMap in nodesMap :
            print number
            print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrole=%s--, type=%s--' % (role, type(role))
            print 'nodeMapRole=%s--, type=%s--' % (nodeMap['role'], type(nodeMap['role']))
            print nodeMap['role'] == role
            
            if nodeMap['role'].strip() == role.strip() :
                print 'xxxxxxxxxxxxxxxxx======'
                uid = string.atoi(nodeMap['uid'])
                print 'yyyyyyyyyyyyyyyyyy'
                uid_list.append(uid)
                node_map_list.append(nodeMap)
                pass
            number += 1
            print ''
            pass
        
        uid_list.sort()
        sorted_role_ip_list = [] #ascend by role uid
        for uid in uid_list :
            for nodeMap in node_map_list :
                if nodeMap['uid'] == str(uid) :
#                     if role == 'rabbitmq' :
#                         sorted_role_ip_list.append("'"+'rabbit@'+nodeMap['name']+"'")
#                     else :
#                         sorted_role_ip_list.append(nodeMap['storage_address'])
#                         pass
                    sorted_role_ip_list.append(nodeMap['storage_address'])
                    pass
                pass
            pass
        
        return sorted_role_ip_list
    
    
    #get role business address
    @staticmethod
    def getRoleExIPList(role): #acsend by role uid
        nodesMap = YAMLUtil.getNodesMap()
        uid_list = []
        node_map_list = []
        number = 1
        for nodeMap in nodesMap :
            print number
            print 'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrole=%s--, type=%s--' % (role, type(role))
            print 'nodeMapRole=%s--, type=%s--' % (nodeMap['role'], type(nodeMap['role']))
            print nodeMap['role'] == role
            
            if nodeMap['role'].strip() == role.strip() :
                print 'xxxxxxxxxxxxxxxxx======'
                uid = string.atoi(nodeMap['uid'])
                print 'yyyyyyyyyyyyyyyyyy'
                uid_list.append(uid)
                node_map_list.append(nodeMap)
                pass
            number += 1
            print ''
            pass
        
        uid_list.sort()
        sorted_role_ip_list = [] #ascend by role uid
        for uid in uid_list :
            for nodeMap in node_map_list :
                if nodeMap['uid'] == str(uid) :
#                     if role == 'rabbitmq' :
#                         sorted_role_ip_list.append("'"+'rabbit@'+nodeMap['name']+"'")
#                     else :
#                         sorted_role_ip_list.append(nodeMap['storage_address'])
#                         pass
                    sorted_role_ip_list.append(nodeMap['public_address'])
                    pass
                pass
            pass
        
        return sorted_role_ip_list
    
    @staticmethod
    def getRabbitRoleManagementIPList(role): #acsend by role uid
        nodesMap = YAMLUtil.getNodesMap()
        uid_list = []
        node_map_list = []
        for nodeMap in nodesMap :
            if nodeMap['role'] == role :
                uid = string.atoi(nodeMap['uid'])
                uid_list.append(uid)
                node_map_list.append(nodeMap)
                pass
            pass
        
        uid_list.sort()
        sorted_role_ip_list = [] #ascend by role uid
        for uid in uid_list :
            for nodeMap in node_map_list :
                if nodeMap['uid'] == str(uid) :
                    sorted_role_ip_list.append(nodeMap['internal_address'])
                    pass
                pass
            pass
        
        return sorted_role_ip_list
            
    @staticmethod
    def hasRoleInNodes(role):
        nodesMap = YAMLUtil.getNodesMap()
        for nodeMap in nodesMap :
            if nodeMap['role'] == role :
                return True
            pass
        return False
    
    #local management ip
    @staticmethod
    def getManagementIP():
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        ss = dataMap['network_scheme']['endpoints']['br-mgmt']['IP'][0].strip()
        ip = ''
        if '/' in str(ss) :
            ip = ss.split('/')[0]
        else :
            ip = ss
            pass
        
        return ip
    
    #local business ip
    @staticmethod
    def getExIP():
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        ss = dataMap['network_scheme']['endpoints']['br-data']['IP'][0].strip()
        ip = ''
        if '/' in str(ss) :
            ip = ss.split('/')[0]
        else :
            ip = ss
            pass
        
        return ip
    
    #local storage ip
    @staticmethod
    def getStorageIP():
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        ss = dataMap['network_scheme']['endpoints']['br-storage']['IP'][0].strip()
        ip = ''
        if '/' in str(ss) :
            ip = ss.split('/')[0]
        else :
            ip = ss
            pass
        
        return ip
    
    
    @staticmethod
    def getVlanRange():
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        vlanRange = dataMap['quantum_settings']['L2']['phys_nets']['physnet2']['vlan_range'].strip()
        return vlanRange
    
    @staticmethod
    def getNodeNameByManagementIP(mgmt_ip):
        '''
nodes:
- swift_zone: '101'
  uid: '101'
  public_address: 10.142.9.6
  ip: 10.254.9.6
  internal_netmask: 255.255.255.0
  fqdn: kilo6.domain.tld
  cabinet: '1'
  role: mysql
  public_netmask: 255.255.255.0
  internal_address: 10.142.10.6
  storage_address: 10.142.50.6
  storage_netmask: 255.255.255.0
  name: kilo6
        '''
        nodeName = ''
        nodesMap = YAMLUtil.getNodesMap()
        for node in nodesMap:
            if node['internal_address'] == mgmt_ip:
                nodeName = node['name']
                break
            pass
        
        return nodeName
    
    @staticmethod
    def setHosts():
        nodes_dict = {}
        host="127.0.0.1 localhost\n"
        nodesMap = YAMLUtil.getNodesMap()
        for node in nodesMap:
            if nodes_dict.has_key(node['internal_address']) == False:
                nodes_dict[node['internal_address']] = node['name']
                host = host + node['internal_address'] + " " + node['name'] + "\n"
                pass
            pass
         
        print host
        FileUtil.writeContent("/etc/hosts",host)
        pass    
        
    
if __name__ == "__main__":
    print 'test yaml========================'
    ###New Test codes
    print 'vlan_range=%s--' % YAMLUtil.getVlanRange()
    mgmt_ip = YAMLUtil.getManagementIP()
    print 'mgmt_ip=%s---' % mgmt_ip
    
    storage_ip = YAMLUtil.getStorageIP()
    print 'storage_ip=%s---' % storage_ip
    
    ex_ip = YAMLUtil.getExIP()
    print 'ex_ip=%s---' % ex_ip
    
    print 'rabbit mgmt ip list======='
    print YAMLUtil.getRabbitRoleManagementIPList('rabbitmq')
    
    print 'mysql mgmt ip list======='
    print YAMLUtil.getRoleManagementIPList('mysql')
    
#     print 'hosts======'
#     YAMLUtil.setHosts()
    
    ###Original Test Codes
#     yamlFilePath = os.path.join(PROJ_HOME_DIR, 'common', 'yaml', 'astute.yaml')
#     component_name = 'mysql'
#     value = YAMLUtil.getValue(component_name, key)
#     YAMLUtil.getNodesMap()
#     print 'mysql_ip_list=%s--' % YAMLUtil.getIPList('glance')
#     
#     print 'xxxxxxxxx'
#     YAMLUtil.writeIPList('mysql')
#     print 'debug--------------'
#     nodesMap = YAMLUtil.getNodesMap()
#     print YAMLUtil.hasRoleInNodes('mysql')
#     print 'get role ip list ascend by uid==========='
#     print YAMLUtil.getRoleManagementIPList('mysql')
#     print 'has role========================='
#     print YAMLUtil.hasRole('cinder')
#     print 'get node name by ip========='
#     print YAMLUtil.getNodeNameByManagementIP('10.20.0.87')
    pass


