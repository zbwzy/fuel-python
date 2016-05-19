'''
Created on Oct 29, 2015

@author: zhangbai
'''

'''
usage:

python ParamsProduer.py

NOTE: the params is from conf/openstack_params.json, this file is called when user drives FUEL to install env.
'''
import sys
import os
import time

debug = False
if debug == True :
    #MODIFY HERE WHEN DO LOCAL DEV
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass

OPENSTACK_VERSION_TAG = 'kilo'
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
    OPENSTACK_ROLES = ['haproxy-keepalived', 'mysql', 'rabbitmq', 'mongodb', 'keystone', 'glance', 'nova-api', 
                       'nova-compute','ceilometer', 'neutron-server', 'neutron', 'horizon', 'cinder-api', 
                       'cinder-storage', 'heat'
                       ]
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def produceIPList(role):
        YAMLUtil.writeIPList(role)
        pass
    
    @staticmethod
    def isExistElementInArray(element, arrayList):
        boolResult = False
        for e in arrayList :
            if element == e :
                boolResult = True
                break
            pass
        
        return boolResult
    
    @staticmethod
    def produce():
        print 'produe role ip list in /opt/{role}_ip_list======='
        for role in ParamsProducer.OPENSTACK_ROLES :
            if YAMLUtil.hasRoleInNodes(role) :
                YAMLUtil.writeIPList(role)
                pass
            pass
        
        print 'produce local management ip in /opt/localip'
        localIPPath = '/opt/localip'
        FileUtil.writeContent(localIPPath, YAMLUtil.getManagementIP())    
        
        print 'produce all params in /opt/openstack_conf/openstack_params.json'
        paramsMap = {}
        #global variables
        print 'global==========================='
        fuel_master_ip = YAMLUtil.getValue('global', 'fuel_master_ip')
        paramsMap['fuel_master_ip'] = fuel_master_ip
        
        admin_token = YAMLUtil.getValue('global', 'admin_token')
        paramsMap['admin_token'] = admin_token
        
        cinder_dbpass = YAMLUtil.getValue('global', 'cinder_dbpass')
        paramsMap['cinder_dbpass'] = cinder_dbpass
        
        keystone_heat_password = YAMLUtil.getValue('global', 'keystone_heat_password')
        paramsMap['keystone_heat_password'] = keystone_heat_password
        
        keystone_neutron_password = YAMLUtil.getValue('global', 'keystone_neutron_password')
        paramsMap['keystone_neutron_password'] = keystone_neutron_password
        
        keystone_admin_password = YAMLUtil.getValue('global', 'keystone_admin_password')
        paramsMap['keystone_admin_password'] = keystone_admin_password
        
        keystone_glance_password = YAMLUtil.getValue('global', 'keystone_glance_password')
        paramsMap['keystone_glance_password'] = keystone_glance_password
        
        neutron_dbpass = YAMLUtil.getValue('global', 'neutron_dbpass')
        paramsMap['neutron_dbpass'] = neutron_dbpass
        
        keystone_cinder_password = YAMLUtil.getValue('global', 'keystone_cinder_password')
        paramsMap['keystone_cinder_password'] = keystone_cinder_password
        
        nova_dbpass = YAMLUtil.getValue('global', 'nova_dbpass')
        paramsMap['nova_dbpass'] = nova_dbpass
        
        keystone_nova_password = YAMLUtil.getValue('global', 'keystone_nova_password')
        paramsMap['keystone_nova_password'] = keystone_nova_password
        
        ceilometer_dbpass = YAMLUtil.getValue('global', 'ceilometer_dbpass')
        paramsMap['ceilometer_dbpass'] = ceilometer_dbpass
        
        heat_dbpass = YAMLUtil.getValue('global', 'heat_dbpass')
        paramsMap['heat_dbpass'] = heat_dbpass
        
        bclinux_repo_url = YAMLUtil.getValue('global', 'bclinux_repo_url')
        paramsMap['bclinux_repo_url'] = bclinux_repo_url
        
        glance_dbpass = YAMLUtil.getValue('global', 'glance_dbpass')
        paramsMap['glance_dbpass'] = glance_dbpass
        
        keystone_dbpass = YAMLUtil.getValue('global', 'keystone_dbpass')
        paramsMap['keystone_dbpass'] = keystone_dbpass
        
        keystone_ceilometer_password = YAMLUtil.getValue('global', 'keystone_ceilometer_password')
        paramsMap['keystone_ceilometer_password'] = keystone_ceilometer_password
        
        cluster_id = YAMLUtil.getValue('global', 'cluster_id')
        paramsMap['cluster_id'] = cluster_id
        
        fuel_master_ip = YAMLUtil.getValue('global', 'fuel_master_ip')
        paramsMap['fuel_master_ip'] = fuel_master_ip
        
        print 'mysql============================'
        #Judge whether current host is mysql role
        role = 'mysql'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            key = 'root_password'
            mysql_root_password = YAMLUtil.getValue(role, key)
            print 'mysql_password=%s--' % mysql_root_password
            
            mysql_ips_list = YAMLUtil.getRoleManagementIPList(role)
            mysql_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            mysql_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            paramsMap['mysql'] = {}
            mysqlParams = paramsMap['mysql']
            
            mysqlParams['mysql_password'] = mysql_root_password
            mysqlParams['mgmt_ips'] = mysql_ips_list
            mysqlParams['storage_ips'] = mysql_storage_ips_list
            mysqlParams['ex_ips'] = mysql_ex_ips_list
            
            if YAMLUtil.getManagementIP() in mysql_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
    #         else:
    #             FileUtil.writeContent(is_mysql_role_file_path, 'false')
    #             pass
    #         pass
    #     else :
    #         FileUtil.writeContent(is_mysql_role_file_path, 'false')
    #         pass
            
        print 'rabbitmq========================'
        role = 'rabbitmq'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            key = 'rabbit_userid'
            rabbit_userid = 'nova'
