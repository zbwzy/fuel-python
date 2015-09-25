'''
Created on Sep 24, 2015

@author: zhangbai
'''
import os

from common.properties.Properties import Properties

class PropertiesUtility(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    @staticmethod
    def getContent(file_path):
        properties_file = open(file_path, 'r')
        lines = properties_file.readlines()
        content = ""
        for line in lines:
            content += line
        properties_file.close()
        return content
    
    @staticmethod
    def getValue(file_path, key):
        p = Properties()
        p.load(open(file_path))
        propertiesDict = p.getPropertyDict()
        
        value = ''
        if propertiesDict.has_key(key) :
            value = p[key]
            pass
        else :
            print "ERROR: No key %s in file %s" % (key, file_path)
            pass
        return value
    
    @staticmethod
    def getOpenstackConfBaseDir():
        curDir = os.path.dirname(__file__)
        print "curDir=%s" % curDir
        curFileName = os.path.basename(curDir)
        FUEL_PYTHON_PROJ_HOME_DIR = curDir.rstrip(curFileName).rstrip('/').rstrip("common")
        openstackEnvConfFilePath = os.path.join(FUEL_PYTHON_PROJ_HOME_DIR, 'conf', 'openstack_env.conf')
        openstackConfBaseDir = PropertiesUtility.getValue(openstackEnvConfFilePath, 'OPENSTACK_CONF_BASE_DIR')
        return openstackConfBaseDir
    
    @staticmethod
    def getOpenstackConfPropertiesFilePath():
        curDir = os.path.dirname(__file__)
        print "curDir=%s" % curDir
        curFileName = os.path.basename(curDir)
        FUEL_PYTHON_PROJ_HOME_DIR = curDir.rstrip(curFileName).rstrip('/').rstrip("common")
        openstackEnvConfPropertiesFilePath = os.path.join(FUEL_PYTHON_PROJ_HOME_DIR, 'conf', 'openstack_env.conf')
        return openstackEnvConfPropertiesFilePath
    
if __name__ == '__main__':
    print "test PropertiesUtil================="
    openstackConfBaseDir = PropertiesUtility.getOpenstackConfBaseDir()
    print 'openstackConfBaseDir=%s' % openstackConfBaseDir
    print os.path.exists(openstackConfBaseDir)
    print "test PropertiesUtil done#####"
    pass
    
    
    
    