'''
Created on Sep 24, 2015

@author: zhangbai
'''
import os

class FileUtil(object):
    '''
    classdocs
    '''
    OPENSTACK_INSTALL_LOG_TEMP_DIR ="/var/log/openstack_icehouse"

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def readContent(file_path):
        config_file = file(file_path, 'r')
        file_content = ""
        file_lines = config_file.readlines();
        for line in file_lines :
            file_content = file_content + line
        config_file.close()
        return file_content
    
    @staticmethod
    def writeContent(file_path, content):
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path) :
            os.system("mkdir -p %s" % dir_path)
            pass
        
        if os.path.exists(file_path) :
            os.system('rm -rf %s' % file_path)
            pass
        else :
            os.system('touch %s' % file_path)
            pass
        
        config_file = file(file_path, 'w')
        config_file.write(content)
        config_file.close()
    
    @staticmethod
    def replaceFileContent(filePath, replaceToken, replaceValue):
        print("Replace %s to %s in conf file %s" % (replaceToken, replaceValue, filePath))
        content = FileUtil.readContent(filePath)
        content = content.replace(replaceToken, replaceValue)
        FileUtil.writeContent(filePath, content)
        pass
    
    @staticmethod
    def replaceByRegularExpression(filePath, toBeReplacedRegularEx, replaceValue):
        print "Replace the string [%s] with [%s] in file %s." % (toBeReplacedRegularEx, replaceValue, filePath)
        sedCmd = "sed -i 's/%s/%s/g' %s" % (toBeReplacedRegularEx, replaceValue, filePath)
        os.system(sedCmd)
        pass