'''
Created on Nov 5, 2015

@author: zhangbai
'''
import sys
import json

debug = True 

if debug == True :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass


sys.path.append(PROJ_HOME_DIR)
#This program is used to parse ip_map_role.json on nailgun docker

from common.file.FileUtil import FileUtil

class Params(object):
    
    CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/cluster/{cluster_id}.json'
    CLUSTER_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/cluster/role_ip_map_{cluster_id}.json'
    OPENSTACK_ROLES = ['mysql', 'rabbitmq', 'mongodb', 'keystone', 'glance', 'nova-api', 
                       'nova-compute','neutron-server', 'neutron', 'horizon', 
                       'cinder-api', 'cinder-storage', 'heat', 'ceilometer']
    
    def __init__(self):
        pass
    
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
            print "ERROR:no params."
            exit()
            pass
        pass
    else :
        print "debug mode.................."
        pass
    
    if debug :
        clusterIPRoleMapFilePath = 'iprole.json'
        pass
    else :
        clusterIPRoleMapFilePath = Params.CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
    
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
    
    print json.dumps(activeRoleIPMap, indent=4)
    
    activeRoles = activeRoleIPMap.keys()
    print 'activeRoles=%s' % activeRoles
    #######DO EXECUTION
    role = 'keystone'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass 
    
    role = 'glance'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass   
    
    role = 'neutron-server'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass 
    
    role = 'neutron'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass 
    
    role = 'nova-api'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass   
    
    role = 'nova-compute'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass
    
    role = 'cinder-api'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass   
    
    role = 'cinder-storage'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass  
    
    role = 'heat'
    if role in activeRoles :
        ip_list = activeRoleIPMap[role]
        for ip in ip_list :
            ######Do something
            pass
        pass 
    pass