#             rabbit_userid = YAMLUtil.getValue(role, key)
            
            key = 'rabbit_password'
            rabbit_password = YAMLUtil.getValue(role, key)
            
            rabbit_ips_list = YAMLUtil.getRabbitRoleManagementIPList(role)
            rabbit_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            rabbit_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            #Judge rabbitmq master ip
            rabbit_master_ip = rabbit_ips_list[0]
            FileUtil.writeContent('/opt/rabbitmq_master_ip', rabbit_master_ip)
            
            print 'rabbit_userid=%s--' % rabbit_userid
            print 'rabbit_password=%s--' % rabbit_password
            
            rabbit_hosts_list = [] #rabbit_ip1:5672,rabbit_ip2:5672
            
            for ip in rabbit_ips_list :
                rabbit_with_port = '%s:5672' % ip
                rabbit_hosts_list.append(rabbit_with_port)
                pass
            
            paramsMap['rabbitmq'] = {}
            rabbitParams = paramsMap['rabbitmq']
            
            rabbitParams['rabbit_hosts'] = ','.join(rabbit_hosts_list)
            rabbitParams['rabbit_host'] = rabbit_ips_list[0]
            rabbitParams['rabbit_userid'] = rabbit_userid
            rabbitParams['rabbit_password'] = rabbit_password
            rabbitParams['mgmt_ips'] = rabbit_ips_list
            rabbitParams['storage_ips'] = rabbit_storage_ips_list
            rabbitParams['ex_ips'] = rabbit_ex_ips_list
            
            if YAMLUtil.getManagementIP() in rabbit_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        print 'keystone========================='
        role = 'keystone'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            
            keystone_mysql_user = 'keystone'
            
            #key = 'keystone_mysql_password'
            #keystone_mysql_password = YAMLUtil.getValue(role, key)
            
            keystone_ips_list = YAMLUtil.getRoleManagementIPList(role)
            keystone_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            keystone_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            print 'keystone_mysql_user=%s--' % keystone_mysql_user 
            
            paramsMap[role] = {}
            keystoneParams = paramsMap[role]
            
            keystoneParams['keystone_mysql_user'] = keystone_mysql_user
            keystoneParams['mgmt_ips'] = keystone_ips_list
            keystoneParams['storage_ips'] = keystone_storage_ips_list
            keystoneParams['ex_ips'] = keystone_ex_ips_list
            
            #XXXXX 11111
