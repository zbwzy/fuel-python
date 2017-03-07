'''
Created on Jan 4, 2016

@author: zhangbai
'''
import os


class Role(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isRabbitMQRole():
        if os.path.exists('/opt/is_rabbitmq_role') :
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isNeutronServerRole():
        if os.path.exists('/opt/is_neutron_server_role') :
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isNeutronAgentRole(): #network node
        if os.path.exists('/opt/is_neutron_agent_role'):
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isNovaComputeRole():
        if os.path.exists('/opt/is_nova_compute_role'):
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isNovaComputeRole4Prerequisites():
        from common.yaml.YAMLUtil import YAMLUtil
        mgmtIPList = YAMLUtil.getRoleManagementIPList('nova-compute')
        localMgmtIP = YAMLUtil.getManagementIP()
        if localMgmtIP in mgmtIPList :
            return True
        else :
            return False
        pass
    
    @staticmethod
    def isGlanceRole():
        if os.path.exists('/opt/is_glance_role'):
            return True
        else :
            return False
        pass
    
    
    
if __name__ == '__main__':
    pass