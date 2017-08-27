'''
Created on May 12, 2017

@author: zhangbai
'''
import sys
import os
import time

#DEBUG
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
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class OpenFile(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
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
                  
                OpenFile.insertAfterLine('\[Service\]', 'Restart=always', filePath)
                pass
            else :
                OpenFile.insertAfterLine('\[Service\]', 'Restart=always', filePath)
                pass
              
            if 'LimitNOFILE' in fileContent :
                #del
                delCmd = 'sed -i -e \'/%s/d\' %s' % ('LimitNOFILE', filePath)
                ShellCmdExecutor.execCmd(delCmd)
                  
                OpenFile.insertAfterLine('\[Service\]', 'LimitNOFILE=409600', filePath)
                pass
            else :
                OpenFile.insertAfterLine('\[Service\]', 'LimitNOFILE=409600', filePath)
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
            if ('openstack-nova-metadata-api' not in fileName) and ('openstack-keystone' not in fileName) :
                ShellCmdExecutor.execCmd('systemctl restart %s' % fileName)
                pass
            pass
        
        file.close()
        return 1

    @staticmethod
    def insertAfterLine(curLineContent, insertLine, filePath):
        cmd = 'sed -i  \'/%s/a\%s\' %s' % (curLineContent, insertLine, filePath)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    #fileName should be xxxx.service,e.g. httpd.service
    @staticmethod
    def execModificationBy(dirPath, fileName):
        backupDir = '/home/backup_service/serviceFile'
        if not os.path.exists(backupDir) :
            os.system('mkdir -p %s' % backupDir)
            pass
        
        #backup
        ShellCmdExecutor.execCmd('cd %s; cp -r %s %s' %(dirPath, fileName, backupDir))
        
        #        
        if fileName.strip() == '' or fileName.strip() == None:
            return 0
            pass
        
        diffDir = '/home/backup_service/serviceRecord.txt'
        if os.path.exists(diffDir) :
            ShellCmdExecutor.execCmd("rm -rf %s" % diffDir)
            pass
        
        file = open(diffDir, 'a')
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
              
            OpenFile.insertAfterLine('\[Service\]', 'Restart=always', filePath)
            pass
        else :
            OpenFile.insertAfterLine('\[Service\]', 'Restart=always', filePath)
            pass
          
        if 'LimitNOFILE' in fileContent :
            #del
            delCmd = 'sed -i -e \'/%s/d\' %s' % ('LimitNOFILE', filePath)
            ShellCmdExecutor.execCmd(delCmd)
              
            OpenFile.insertAfterLine('\[Service\]', 'LimitNOFILE=409600', filePath)
            pass
        else :
            OpenFile.insertAfterLine('\[Service\]', 'LimitNOFILE=409600', filePath)
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
        if ('openstack-nova-metadata-api' not in fileName) and ('openstack-keystone' not in fileName) :
            ShellCmdExecutor.execCmd('systemctl restart %s' % fileName)
            pass
        
        file.close()
        return 1
    
    
    
if __name__ == '__main__':
    print 'hello  execModification==================='
    print 'start time: %s' % time.ctime()
    
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/initOpenFile'
    if not os.path.exists(INSTALL_TAG_FILE) :
        OpenFile.execModification('/usr/lib/systemd/system', 'openstack-')
        os.system('touch %s' % INSTALL_TAG_FILE)
        
    print 'done time: %s' % time.ctime()
    print 'done  execModification#####'
    pass
        