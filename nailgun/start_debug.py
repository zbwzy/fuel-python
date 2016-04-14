'''
Created on Nov 5, 2015

@author: zhangbai
'''
import os
import sys
import json
import time

debug = False 

#This program is used to parse ip_map_role.json on nailgun docker
if debug == True :
    from nailgun.common.ssh import Client as SSHClient
    from nailgun.logger import logger
    pass
else :
    pass


class Params(object):
#     OPENSTACK_ROLES = ['mysql', 'keystone', 'glance', 'cinder-api', 'cinder-storage', 'heat', 
#                        'horizon', 'nova-api', 'nova-compute', 'ceilometer', 'neutron-server', 
#                        'neutron-agent'
#                        ]
    
    OPENSTACK_ROLES = ['mysql', 'rabbitmq', 'keystone', 'glance', 'cinder-api', 'cinder-storage', 
                       'horizon', 'nova-api', 'nova-compute', 'neutron-server', 
                       'neutron-agent'
                       ]
    
    CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/{cluster_id}/ip_map_role.json'
    CLUSTER_IP_UID_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/{cluster_id}/ip_map_uid.json'
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
    logger.info('exec remote cmd:%s to ip:%s, the result:%s.' % (cmd, ip, result))
    pass

def getActiveRoleIPMap(cluster_id):
    if debug :
        print 'cluster_id=%s' % cluster_id
        clusterIPRoleMapFilePath = 'iprole.json'
        pass
    else :
        clusterIPRoleMapFilePath = Params.CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
        print 'clusterIPRoleMapFilePath=%s' % clusterIPRoleMapFilePath
        
        clusterIPUidMapFilePath = Params.CLUSTER_IP_UID_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
        print 'clusterIPUidMapFilePath=%s' % clusterIPUidMapFilePath
        pass
    
    print 'uid sort=============='
    jsonContent = FileUtil.readContent(clusterIPUidMapFilePath)
    ipUidMap = json.loads(jsonContent)
    
    uid_list = []
    for ip in ipUidMap.keys() :
        uid_list.append(ipUidMap[ip])
        pass
    
    #sort the tuple (ip, uid) by uid ascend
    ipUidTuple = sorted(ipUidMap.items(), key=lambda d: d[1]) 
    for s in ipUidTuple:
        print s
        print type(s)
        pass
    
    print 'uid sort=============='
    
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
    print 'sort the list by uid========'
    activeRoleIPMap = {}
    for role in roleIPMap.keys() :
        print 'role=%s' % role
        if len(roleIPMap[role]) > 0 :
            ip_list_sorted_by_uid = []
            #sort by uid for each role
            for tuple in ipUidTuple :
                for e in tuple : # (ip, uid)
                    if e in roleIPMap[role] :
                        ip_list_sorted_by_uid.append(e)
                        pass
                    pass
                pass
            activeRoleIPMap[role] = ip_list_sorted_by_uid
            print 'xxxx==='
            print type(activeRoleIPMap[role])
            pass
        pass
    
    print 'sorted table=========='
    for t in ipUidTuple :
        print t
            
    return activeRoleIPMap

def getInitCmdByRole(role):
    ######DEBUG
    version_tag = 'kilo'
    initCmd = 'hostname'
    
    if role == 'rabbitmq' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/rabbitmq/initRabbitmq.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'keystone' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/keystone/initKeystone.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'glance' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/glance/initGlance.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'cinder-api' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/cinder/initCinder.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'cinder-storage' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/cinderstorage/initCinderStorage.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'horizon' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/dashboard/initDashboard.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'heat' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/heat/initHeat.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'ceilometer' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/ceilometer/initCeilometer.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'nova-api' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/nova/initNova.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'nova-compute' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/novacompute/initNovaCompute.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'neutron-server' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/neutronserver/initNeutronServer.py'\
        .format(version_tag='kilo')
        pass
    
    if role == 'neutron-agent' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/{version_tag}/network/initNetwork.py'\
        .format(version_tag='kilo')
        pass
    
    return initCmd
    
    
    
if __name__ == '__main__':
    print 'init OpenStack HA----------------------'
#     if os.path.exists(TAG) :
#         logger.info('OpenStack HA has been initted-----')
#         pass
#     else :
    print ('start to init OpenStack HA----------------')
    cluster_id = ''
    argv = sys.argv
    argv.pop(0)
    print "agrv=%s--" % argv
    if debug == False :
        if len(argv) > 0 :
            cluster_id = str(argv[0])
            pass
        else :
            print "ERROR:no params, do not transter cluster_id to this init file yet."
            exit()
            pass
        pass
    else :
        print "debug mode.................."
        cluster_id = str(argv[0])
        print 'cluster_id=%s' % cluster_id
        pass
    
    TAG = '/opt/openstack_init_{cluster_id}'.format(cluster_id=str(cluster_id))
    if os.path.exists(TAG) :
        print ('OpenStack HA has been initted-----')
        pass
    else :
        activeRoleIPMap = getActiveRoleIPMap(cluster_id)
        
        CLUSTER_ROLE_MAP_JSON_FILE_PATH = Params.CLUSTER_ROLE_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
        FileUtil.writeContent(CLUSTER_ROLE_MAP_JSON_FILE_PATH, json.dumps(activeRoleIPMap, indent=4))
                              
        activeRoles = activeRoleIPMap.keys()
        print 'activeRoles=%s' % activeRoles
        #######DO EXECUTION
#         cluster_ip_list = []
        ##Do mysql execution
        mysql_ip_list = activeRoleIPMap['mysql']
        print 'mysql_ip_list=%s' % mysql_ip_list
        
        horizon_ip_list = activeRoleIPMap['horizon']
        print 'horizon_ip_list=%s' % horizon_ip_list
        nova_compute_ip_list = activeRoleIPMap['nova-compute']
        print 'nova_compute_ip_list=%s' % nova_compute_ip_list
        rabbitmq_ip_list = activeRoleIPMap['rabbitmq']
        print 'rabbitmq_ip_list=%s' % rabbitmq_ip_list
        pass    
        
        




