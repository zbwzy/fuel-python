'''
Created on July 21, 2016

@author: zhangbai
'''

'''
usage:

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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

sys.path.append(PROJ_HOME_DIR)

from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.yaml.YAMLUtil import YAMLUtil

class Net(object):
    '''
    classdocs
    '''
    TIMEOUT = 600 #unit:second
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def getNetworkSchemeTransformations(): # return dict list
        dataMap = YAMLUtil.getMap(YAMLUtil.ASTUTE_YAML_FILE_PATH)
        networkSchemeTransformations = dataMap['network_scheme']['transformations']
        return networkSchemeTransformations
        pass
    
    @staticmethod
    def getInterfaceNameByBridge(bridge_name):
        networkSchemeTransformationsDictList = Net.getNetworkSchemeTransformations()
        
        ifName = ''
        for element in networkSchemeTransformationsDictList :
            if element.has_key('action') and element.has_key('bridge') :
                if element['bridge'] == bridge_name :
                    ifName = element['name']
                    pass
                pass
            pass
        
        if ifName == '' :
            raise Exception("Failed to get interface name by bridge [%s]." % bridge_name)
        
        return ifName
    
    @staticmethod
    def removePhyNet(bridge_name):
        networkSchemeTransformationsDictList = Net.getNetworkSchemeTransformations()
        
        ifName = ''
        for element in networkSchemeTransformationsDictList :
            if element.has_key('action') and element.has_key('bridge') :
                if element['bridge'] == bridge_name :
                    ifName = element['name']
                    pass
                pass
            pass
        
        if ifName == '' :
            raise Exception("Failed to get interface name by bridge [%s]." % bridge_name)
        
        return ifName
        
        pass
    
    @staticmethod
    def implement_lldp():
        print 'implement_lldp========'
        role = 'neutron-agent'
        key = 'neutron_network_mode'
        network_mode = YAMLUtil.getValue(role, key)
        
#         if network_mode == 'vlan' :
        ShellCmdExecutor.execCmd('yum install lldpad -y')
        ShellCmdExecutor.execCmd('lldpad -d')
        
        mgmt_interface_names = YAMLUtil.getInterfacesByBridge('br-mgmt')
        for interface_name in mgmt_interface_names:
            
            cmd1 = 'lldptool set-lldp -i {interface_name} adminStatus=rxtx'.format(interface_name=interface_name)
            cmd2 = 'lldptool -T -i {interface_name} -V  sysName enableTx=yes'.format(interface_name=interface_name)
            cmd3 = 'lldptool -T -i {interface_name} -V  portDesc enableTx=yes'.format(interface_name=interface_name)
            cmd4 = 'lldptool -T -i {interface_name} -V  sysDesc enableTx=yes'.format(interface_name=interface_name)
            cmd5 = 'lldptool -T -i {interface_name} -V sysCap enableTx=yes'.format(interface_name=interface_name)
            cmd6 = 'lldptool -T -i {interface_name} -V mngAddr enableTx=yes'.format(interface_name=interface_name)
            ShellCmdExecutor.execCmd(cmd1)
            ShellCmdExecutor.execCmd(cmd2)
            ShellCmdExecutor.execCmd(cmd3)
            ShellCmdExecutor.execCmd(cmd4)
            ShellCmdExecutor.execCmd(cmd5)
            ShellCmdExecutor.execCmd(cmd6)
        print 'implement_lldp#########'
        pass
    
    @staticmethod
    def rmBusinessNet():
        print 'rm business net========'
        role = 'neutron-agent'
        key = 'neutron_network_mode'
        network_mode = YAMLUtil.getValue(role, key)
        
#         if network_mode == 'vlan' :
        ShellCmdExecutor.execCmd('ifconfig br-data down')
        bondv = Net.getInterfaceNameByBridge('br-data')
        
        ShellCmdExecutor.execCmd('brctl delif br-data {bondv}'.format(bondv=bondv))
        ShellCmdExecutor.execCmd('brctl delbr br-data')
        
        ShellCmdExecutor.execCmd('rm -rf /etc/sysconfig/network-scripts/ifcfg-br-data')
        
        rm_bondv_cmd = 'rm -rf /etc/sysconfig/network-scripts/ifcfg-{bondv}'.format(bondv=bondv)
        ShellCmdExecutor.execCmd(rm_bondv_cmd)
        
        ShellCmdExecutor.execCmd('systemctl restart network')
        
        #####
        ShellCmdExecutor.execCmd('ovs-vsctl add-br br-ex')
        bond = bondv.split('.')[0]
        add_port_cmd = 'ovs-vsctl add-port br-ex {bond}'.format(bond=bond)
        ShellCmdExecutor.execCmd(add_port_cmd)
        print 'rm business net#########'
        pass
    
    
    #for ICBC
    @staticmethod
    def patch():
        if os.path.exists('/usr/lib/python2.7/site-packages/neutron/plugins/ml2/rpc.py') :
            backup_cmd = 'mv /usr/lib/python2.7/site-packages/neutron/plugins/ml2/rpc.py  /usr/lib/python2.7/site-packages/neutron/plugins/ml2/rpc.py.huawei'
            ShellCmdExecutor.execCmd(backup_cmd)
            pass
        
        rpc_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'neutron-server', 'rpc.py')
        ShellCmdExecutor.execCmd('cp -r %s /usr/lib/python2.7/site-packages/neutron/plugins/ml2/' % rpc_template_file_path)
        
        ShellCmdExecutor.execCmd('chown -R neutron:neutron /etc/neutron/neutron_lbaas.conf')
        pass
    
    

if __name__ == '__main__':
    #Test
    val = 'bond0.999'
    
    print val.split('.')[0]
#     ifName = Network.getInterfaceNameByBridge('br-mgmt')
#     print 'interfanceName=%s--' % ifName
    pass



