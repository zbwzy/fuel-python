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
    def isGlanceRole():
        if os.path.exists('/opt/is_glance_role'):
            return True
        else :
            return False
        pass
    
    
    
if __name__ == '__main__':
    pass