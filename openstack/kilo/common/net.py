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
        
        pass
    
    

if __name__ == '__main__':
    #Test
    val = 'bond0.999'
    
    print val.split('.')[0]
#     ifName = Network.getInterfaceNameByBridge('br-mgmt')
#     print 'interfanceName=%s--' % ifName
    pass