#             keystoneParams['keystone_ips'] = keystone_ips
            
            if YAMLUtil.getManagementIP() in keystone_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
    #         else:
    #             FileUtil.writeContent(is_keystone_role_file_path, 'false')
    #             pass
    #         pass
    #     else :
    #         FileUtil.writeContent(is_keystone_role_file_path, 'false')
    #         pass
        
        print 'glance====================================='
        role = 'glance'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            key = 'glance_vip'
            glance_vip = YAMLUtil.getValue(role, key)
            
            key = 'glance_mysql_user'
            glance_mysql_user = YAMLUtil.getValue(role, key)
            
            #key = 'glance_mysql_password'
            #glance_mysql_password = YAMLUtil.getValue(role, key)
            
            glance_ips_list = YAMLUtil.getRoleManagementIPList(role)
            
            glance_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            glance_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            print 'glance_vip=%s--' % glance_vip
            print 'glance_mysql_user=%s--' % glance_mysql_user
            #print 'glance_mysql_password=%s--' % glance_mysql_password 
            
            paramsMap['glance'] = {}
            glanceParams = paramsMap['glance']
            glanceParams['glance_mysql_user'] = glance_mysql_user
            glanceParams['mgmt_ips'] = glance_ips_list
            glanceParams['storage_ips'] = glance_storage_ips_list
            glanceParams['ex_ips'] = glance_ex_ips_list
            #paramsMap['glance_mysql_password'] = glance_mysql_password
            
            if YAMLUtil.getManagementIP() in glance_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
    
        print 'neutron-server========================================='
        role = 'neutron-server'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            key = 'vlan_id_range'
            vlan_id_range = YAMLUtil.getValue(role, key)
            
            key = 'neutron_network_mode'
            neutron_network_mode = YAMLUtil.getValue(role, key)
            
            key = 'neutron_mysql_user'
#             neutron_mysql_user = YAMLUtil.getValue(role, key)
            neutron_mysql_user = "neutron"
            #key = 'neutron_mysql_password'
            #neutron_mysql_password = YAMLUtil.getValue(role, key)
            
            neutron_ip_list = YAMLUtil.getRoleManagementIPList(role)
            neutron_storage_ip_list = YAMLUtil.getRoleStorageIPList(role)
            neutron_ex_ip_list = YAMLUtil.getRoleExIPList(role)
            
            print 'vlan_id_range=%s--' % vlan_id_range
            print 'neutron_network_mode=%s--' % neutron_network_mode
            
            print 'neutron_mysql_user=%s--' % neutron_mysql_user
            #print 'neutron_mysql_user_password=%s--' % neutron_mysql_password
            
            paramsMap['neutron-server'] = {}
            neutronServerParams = paramsMap['neutron-server']
            neutronServerParams['vlan_id_range'] = vlan_id_range
            neutronServerParams['neutron_mysql_user'] = neutron_mysql_user
            #neutronServerParams['neutron_mysql_password'] = neutron_mysql_password
            neutronServerParams['neutron_network_mode'] = neutron_network_mode
            neutronServerParams['mgmt_ips'] = neutron_ip_list
            neutronServerParams['storage_ips'] = neutron_storage_ip_list
            neutronServerParams['ex_ips'] = neutron_ex_ip_list
            
            if YAMLUtil.getManagementIP() in neutron_ip_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        print 'nova-api========================================='
        role = 'nova-api'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            
            key = 'nova_mysql_user'
            nova_mysql_user = "nova"
