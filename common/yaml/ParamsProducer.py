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
                       'ceilometer', 'neutron-server', 'neutron', 'horizon', 'cinder-api', 'cinder-storage', 'heat']
    
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
    paramsMap = {}
    print 'mysql============================'
    role = 'mysql'
    if YAMLUtil.hasRoleInNodes(role):
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
        paramsMap['mysql_vip'] = mysql_vip
        paramsMap['mysql_vip_interface'] = mysql_vip_interface
        paramsMap['mysql_password'] = mysql_root_password
        paramsMap['mysql_ips'] = mysql_ips
        
        
    
    print 'rabbitmq========================'
    role = 'rabbitmq'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'rabbit_userid'
        rabbit_userid = YAMLUtil.getValue(role, key)
        
        key = 'rabbit_password'
        rabbit_password = YAMLUtil.getValue(role, key)
        
        key = 'rabbit_vip'
        rabbit_vip = YAMLUtil.getValue(role, key)
        
        key = 'rabbit_vip_interface'
        rabbit_vip_interface = YAMLUtil.getValue(role, key)
        
        rabbit_ips_list = YAMLUtil.getRabbitRoleIPList(role)
        rabbit_ips = ','.join(rabbit_ips_list)
        
        print 'rabbit_userid=%s--' % rabbit_userid
        print 'rabbit_vip=%s--' % rabbit_vip
        print 'rabbit_vip_interface=%s--' % rabbit_vip_interface
        print 'rabbit_password=%s--' % rabbit_password
        print 'rabbit_ips=%s--' % rabbit_ips
        
        rabbit_hosts_list = [] #rabbit_ip1:5672,rabbit_ip2:5672
        
        for ip in rabbit_ips_list :
            rabbit_with_port = '%s:5672' % ip
            rabbit_hosts_list.append(rabbit_with_port)
            pass
        paramsMap['rabbit_hosts'] = ','.join(rabbit_hosts_list)
        paramsMap['rabbit_host'] = rabbit_ips_list[0]
        paramsMap['rabbit_vip'] = rabbit_vip
        paramsMap['rabbit_vip_interface'] = rabbit_vip_interface
        paramsMap['rabbit_userid'] = rabbit_userid
        paramsMap['rabbit_password'] = rabbit_password
        
        pass
    
    print 'keystone========================='
    role = 'keystone'
    if YAMLUtil.hasRoleInNodes(role):
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
        
        paramsMap['keystone_vip'] = keystone_vip
        paramsMap['keystone_vip_interface'] = keystone_vip_interface
        paramsMap['keystone_mysql_user'] = keystone_mysql_user
        paramsMap['keystone_mysql_password'] = keystone_mysql_password
        paramsMap['keystone_ips'] = keystone_ips
        
        pass
    
    print 'glance====================================='
    role = 'glance'
    if YAMLUtil.hasRoleInNodes(role):
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
        paramsMap['glance_vip'] = glance_vip
        paramsMap['glance_vip_interface'] = glance_vip_interface
        paramsMap['glance_mysql_user'] = glance_mysql_user
        paramsMap['glance_mysql_password'] = glance_mysql_password
        paramsMap['glance_ips'] = glance_ips
        pass

    print 'neutron-server========================================='
    role = 'neutron-server'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'neutron_vip'
        neutron_vip = YAMLUtil.getValue(role, key)
        
        key = 'neutron_vip_interface'
        neutron_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'network_mode'
        network_mode = YAMLUtil.getValue(role, key)
        
        key = 'neutron_mysql_user'
        neutron_mysql_user = YAMLUtil.getValue(role, key)
        key = 'neutron_mysql_password'
        neutron_mysql_password = YAMLUtil.getValue(role, key)
        
        neutron_ip_list = YAMLUtil.getRoleIPList(role)
        neutron_ips = ','.join(neutron_ip_list)
        
        print 'neutron_vip=%s--' % neutron_vip
        print 'neutron_vip_interface=%s--' % neutron_vip_interface
        print 'network_mode=%s--' % network_mode
        
        print 'neutron_mysql_user=%s--' % neutron_mysql_user
        print 'neutron_mysql_user_password=%s--' % neutron_mysql_password
        
        print 'neutron_ips=%s--' % neutron_ips
        paramsMap['neutron_vip'] = neutron_vip
        paramsMap['neutron_vip_interface'] = neutron_vip_interface
        paramsMap['neutron_mysql_user'] = neutron_mysql_user
        paramsMap['neutron_mysql_password'] = neutron_mysql_password
        paramsMap['network_mode'] = network_mode
        paramsMap['neutron_ips'] = neutron_ips
        pass
    
    print 'nova-api========================================='
    role = 'nova-api'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'nova_vip'
        nova_vip = YAMLUtil.getValue(role, key)
        
        key = 'nova_vip_interface'
        nova_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'nova_mysql_user'
        nova_mysql_user = YAMLUtil.getValue(role, key)
        
        key = 'nova_mysql_password'
        nova_mysql_password = YAMLUtil.getValue(role, key)
        
        nova_ip_list = YAMLUtil.getRoleIPList(role)
        nova_ips = ','.join(nova_ip_list)
        
        print 'nova_vip=%s--' % nova_vip
        print 'nova_vip_interface=%s--' % nova_vip_interface
        print 'nova_mysql_user=%s--' % nova_mysql_user
        print 'nova_mysql_password=%s--' % nova_mysql_password
        
        print 'nova_ips=%s--' % nova_ips
        print YAMLUtil.hasRoleInNodes('nova-api')
        paramsMap['nova_vip'] = nova_vip
        paramsMap['nova_vip_interface'] = nova_vip_interface
        paramsMap['nova_mysql_user'] = nova_mysql_user
        paramsMap['nova_mysql_password'] = nova_mysql_password
        paramsMap['nova_ips'] = nova_ips
        pass
          
    
    print 'nova-compute============================================='
    role = 'nova-compute'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'virt_type'
        virt_type= YAMLUtil.getValue(role, key)
        print 'virt_type=%s' % virt_type
        
        nova_compute_ip_list = YAMLUtil.getRoleIPList(role)
        nova_compute_ips = ','.join(nova_compute_ip_list)
        print 'nova_compute_ips=%s--' % nova_compute_ips
        paramsMap['virt_type'] = virt_type
        paramsMap['nova_compute_ips'] = nova_compute_ips
        pass
    
    role = 'horizon'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'dashboard_vip'
        dashboard_vip= YAMLUtil.getValue(role, key)
        key = 'dashboard_vip_interface'
        dashboard_vip_interface = YAMLUtil.getValue(role, key)
        
        dashboard_ips_list = YAMLUtil.getRoleIPList(role)
        dashboard_ips = ','.join(dashboard_ips_list)
        print 'dashboard_vip=%s--' % dashboard_vip
        print 'dashboard_vip_interface=%s--' % dashboard_vip_interface
        print 'dashboard_ips=%s--' % dashboard_ips
        paramsMap['dashboard_vip'] = dashboard_vip
        paramsMap['dashboard_vip_interface'] = dashboard_vip_interface
        paramsMap['dashboard_ips'] = dashboard_ips
        pass
        
    print 'cinder============================================'
    role = 'cinder-api'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'cinder_vip'
        cinder_vip = YAMLUtil.getValue(role, key)
        
        key = 'cinder_vip_interface'
        cinder_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'cinder_mysql_user'
        cinder_mysql_user = YAMLUtil.getValue(role, key)
        
        key = 'cinder_mysql_password'
        cinder_mysql_password = YAMLUtil.getValue(role, key)
        
        cinder_ips_list = YAMLUtil.getRoleIPList(role)
        cinder_ips = ','.join(cinder_ips_list)
        print 'cinder_vip=%s-' % cinder_vip
        print 'cinder_vip_interface=%s--' % cinder_vip_interface
        print 'cinder_mysql_user=%s--' % cinder_mysql_user
        print 'cinder_mysql_password=%s--' % cinder_mysql_password
        print 'cinder_ips=%s--' % cinder_ips
        paramsMap['cinder_vip'] = cinder_vip
        paramsMap['cinder_vip_interface'] = cinder_vip_interface
        paramsMap['cinder_mysql_user'] = cinder_mysql_user
        paramsMap['cinder_mysql_password'] = cinder_mysql_password
        paramsMap['cinder_ips'] = cinder_ips
        pass
    
    print 'cinder-storage============================================'
    role = 'cinder-storage'
    if YAMLUtil.hasRoleInNodes(role):
        cinder_storage_ips_list = YAMLUtil.getRoleIPList(role)
        cinder_storage_ips = ','.join(cinder_storage_ips_list)
        print 'cinder_storage_ips=%s--' % cinder_ips
        paramsMap['cinder_storage_ips'] = cinder_storage_ips
        pass
    
    print 'heat============================================'
    role = 'heat'
    if YAMLUtil.hasRoleInNodes(role):
        heat_ips_list = YAMLUtil.getRoleIPList(role)
        heat_ips = ','.join(heat_ips_list)
        print 'heat_ips=%s--' % heat_ips
        
        key = 'heat_vip'
        heat_vip = YAMLUtil.getValue(role, key)
        
        key = 'heat_vip_interface'
        heat_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'heat_mysql_user'
        heat_mysql_user = YAMLUtil.getValue(role, key)
        
        key = 'heat_mysql_password'
        heat_mysql_password = YAMLUtil.getValue(role, key)
        
        paramsMap['heat_ips'] = heat_ips
        paramsMap['heat_vip'] = heat_vip
        paramsMap['heat_vip_interface'] = heat_vip_interface
        paramsMap['heat_mysql_user'] = heat_mysql_user
        paramsMap['heat_mysql_password'] = heat_mysql_password
        pass
    
    print 'neutron============================================'
    role = 'neutron'
    if YAMLUtil.hasRoleInNodes(role):
        neutron_service_ips_list = YAMLUtil.getRoleIPList(role)
        neutron_service_ips = ','.join(neutron_service_ips_list)
        print 'neutron_service_ips=%s--' % neutron_service_ips
        paramsMap['neutron_service_ips'] = neutron_service_ips
        pass
    
    print 'ceilometer==========================================='
    role = 'ceilometer'
    if YAMLUtil.hasRoleInNodes(role):
        key = 'ceilometer_vip'
        ceilometer_vip = YAMLUtil.getValue(role, key)
        
        key = 'ceilometer_vip_interface'
        ceilometer_vip_interface = YAMLUtil.getValue(role, key)
        
        key = 'ceilometer_mongo_user'
        ceilometer_mongo_user = YAMLUtil.getValue(role, key)
        
        key = 'ceilometer_mongo_password'
        ceilometer_mongo_password = YAMLUtil.getValue(role, key)
        
        ceilometer_ips_list = YAMLUtil.getRoleIPList(role)
        ceilometer_ips = ','.join(ceilometer_ips_list)
        print 'ceilometer_vip=%s-' % ceilometer_vip
        print 'ceilometer_vip_interface=%s--' % ceilometer_vip_interface
        print 'ceilometer_mongo_user=%s--' % ceilometer_mongo_user
        print 'ceilometer_mongo_password=%s--' % ceilometer_mongo_password
        print 'ceilometer_ips=%s--' % ceilometer_ips
        paramsMap['ceilometer_vip'] = ceilometer_vip
        paramsMap['ceilometer_vip_interface'] = ceilometer_vip_interface
        paramsMap['ceilometer_mongo_user'] = ceilometer_mongo_user
        paramsMap['ceilometer_mongo_password'] = ceilometer_mongo_password
        paramsMap['ceilometer_ips'] = ceilometer_ips
        pass
    
    openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
    admin_email = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'ADMIN_EMAIL')
    
    paramsMap['admin_email'] = admin_email
    
    import json
    jsonParams = json.dumps(paramsMap,indent=4)
    print jsonParams
    print type(jsonParams)
    
    openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
    openstackConfBaseDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_CONF_BASE_DIR')
    if not os.path.exists(openstackConfBaseDir) :
        ShellCmdExecutor.execCmd("mkdir %s" % openstackConfBaseDir)
        pass
    openstackParamsFilePath = os.path.join(openstackConfBaseDir, 'openstack_params.json')
    FileUtil.writeContent(openstackParamsFilePath, jsonParams)
    
    print 'produce role list done#######'
    
