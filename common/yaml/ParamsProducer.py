'''
Created on Aug 26, 2015

@author: zhangbai
'''

'''
usage:

python ParamsProduer.py

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
SOURCE_KEYSTONE_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keystone.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil
from common.yaml.YAMLUtil import YAMLUtil

class ParamsProducer(object):
    '''
    classdocs
    '''
    OPENSTACK_ROLES = ['mysql', 'rabbitmq', 'mongodb', 'keystone', 'glance', 'nova-api', 'nova-compute',
                       'ceilometer', 'neutron-server', 'neutron', 'dashboard', 'cinder', 'cinder-storage']
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def produceIPList(role):
        YAMLUtil.writeIPList(role)
        pass
    pass



if __name__ == '__main__':
    print 'produe role ip list in /opt/{role_ip_list}======='
    for role in ParamsProducer.OPENSTACK_ROLES :
        if YAMLUtil.hasRoleInNodes(role) :
            YAMLUtil.writeIPList(role)
            pass
        pass
    
    print 'produce localip in /opt/localip'
    localIPPath = '/opt/localip'
    FileUtil.writeContent(localIPPath, YAMLUtil.getLocalIP())    
    print 'produce all params in /opt/openstack_conf/openstack_params.json'
    print 'mysql============================'
    role = 'mysql'
    if YAMLUtil.hasRole(role) :
        key = 'mysql_vip'
        mysql_vip = YAMLUtil.getValue(role, key)
        
        key = 'mysql_vip_interface'
        mysql_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'root_password'
        mysql_root_password = YAMLUtil.getValue(role, key)
        print 'mysql_vip=%s--' % mysql_vip
        print 'mysql_vip_interface=%s--' % mysql_vip_interface
        print 'mysql_password=%s--' % mysql_root_password
        
        mysql_ips_list = YAMLUtil.getRoleIPList(role)
        mysql_ips = ','.join(mysql_ips_list)
        print 'mysql_ips=%s' % mysql_ips
    
    print 'rabbitmq========================'
    role = 'rabbitmq'
    if YAMLUtil.hasRole(role) :
        key = 'rabbit_userid'
        rabbit_userid = YAMLUtil.getValue(role, key)
        
        key = 'rabbit_password'
        rabbit_password = YAMLUtil.getValue(role, key)
        
        key = 'rabbit_vip'
        rabbit_vip = YAMLUtil.getValue(role, key)
        
        key = 'rabbit_vip_interface'
        rabbit_vip_interface = YAMLUtil.getValue(role, key)
        
        rabbit_ips_list = YAMLUtil.getRoleIPList(role)
        rabbit_ips = ','.join(rabbit_ips_list)
        
        print 'rabbit_userid=%s--' % rabbit_userid
        print 'rabbit_vip=%s--' % rabbit_vip
        print 'rabbit_vip_interface=%s--' % rabbit_vip_interface
        print 'rabbit_password=%s--' % rabbit_password
        print 'rabbit_ips=%s--' % rabbit_ips
        pass
    
    print 'keystone========================='
    role = 'keystone'
    if YAMLUtil.hasRole(role) :
        key = 'keystone_vip'
        keystone_vip = YAMLUtil.getValue(role, key)
        
        key = 'keystone_vip_interface'
        keystone_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'keystone_mysql_user'
        keystone_mysql_user = YAMLUtil.getValue(role, key)
        
        key = 'keystone_mysql_password'
        keystone_mysql_password = YAMLUtil.getValue(role, key)
        
        keystone_ips_list = YAMLUtil.getRoleIPList(role)
        keystone_ips = ','.join(keystone_ips_list)
        
        print 'keystone_vip=%s--' % keystone_vip
        print 'keystone_vip_interface=%s--' % keystone_vip_interface
        print 'keystone_mysql_user=%s--' % keystone_mysql_user 
        print 'keystone_ips=%s--' % keystone_ips
        pass
    
    #NOT TEST
    print 'glance====================================='
    role = 'glance'
    if YAMLUtil.hasRole(role) :
        key = 'glance_vip'
        glance_vip = YAMLUtil.getValue(role, key)
        
        key = 'glance_vip_interface'
        glance_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'glance_mysql_user'
        glance_mysql_user = YAMLUtil.getValue(role, key)
        
        key = 'glance_mysql_password'
        glance_mysql_password = YAMLUtil.getValue(role, key)
        
        glance_ips_list = YAMLUtil.getRoleIPList(role)
        glance_ips = ','.join(glance_ips_list)
        
        print 'glance_vip=%s--' % glance_vip
        print 'glance_vip_interface=%s--' % glance_vip_interface
        print 'glance_mysql_user=%s--' % glance_mysql_user
        print 'glance_mysql_password=%s--' % glance_mysql_password 
        print 'glance_ips=%s--' % glance_ips
        pass
    #NOT TEST
    print 'neutron-server========================================='
    role = 'neutron-server'
    if YAMLUtil.hasRole(role) :
        key = 'neutron_server_vip'
        neutron_server_vip = YAMLUtil.getValue(role, key)
        
        key = 'neutron_server_vip_interface'
        neutron_server_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'network_mode'
        network_mode = YAMLUtil.getValue(role, key)
        
        key = 'neutron_server_mysql_user'
        neutron_mysql_user = YAMLUtil.getValue(role, key)
        key = 'neutron_server_mysql_password'
        neutron_mysql_user_password = YAMLUtil.getValue(role, key)
        
        neutron_server_ip_list = YAMLUtil.getRoleIPList(role)
        neutron_server_ips = ','.join(neutron_server_ip_list)
        
        print 'neutron_server_vip=%s--' % neutron_server_vip
        print 'neutron_server_vip_interface=%s--' % neutron_server_vip_interface
        print 'network_mode=%s--' % network_mode
        
        print 'neutron_mysql_user=%s--' % neutron_mysql_user
        print 'neutron_mysql_user_password=%s--' % neutron_mysql_user_password
        
        print 'neutron_server_ips=%s--' % neutron_server_ips
        pass
    
    print 'nova-api========================================='
    role = 'nova-api'
    if YAMLUtil.hasRole(role): 
        key = 'nova_api_vip'
        nova_api_vip = YAMLUtil.getValue(role, key)
        
        key = 'nova_api_vip_interface'
        nova_api_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'nova_api_mysql_user'
        nova_api_mysql_user = YAMLUtil.getValue(role, key)
        
        key = 'nova_api_mysql_password'
        nova_api_mysql_password = YAMLUtil.getValue(role, key)
        
        nova_api_ip_list = YAMLUtil.getRoleIPList(role)
        nova_api_ips = ','.join(nova_api_ip_list)
        
        print 'nova_api_vip=%s--' % nova_api_vip
        print 'nova_api_vip_interface=%s--' % nova_api_vip_interface
        print 'nova_api_mysql_user=%s--' % nova_api_mysql_user
        print 'nova_api_mysql_password=%s--' % nova_api_mysql_password
        
        print 'nova_api_ips=%s--' % nova_api_ips
        print YAMLUtil.hasRoleInNodes('nova-api')
    
    print 'nova-compute============================================='
    role = 'nova-compute'
    if YAMLUtil.hasRole(role): 
        key = 'virt_type'
        virt_type= YAMLUtil.getValue(role, key)
        print 'virt_type=%s' % virt_type
        
        nova_compute_ip_list = YAMLUtil.getRoleIPList(role)
        nova_compute_ips = ','.join(nova_compute_ip_list)
        print 'nova_compute_ips=%s--' % nova_compute_ips
        
    print 'local_ip=%s--' % YAMLUtil.getLocalIP()
    
    print 'cinder============================================'
    
    
        
    
    
    
    
        
    
        
    print 'produce role list done#######'
