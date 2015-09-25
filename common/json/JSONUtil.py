'''
Created on Sep 24, 2015

@author: zhangbai
'''
import os
import json
from common.properties.PropertiesUtil import PropertiesUtility

class JSONUtility(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    @staticmethod
    def getContent(file_path):
        json_file = open(file_path, 'r')
        lines = json_file.readlines()
        jsonContent = ""
        for line in lines:
            jsonContent += line
        json_file.close()
        return jsonContent
    
    @staticmethod
    def getValue(key):
        openstackConfFileDir = PropertiesUtility.getOpenstackConfBaseDir()
        openstack_params_file_path = os.path.join(openstackConfFileDir, "openstack_params.json")
        jsonContent = JSONUtility.getContent(openstack_params_file_path)
        
        try :
            jsonDict = json.loads(jsonContent)
        except Exception, e :
            print 'Exception happens when do json loads file %s' % openstack_params_file_path
            print 'Exception:%s' % str(e)
        
        value = ''    
        if jsonDict.has_key(key):
            value = jsonDict[key]
            pass
        else :
            print 'ERROR:no key % in openstack_params.json.' % key
            
        return value
    
        
        
        
    