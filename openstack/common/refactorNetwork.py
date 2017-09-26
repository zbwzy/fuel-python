'''
Created on Aug 27, 2017

@author: zhangbai
'''

import sys
import os
import time
import subprocess

reload(sys)
sys.setdefaultencoding('utf8')


def execute_cmd(cmd, customer_errmsg):
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    res.wait()
    readmsg = res.stdout.read().strip()
    errormsg = res.stderr.read()

    if errormsg:
        print(errormsg)
        print(customer_errmsg)
        sys.exit()
    else:
        return readmsg
    
    
class FileUtil(object):
    '''
    classdocs
    '''
    OPENSTACK_INSTALL_LOG_TEMP_DIR ="/var/log/openstack_kilo"

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



class RefactorNetwork(object):
    '''
    classdocs
    '''
    NETWORK_CONF_DIR = '/etc/sysconfig/network-scripts/'
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def getIfcfgFileNameList():
        output = execute_cmd('ls -lt %s |grep ifcfg- | awk \'{print $9}\'' % RefactorNetwork.NETWORK_CONF_DIR, 'get ifcfg file name failure')
        print 'output=%s--' % output.strip()
        file_name_list = []
        
        if output == None or output == "" :
            return file_name_list
        
        file_name_list = output.strip().split('\n')
        return file_name_list
    
    @staticmethod
    def removeEthtoolOpts():
        file_name_list = RefactorNetwork.getIfcfgFileNameList()
        if len(file_name_list) > 0 :
            for ifcfg_file_name in file_name_list :
                abs_ifcfg_file_path = os.path.join(RefactorNetwork.NETWORK_CONF_DIR, ifcfg_file_name)
                config_file = file(abs_ifcfg_file_path, 'r')
                file_content = ""
                file_lines = config_file.readlines();
                for line in file_lines :
                    if 'ETHTOOL_OPTS=' not in line :
                        file_content = file_content + line
                        pass
                    pass
                
                config_file.close()
                
                rm_file_cmd = 'rm -rf %s' % abs_ifcfg_file_path
                execute_cmd(rm_file_cmd, 'rm %s failure' % abs_ifcfg_file_path)
                
                FileUtil.writeContent(abs_ifcfg_file_path, file_content)
                pass
            pass
        pass
    
    
    
if __name__ == '__main__' :
    RefactorNetwork.removeEthtoolOpts()
    execute_cmd("systemctl restart network","restart network failure")
    pass


