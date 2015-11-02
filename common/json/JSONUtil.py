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
    
    #only for openstack params
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
            pass
        
        #refactor: if key='admin_email', value = 'admin@cmss.chinamobile.com'
        if key == 'admin_email' :
            value = 'admin@cmss.chinamobile.com'
            pass
            
        return value
    
    @staticmethod
    def getValueInJsonFile(key, json_file_path): 
        if not os.path.exists(json_file_path) :
            print 'ERROR:the json file %s NOT exist!' % json_file_path
            return ''
            
        jsonContent = JSONUtility.getContent(json_file_path)
        
        try :
            jsonDict = json.loads(jsonContent)
        except Exception, e :
            print 'Exception happens when do json loads file %s' % json_file_path
            print 'Exception:%s' % str(e)
        
        value = ''    
        if jsonDict.has_key(key):
            value = jsonDict[key]
            pass
        else :
            print 'ERROR:no key % in openstack_params.json.' % key
            
        return value
    
        
        
        
    