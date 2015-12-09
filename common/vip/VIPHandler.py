'''
Created on Nov 30, 2015

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

import yaml

class VIPHandler(object):
    '''
    classdocs
    '''
    ASTUTE_YAML_FILE_PATH = '/etc/astute.yaml'
    #mongodb, nova-compute, cinder-storage, neutron-agent : 
    #do not use VIP
    OPENSTACK_ROLES = ['mysql', 'rabbitmq', 'keystone', 'glance', 'nova-api', 'neutron-server', 'cinder-api', 'horizon', 'ceilometer', 'heat']
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def handle():
        pass
    
    @staticmethod
    def isMaster(role):
        role_ips_key = ''
        if role == 'nova-api' :
            role_ips_key = 'nova_ips'
            pass
        
        elif role == 'neutron-server' :
            role_ips_key = 'neutron_ips'
            pass
        
        elif role == 'cinder-api' :
            role_ips_key = 'cinder_ips'
            pass
        
        elif role == 'horizon' :
            role_ips_key = 'dashboard_ips'
            pass
        
        else :
            role_ips_key = '{rolename}_ips'.format(rolename=role).replace('-', '_')
            pass
        
        role_ips = JSONUtility.getValue(role_ips_key)
        
        role_ip_list = role_ips.split(',')
        
        output, exitcode = ShellCmdExecutor.execCmd("cat /opt/localip")
        localIP = output.strip()
        index = role_ip_list.index(localIP)
        print 'VIPHandler.isMaster:index=%s-----------' % index
        
        if index == 0 :
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isExistVIP(vip, interface):
        cmd = 'ip addr show dev {interface} | grep {vip}'.format(interface=interface, vip=vip)
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == None or output == '':
            print 'Do no exist vip %s on interface %s.' % (vip, interface)
            return False
        
        if debug == True :
            output = '''
            xxxx
            inet 192.168.11.100/32 scope global eth0
            xxxx
            '''
            pass
        
        newString = vip + '/'
        if newString in output :
            print 'exist vip %s on interface %s.' % (vip, interface)
            return True
        else :
            print 'Do no exist vip %s on interface %s.' % (vip, interface)
            return False
        pass
    
    #return value: 192.168.11.100/32
    @staticmethod
    def getVIPFormatString(vip, interface):
        vipFormatString = ''
        if VIPHandler.isExistVIP(vip, interface) :
            print 'getVIPFormatString====exist vip %s on interface %s' % (vip, interface) 
            cmd = 'ip addr show dev {interface} | grep {vip}'.format(interface=interface, vip=vip)
            output, exitcode = ShellCmdExecutor.execCmd(cmd)
            vipFormatString = output.strip()
            if debug == True :
                fakeVIPFormatString = 'inet 192.168.11.100/32 scope global eth0'
                vipFormatString = fakeVIPFormatString
                pass
            
            result = vipFormatString.split(' ')[1]
            pass
        else :
            #construct vip format string
            print 'getVIPFormatString====do not exist vip %s on interface %s, to construct vip format string' % (vip, interface) 
            vipFormatString = '{vip}/32'.format(vip=vip)
            print 'vipFormatString=%s--' % vipFormatString
            result = vipFormatString
            pass
        
        return result
    
    @staticmethod
    def addVIP(vip, interface):
        result = VIPHandler.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not VIPHandler.isExistVIP(vip, interface) :
            print 'NOT exist vip %s on interface %s.' % (vip, interface)
            addVIPCmd = 'ip addr add {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'addVIPCmd=%s--' % addVIPCmd
            ShellCmdExecutor.execCmd(addVIPCmd)
            pass
        else :
            print 'The VIP %s already exists on interface %s.' % (vip, interface)
            pass
        pass
    
    @staticmethod
    def deleteVIP(vip, interface):
        result = VIPHandler.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if VIPHandler.isExistVIP(vip, interface) :
            deleteVIPCmd = 'ip addr delete {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'deleteVIPCmd=%s--' % deleteVIPCmd
            ShellCmdExecutor.execCmd(deleteVIPCmd)
            pass
        else :
            print 'The VIP %s does not exist on interface %s.' % (vip, interface)
            pass
        pass
    
    @staticmethod
    def deleteRoleVIP(role):
        role_vip_key = ''
        role_vip_interface_key = ''
        if role == 'nova-api' :
            role_vip_key = 'nova_vip'
            role_vip_interface_key = 'nova_vip_interface'
            pass
        
        elif role == 'neutron-server' :
            role_vip_key = 'neutron_vip'
            role_vip_interface_key = 'neutron_vip_interface'
            pass
        
        elif role == 'cinder-api' :
            role_vip_key = 'cinder_vip'
            role_vip_interface_key = 'cinder_vip_interface'
            pass
        
        elif role == 'horizon' :
            role_vip_key = 'dashboard_vip'
            role_vip_interface_key = 'dashboard_vip_interface'
            pass
        
        elif role == 'rabbitmq' :
            role_vip_key = 'rabbit_vip'
            role_vip_interface_key = 'rabbit_vip_interface'
            pass
        
        else :
            role_vip_key = '{rolename}_vip'.format(rolename=role)
            role_vip_interface_key = '{rolename}_vip_interface'.format(rolename=role)
            pass
        
        role_vip = JSONUtility.getValue(role_vip_key)
        role_vip_interface = JSONUtility.getValue(role_vip_interface_key)
        
        VIPHandler.deleteVIP(role_vip, role_vip_interface)
        pass
    

if __name__ == "__main__":
    print 'Keep one vip for each role: delete non-master role vip========================'
    
    for role in VIPHandler.OPENSTACK_ROLES :
        is_role_file_path = '/opt/is_{rolename}_role'.format(rolename=role).replace('-', '_')
        #judge role
        if os.path.exists(is_role_file_path) :
            #judge master
            if not VIPHandler.isMaster(role) :
                #delete VIP
                VIPHandler.deleteRoleVIP(role)
                
                #restart keepalived
                ShellCmdExecutor.execCmd('service keepalived restart')
                pass
            else :
                xx = 'This is %s master.Do not need to delete VIP.' % role
                print xx
                file_path = '/tmp/{rolename}_vip_handle.log'.format(rolename=role)
                FileUtil.writeContent(file_path, xx)
            pass
        pass
    
    print 'delete role vip done##########'
    pass

    
    
        
        
    