#             nova_mysql_user = YAMLUtil.getValue(role, key)
            
            #key = 'nova_mysql_password'
            #nova_mysql_password = YAMLUtil.getValue(role, key)
            
            nova_ip_list = YAMLUtil.getRoleManagementIPList(role)
            nova_storage_ip_list = YAMLUtil.getRoleStorageIPList(role)
            nova_ex_ip_list = YAMLUtil.getRoleExIPList(role)
            
            print 'nova_mysql_user=%s--' % nova_mysql_user
            #print 'nova_mysql_password=%s--' % nova_mysql_password
            
            print YAMLUtil.hasRoleInNodes('nova-api')
            paramsMap[role] = {}
            novaApiParams = paramsMap[role]
            novaApiParams['nova_mysql_user'] = nova_mysql_user
            novaApiParams['mgmt_ips'] = nova_ip_list
            novaApiParams['storage_ips'] = nova_storage_ip_list
            novaApiParams['ex_ips'] = nova_ex_ip_list
            #paramsMap['nova_mysql_password'] = nova_mysql_password
            
            if YAMLUtil.getManagementIP() in nova_ip_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        print 'nova-compute============================================='
        role = 'nova-compute'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            key = 'virt_type'
            virt_type= YAMLUtil.getValue(role, key)
            print 'virt_type=%s' % virt_type
            
            nova_compute_ip_list = YAMLUtil.getRoleManagementIPList(role)
            nova_compute_storage_ip_list = YAMLUtil.getRoleStorageIPList(role)
            nova_compute_ex_ip_list = YAMLUtil.getRoleExIPList(role)
            
            paramsMap[role] = {}
            novaComputeParams = paramsMap[role]
            novaComputeParams['virt_type'] = virt_type
            novaComputeParams['mgmt_ips'] = nova_compute_ip_list
            novaComputeParams['storage_ips'] = nova_compute_storage_ip_list
            novaComputeParams['ex_ips'] = nova_compute_ex_ip_list
            
            if YAMLUtil.getManagementIP() in nova_compute_ip_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        role = 'horizon'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            dashboard_ips_list = YAMLUtil.getRoleManagementIPList(role)
            dashboard_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            dashboard_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            paramsMap[role] = {}
            horizonParams = paramsMap[role]
            horizonParams["mgmt_ips"] = dashboard_ips_list
            horizonParams["storage_ips"] = dashboard_storage_ips_list
            horizonParams["ex_ips"] = dashboard_ex_ips_list
            
            if YAMLUtil.getManagementIP() in dashboard_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
            
        print 'cinder============================================'
        role = 'cinder-api'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
#             key = 'cinder_mysql_user'
#             cinder_mysql_user = YAMLUtil.getValue(role, key)
            cinder_mysql_user = "cinder"
            
            cinder_ips_list = YAMLUtil.getRoleManagementIPList(role)
            cinder_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            cinder_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            print 'cinder_mysql_user=%s--' % cinder_mysql_user
            paramsMap[role] = {}
            cinderParams = paramsMap[role]
            cinderParams['cinder_mysql_user'] = cinder_mysql_user
            cinderParams["mgmt_ips"] = cinder_ips_list
            cinderParams["storage_ips"] = cinder_storage_ips_list
            cinderParams["ex_ips"] = cinder_ex_ips_list
            #XXXXX
#             paramsMap['cinder_ips'] = cinder_ips
            
            if YAMLUtil.getManagementIP() in cinder_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        print 'cinder-storage============================================'
        role = 'cinder-storage'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            cinder_ips_list = YAMLUtil.getRoleManagementIPList(role)
            cinder_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            cinder_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            paramsMap[role] = {}
            cinderStorageParams = paramsMap[role]
            cinderStorageParams["mgmt_ips"] = cinder_ips_list
            cinderStorageParams["storage_ips"] = cinder_storage_ips_list
            cinderStorageParams["ex_ips"] = cinder_ex_ips_list
            
            if YAMLUtil.getManagementIP() in cinder_storage_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        print 'heat============================================'
        role = 'heat'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            heat_ips_list = YAMLUtil.getRoleManagementIPList(role)
            heat_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            heat_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
