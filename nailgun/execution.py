'''
Created on Nov 5, 2015

@author: zhangbai
'''
import os
import sys
import json
import time

debug = True 

# if debug == True :
#     #MODIFY HERE WHEN TEST ON HOST
#     PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
#     pass
# else :
#     # The real dir in which this project is deployed on PROD env.
#     PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
#     pass
# 
# 
# sys.path.append(PROJ_HOME_DIR)
#This program is used to parse ip_map_role.json on nailgun docker
if debug == False :
    from nailgun.common.ssh import Client as SSHClient
    pass
else :
    pass


class Params(object):
    OPENSTACK_ROLES = ['mongodb', 'keystone', 'glance', 
                       'nova-api', 'nova-compute','neutron-server', 'neutron', 
                       'horizon', 'cinder-api', 'cinder-storage', 'heat', 'ceilometer']
    
    CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/{cluster_id}.json'
    CLUSTER_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/role_ip_map_{cluster_id}.json'
    
    
    def __init__(self):
        pass
    pass


class FileUtil(object):
    '''
    classdocs
    '''
    OPENSTACK_INSTALL_LOG_TEMP_DIR ="/var/log/openstack_icehouse"

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def readContent(file_path):
        config_file = file(file_path, 'r')
        file_content = ""
        file_lines = config_file.readlines();
        for line in file_lines :
            file_content = file_content + line
        config_file.close()
        return file_content
    
    @staticmethod
    def writeContent(file_path, content):
        dir_path = os.path.dirname(file_path)
        os.system("mkdir -p %s" % dir_path)
        config_file = file(file_path, 'w')
        config_file.write(content)
        config_file.close()
    
    @staticmethod
    def replaceFileContent(filePath, replaceToken, replaceValue):
        print("Replace %s to %s in conf file %s" % (replaceToken, replaceValue, filePath))
        content = FileUtil.readContent(filePath)
        content = content.replace(replaceToken, replaceValue)
        FileUtil.writeContent(filePath, content)
        pass
    
    @staticmethod
    def replaceByRegularExpression(filePath, toBeReplacedRegularEx, replaceValue):
        print "Replace the string [%s] with [%s] in file %s." % (toBeReplacedRegularEx, replaceValue, filePath)
        sedCmd = "sed -i 's/%s/%s/g' %s" % (toBeReplacedRegularEx, replaceValue, filePath)
        os.system(sedCmd)
        pass
    pass


def example():
    ip = '10.20.0.151'
    ssh_user = 'root'
    ssh_password = 'r00tme'
    key_filename = '/root/.ssh/id_rsa'
    timeout = 1000
    ssh_client = SSHClient(ip, ssh_user, ssh_password, timeout, key_filename)
    
    cmd = 'echo `date` >> /tmp/hello.txt'
    result = ssh_client.exec_command(cmd)
    
    cmd = 'service openstack-glance-api restart'
    result = ssh_client.exec_command(cmd)
    print 'start glance-api=%s--' % result
    pass

def execRemoteCmd(ip, cmd, timeout=600):
    ssh_user = 'root'
    ssh_password = 'r00tme'
    key_filename = '/root/.ssh/id_rsa'
    if timeout == None :
        timeout = 600
        pass
    
    ssh_client = SSHClient(ip, ssh_user, ssh_password, timeout, key_filename)
    
    result = ssh_client.exec_command(cmd)
    print 'exec remote cmd:%s to ip:%s, the result:%s.' % (cmd, ip, result) 
    pass


def getActiveRoleIPMap(cluster_id):
    if debug :
        print 'cluster_id=%s' % cluster_id
        clusterIPRoleMapFilePath = 'iprole.json'
        pass
    else :
        clusterIPRoleMapFilePath = Params.CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
        print 'clusterIPRoleMapFilePath=%s' % clusterIPRoleMapFilePath
        pass
    
    jsonString = FileUtil.readContent(clusterIPRoleMapFilePath)
    ipRoleMap = json.loads(jsonString)
    
    ip_list = ipRoleMap.keys()
    
    roleIPMap = {}
    for role in Params.OPENSTACK_ROLES :
        roleIPMap[role] = []
        for ip in ip_list:
            role_list = ipRoleMap[ip]
            if role in role_list :
                roleIPMap[role].append(ip)
                pass
            pass
        pass
    
    #record the active nodes by role
    activeRoleIPMap = {}
    for role in roleIPMap.keys() :
        if len(roleIPMap[role]) > 0 :
            activeRoleIPMap[role] = roleIPMap[role]
            pass
        pass
    return activeRoleIPMap

def getInitCmdByRole(role):
    ######DEBUG
    initCmd = 'hostname'
    
    if role == 'keystone' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/keystone/initKeystone.py'
        pass
    
    if role == 'glance' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/glance/initGlance.py'
        pass
    
    if role == 'cinder-api' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/cinder/initCinder.py'
        pass
    
    if role == 'cinder-storage' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/cinder/initCinderStorage.py'
        pass
    
    if role == 'horizon' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/dashboard/initDashboard.py'
        pass
    
    if role == 'heat' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/heat/initHeat.py'
        pass
    
    
    
    
    return initCmd
    
    
    
if __name__ == '__main__':
    cluster_id = ''
    argv = sys.argv
    argv.pop(0)
    print "agrv=%s--" % argv
    if debug == False :
        if len(argv) > 0 :
            cluster_id = str(argv[0])
            pass
        else :
            print "ERROR:no params, do not transter cluster_id to this init file."
            exit()
            pass
        pass
    else :
        print "debug mode.................."
        cluster_id = str(argv[0])
        print 'cluster_id=%s' % cluster_id
        pass
    
    activeRoleIPMap = getActiveRoleIPMap(cluster_id)
    
    print json.dumps(activeRoleIPMap, indent=4)
    
    activeRoles = activeRoleIPMap.keys()
    print 'activeRoles=%s' % activeRoles
    #######DO EXECUTION
    for role in Params.OPENSTACK_ROLES :
        if role in activeRoles :
            ip_list = activeRoleIPMap[role]
            initCmd = getInitCmdByRole(role)
            for ip in ip_list :
                execRemoteCmd(ip, initCmd, timeout=600)
                pass
            time.sleep(5)
            pass
        pass 
    pass
#     
#     role = 'glance'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass   
#     
#     role = 'neutron-server'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass 
#     
#     role = 'neutron'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass 
#     
#     role = 'nova-api'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass   
#     
#     role = 'nova-compute'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass
#     
#     role = 'cinder-api'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass   
#     
#     role = 'cinder-storage'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass  
#     
#     role = 'heat'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass 
#     pass


