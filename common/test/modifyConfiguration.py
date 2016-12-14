'''
Created on Mar 13, 2016

@author: zhangbai
'''
'''
Created on Dec 15, 2015

@author: zhangbai
'''
import sys
import os
import time

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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.common.role import Role

def foo(val1, val2):
    print 'value1=%s' % val1
    print 'value2=%s' % val2
    return val1,val2
    pass

def getPackage():
    f = open('1.txt','r')  
    result = list()  
    for line in open('1.txt'):  
        line = f.readline()  
        rpmPackageArray = line.strip().split(':')
        yumCmd = rpmPackageArray[1].strip()
        print 'yumCmd=%s--------' % yumCmd
        result.append(yumCmd)
        pass
    
    print 'result=\n%s\n--' %  result  
    f.close()                  
    open('result-readline.txt', 'w').write('%s' % '\n'.join(result))
    pass

def getPackage2():
    f = open('2.txt','r')  
    result = list()  
    for line in open('2.txt'):  
        line = f.readline()  
        rpmPackageArray = line.strip().split('=')
        yumCmd = rpmPackageArray[1].strip()
        print 'yumCmd=%s--------' % yumCmd
        result.append(yumCmd)
        pass
    
    print 'result=\n%s\n--' %  result  
    f.close()                  
    open('result-readline.txt', 'w').write('%s' % '\n'.join(result))
    pass

def getPackage3():
    f = open('3.txt','r')  
    result = list()  
    for line in open('3.txt'):  
        line = f.readline()  
        rpmPackageArray = line.strip().split('install')
        yumCmd = rpmPackageArray[1].strip()
        print 'yumCmd=%s--------' % yumCmd
        rpmList = yumCmd.split(' ')
        result.append(yumCmd)
        pass
    
    print 'result=\n%s\n--' %  result  
    f.close()                  
    open('result-readline.txt', 'w').write('%s' % '\n'.join(result))
    pass


def getPackage4():
    f = open('4.txt','r')  
    result = list()  
    for line in open('4.txt'):  
        line = f.readline()  
        rpmPackageArray = line.strip().split(' ')
        for e in rpmPackageArray :
            result.append('yum search %s >> /tmp/yum_search.log' % e)
            pass
        pass
    
    print 'result=\n%s\n--' %  result  
    f.close()                  
    open('result-readline.txt', 'w').write('%s' % '\n'.join(result))
    pass


def getAllPackage():
    f = open('yum.txt','r')  
    result = list()  
    for line in open('yum.txt'):  
        line = f.readline()  
        print 'line==%s--' % line
        rpmPackageArray = line.strip().split(' ')
        for e in rpmPackageArray :
            result.append('yum search %s >> /tmp/yum_search.log' % e)  
            pass
        pass
    
    print 'result=\n%s\n--' %  result  
    f.close()                  
    open('result-readline.txt', 'w').write('%s' % '\n'.join(result)) 
    pass


def execModification(dirPath, fileNameKey):
    backupDir = '/home/backup_service/serviceFile'
    if not os.path.exists(backupDir) :
        os.system('mkdir -p %s' % backupDir)
        pass
    
    #backup
    ShellCmdExecutor.execCmd('cd %s; cp -r %s* %s' %(dirPath, fileNameKey, backupDir))
    
    #
    output, exitcode = ShellCmdExecutor.execCmd('cd %s; ls -lt | grep %s | awk \'{print $9}\'' % (dirPath, fileNameKey))
    print 'fileName=\n%s\n--' % output.strip()
    
    if output.strip() == '' or output.strip() == None:
        return 0
        pass
    
    fileNameList = output.strip().split('\n')
    print len(fileNameList)
    
    diffDir = '/home/backup_service/serviceRecord.txt'
    if os.path.exists(diffDir) :
        ShellCmdExecutor.execCmd("rm -rf %s" % diffDir)
        pass
    
    file = open(diffDir, 'a')
    for fileName in fileNameList :
    #////////////////  modify service configuration file: add limitNOFILE=409600, Restart=always
        filePath = os.path.join(dirPath, fileName)
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % filePath)
        fileContent = output.strip()
          
        limitNOFILECount, exitcode = ShellCmdExecutor.execCmd('cat %s | grep LimitNOFILE | wc -l' % filePath)
        limitNOFILECount = limitNOFILECount.strip()
          
        restartCount, exitcode = ShellCmdExecutor.execCmd('cat %s | grep Restart | wc -l' % filePath)
        restartCount = restartCount.strip()
          
        file.write('%s\n\'%s\'->[%s].  \'%s\'->[%s].\n------------------------------------\n' % (fileName,'LimitNOFILE', limitNOFILECount, 'Restart', restartCount))
          
        if 'Restart' in fileContent and 'always' in fileContent :
            #del
            delCmd = 'sed -i -e \'/%s/d\' %s' % ('Restart', filePath)
            ShellCmdExecutor.execCmd(delCmd)
              
            insertAfterLine('\[Service\]', 'Restart=always', filePath)
            pass
        else :
            insertAfterLine('\[Service\]', 'Restart=always', filePath)
            pass
          
        if 'LimitNOFILE' in fileContent :
            #del
            delCmd = 'sed -i -e \'/%s/d\' %s' % ('LimitNOFILE', filePath)
            ShellCmdExecutor.execCmd(delCmd)
              
            insertAfterLine('\[Service\]', 'LimitNOFILE=409600', filePath)
            pass
        else :
            insertAfterLine('\[Service\]', 'LimitNOFILE=409600', filePath)
            pass
          
          
        #After
        limitNOFILECount, exitcode = ShellCmdExecutor.execCmd('cat %s | grep LimitNOFILE | wc -l' % filePath)
        limitNOFILECount = limitNOFILECount.strip()
          
        restartCount, exitcode = ShellCmdExecutor.execCmd('cat %s | grep Restart | wc -l' % filePath)
        restartCount = restartCount.strip()
          
        file.write('After modification: %s\n\'%s\'->[%s].  \'%s\'->[%s].\n------------------------------------\n' % (fileName,'LimitNOFILE', limitNOFILECount, 'Restart', restartCount))
        
        ###
        ShellCmdExecutor.execCmd('systemctl daemon-reload')
        #Restart service
        ShellCmdExecutor.execCmd('systemctl restart %s' % fileName)
        pass
    
    file.close()
    
    return 1
    pass


def insertAfterLine(curLineContent, insertLine, filePath):
    cmd = 'sed -i  \'/%s/a\%s\' %s' % (curLineContent, insertLine, filePath)
    ShellCmdExecutor.execCmd(cmd)
    pass

def getAllFilePath():
    pass


if __name__ == '__main__':
    print 'hello modfiy configuration test============'
    print 'start time: %s' % time.ctime()
    
    #when execute script,exec: python <this file absolute path>
    ###############################
    result = execModification('/usr/lib/systemd/system', 'openstack-ceilometer')
    print 'result=%s-------------' % result
    
    exit()
    
    
    

    