#             key = 'heat_mysql_user'
#             heat_mysql_user = YAMLUtil.getValue(role, key)
            heat_mysql_user = "heat"
            paramsMap[role] = {}
            heatParams = paramsMap[role]
#             paramsMap['heat_ips'] = heat_ips
            heatParams["mgmt_ips"] = heat_ips_list
            heatParams["storage_ips"] = heat_storage_ips_list
            heatParams["ex_ips"] = heat_ex_ips_list
            heatParams['heat_mysql_user'] = heat_mysql_user
            
            if YAMLUtil.getManagementIP() in heat_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
        #Network Node
        print 'neutron-agent============================================'
        role = 'neutron-agent'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            net_node_ips_list = YAMLUtil.getRoleManagementIPList(role)
            net_node_storage_ips_list = YAMLUtil.getRoleStorageIPList(role)
            net_node_ex_ips_list = YAMLUtil.getRoleExIPList(role)
            
            key = 'interface_name'
            physical_external_network_interface = YAMLUtil.getValue(role, key)
            print 'physical_external_network_interface=%s--' % physical_external_network_interface
            
            paramsMap['network'] = {}
            networkParams = paramsMap['network']
            networkParams["mgmt_ips"] = net_node_ips_list
            networkParams["storage_ips"] = net_node_storage_ips_list
            networkParams["ex_ips"] = net_node_ex_ips_list
            networkParams['physical_external_network_interface'] = physical_external_network_interface
            
            #REFACTOR LATER
            networkParams['metadata_secret'] = '123456'
            
            if YAMLUtil.getManagementIP() in net_node_ips_list :
                FileUtil.writeContent(is_role_file_path, 'true')
                pass
            pass
        
#         print 'mongodb==========================================='
#         role = 'mongodb'
#         is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
#         if YAMLUtil.hasRoleInNodes(role):
#             #refactor later
#     #         key = 'mongodb_vip'
#     #         mongodb_vip = YAMLUtil.getValue(role, key)
#     #         
#     #         key = 'mongodb_vip_interface'
#     #         mongodb_vip_interface = YAMLUtil.getValue(role, key)
#             
#             mongodb_ips_list = YAMLUtil.getRoleManagementIPList(role)
#             mongodb_ips = ','.join(mongodb_ips_list)
#             
#             #refactor later
#             mongodb_vip = mongodb_ips_list[0]
#             mongodb_vip_interface = 'eth0'
#             print 'mongodb_vip=%s-' % mongodb_vip
#             print 'mongodb_vip_interface=%s--' % mongodb_vip_interface
#             paramsMap['mongodb_vip'] = mongodb_vip
#             paramsMap['mongodb_vip_interface'] = mongodb_vip_interface
#             paramsMap['mongodb_ips'] = mongodb_ips
#             
#             if ParamsProducer.isExistElementInArray(YAMLUtil.getLocalIP(), mongodb_ips_list) :
#                 FileUtil.writeContent(is_role_file_path, 'true')
#                 pass
#             pass
        
        print 'ceilometer==========================================='
        role = 'ceilometer'
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        if YAMLUtil.hasRoleInNodes(role):
            print 'Do nothing currently======='
#             key = 'ceilometer_mongo_user'
#             ceilometer_mongo_user = YAMLUtil.getValue(role, key)
#             
#             key = 'ceilometer_mongo_password'
#             ceilometer_mongo_password = YAMLUtil.getValue(role, key)
#             
#             ceilometer_ips_list = YAMLUtil.getRoleManagementIPList(role)
#             ceilometer_ips = ','.join(ceilometer_ips_list)
#             print 'ceilometer_mongo_user=%s--' % ceilometer_mongo_user
#             print 'ceilometer_mongo_password=%s--' % ceilometer_mongo_password
#             print 'ceilometer_ips=%s--' % ceilometer_ips
#             paramsMap['ceilometer_mongo_user'] = ceilometer_mongo_user
#             paramsMap['ceilometer_mongo_password'] = ceilometer_mongo_password
#             paramsMap['ceilometer_ips'] = ceilometer_ips
#             
#             #REFACTOR LATER
#             ceilometer_metering_secret = '7c1edcdfc1b2841c21ff'
#             paramsMap['ceilometer_metering_secret'] = ceilometer_metering_secret
#             
#             if YAMLUtil.getManagementIP() in ceilometer_ips_list :
#                 FileUtil.writeContent(is_role_file_path, 'true')
            pass
        
        print 'get global var==========================================='
        role = 'global'
        neutron_dbpass = YAMLUtil.getValue(role, 'neutron_dbpass')
        nova_dbpass = YAMLUtil.getValue(role, 'nova_dbpass')
        
        paramsMap['neutron_dbpass'] = YAMLUtil.getValue(role, 'neutron_dbpass')
        paramsMap['nova_dbpass'] =  YAMLUtil.getValue(role, 'nova_dbpass')
            
        #HA: only 2,master-backup mutually
        print 'haproxy-keepalived=================='
        role = 'haproxy-keepalived'
        if YAMLUtil.hasRoleInNodes(role):
            ha_vip1 = YAMLUtil.getValue(role, 'haproxy_vip1')
            ha_vip2 = YAMLUtil.getValue(role, 'haproxy_vip2')
            ha_vip1_interface = YAMLUtil.getValue(role, 'haproxy_vipinterface1')
            ha_vip2_interface = YAMLUtil.getValue(role, 'haproxy_vipinterface2')
            
            paramsMap[role] = {}
            haParams = paramsMap[role]
            haParams['ha_vip1'] = ha_vip1
            haParams['ha_vip2'] = ha_vip2
            haParams['ha_vip1_interface'] = ha_vip1_interface
            haParams['ha_vip2_interface'] = ha_vip2_interface
            
            print 'ha ip list=============='
            ha_ips_list = YAMLUtil.getRoleManagementIPList(role)
            haParams['ha_ips'] = ha_ips_list
#             paramsMap['ha_ips'] = ha_ips
            print 'ha ip list#####'
            
            #dispatch vip
            paramsMap['vip'] = {}
            vipParams = paramsMap['vip']
            vipParams['mysql_vip'] = ha_vip1
            vipParams['rabbit_vip'] = ha_vip1
            vipParams['keystone_vip'] = ha_vip1
            vipParams['glance_vip'] = ha_vip1
            vipParams['neutron_vip'] = ha_vip1
            vipParams['nova_vip'] = ha_vip1
            vipParams['dashboard_vip'] = ha_vip1
            vipParams['cinder_vip'] = ha_vip1
            vipParams['heat_vip'] = ha_vip1
            
            vipParams['ceilometer_vip'] = ha_vip2
            pass
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        admin_email = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'ADMIN_EMAIL')
        
        paramsMap['admin_email'] = admin_email
        
        import json
        jsonParams = json.dumps(paramsMap,indent=4)
        print 'jsonParams=%s-----------' % jsonParams
        print type(jsonParams)
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        openstackConfBaseDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'OPENSTACK_CONF_BASE_DIR')
        if not os.path.exists(openstackConfBaseDir) :
            ShellCmdExecutor.execCmd("mkdir %s" % openstackConfBaseDir)
            pass
        openstackParamsFilePath = os.path.join(openstackConfBaseDir, 'openstack_params.json')
        print 'openstackParamsFilePath=%s--' % openstackParamsFilePath
        FileUtil.writeContent(openstackParamsFilePath, jsonParams)
        
        print 'produce role list done#######'
        
        ###zgf add
        YAMLUtil.setHosts()
    pass

if __name__ == '__main__':
    ParamsProducer.produce()
    pass

