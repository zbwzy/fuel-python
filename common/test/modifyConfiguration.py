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



import os
import subprocess
import datetime
import commands


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

class ShellCmdExecutor(object):
    '''
    classdocs
    '''
    DEFAULT_TIMEOUT = 600
    OPENSTACK_INSTALL_LOG_TEMP_DIR = "/tmp/openstack"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def debugEnv(scriptfile=None, env=None) :
        if scriptfile == None or env == None :
            return
    
        outfilepath = scriptfile + ".env"
        os.system("rm -f %s" % outfilepath)

        outfile = open(outfilepath, 'w')
    
        for k in env :
            e = "export %s=\"%s\"\n" % (k, env[k])
            print(e)
            outfile.write(e)

        outfile.close()
    
    @staticmethod
    def execCmd(cmd, ifPrint=None, exitcodeSwitch=None, timeout=None, env=None):
        if timeout == None :
            timeout = ShellCmdExecutor.DEFAULT_TIMEOUT
            pass
        
        if exitcodeSwitch == None:
            exitcodeSwitch = False
            pass
        
        if not cmd:
            return
        #write cmd to a temp file in order to support multiple shell commands execution
        msg = 'Executing cmd with timeout(timeout=%s s): %s' % (timeout, cmd)
        print(msg)
        
        strTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        strUUID = commands.getoutput('uuidgen')
        bashFileName = "bashfile-%s-%s.sh" % (strTime, strUUID)
        if not os.path.exists(ShellCmdExecutor.OPENSTACK_INSTALL_LOG_TEMP_DIR) :
            os.system("mkdir -p %s" % ShellCmdExecutor.OPENSTACK_INSTALL_LOG_TEMP_DIR)
            pass
        bashFilePath = "%s/%s" % (ShellCmdExecutor.OPENSTACK_INSTALL_LOG_TEMP_DIR, bashFileName)
        FileUtil.writeContent(bashFilePath, cmd)
        bash_cmd = "bash %s" % bashFilePath
        output = None
        exitcode = -1
        
        try :
            output, exitcode = ShellCmdExecutor.execCmdWithKillTimeout(bash_cmd, ifPrint=ifPrint, kill_timeout=timeout, env=env)
            if exitcodeSwitch :
                if exitcode != 0 :
                    print("otuput=%s" % output)
                    print("exitcode=%s" % exitcode)
                    pass
                else :
                    print("otuput=%s" % output)
                    print("exitcode=%s" % exitcode)
                    pass
                pass
            pass
        except Exception, e:
            print("Write content exception:" + str(e))
        finally:
            if output != None and "[ERROR] [TIMEOUT]" in output :
                print("TIMEOUT when execute cmd:%s" % cmd)
                pass
            os.system("rm -rf %s" % bashFilePath)
#         print(cmd)
        return (output, exitcode)
    
    #The type of env should be dict.
    @staticmethod
    def execCmdWithoutKillTimeout(cmd, ifPrint=None, env=None):
        if not cmd:
            return
        
        print('Executing cmd without timeout : %s' % cmd)
        output = None
        error = None
        outputFile = None
        outputFilePath = ""
        try :
            strTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            strUUID = commands.getoutput('uuidgen')
            outputFileName = "output%s.%s.log" % (strTime, strUUID)
            if not os.path.exists(ShellCmdExecutor.OPENSTACK_INSTALL_LOG_TEMP_DIR) :
                os.system("mkdir -p %s" % ShellCmdExecutor.OPENSTACK_INSTALL_LOG_TEMP_DIR)
                pass
            
            outputFilePath = "%s/%s" % (ShellCmdExecutor.OPENSTACK_INSTALL_LOG_TEMP_DIR, outputFileName)
            print("OutputFileName=%s" % outputFilePath)
            outputFile=open(outputFilePath, 'w')
            
            if env != None :
                try:
                    import inspect
                    import json
                    stack = inspect.stack()
                    the_class = stack[2][0].f_locals["self"].__class__.__name__
                    if not os.path.exists("/var/log/autoops_env.json"):
                        record_env = {the_class: env}
                        content = json.dumps(record_env, sort_keys=True, indent=4)
                    else:
                        content_data = json.load(file("/var/log/autoops_env.json"))
                        content_data[the_class] = env
                        content = json.dumps(content_data, sort_keys=True, indent=4)
                    FileUtil.writeContent("/var/log/autoops_env.json", content)
                except Exception as ex:
                    print("Save parsed Env params Failed")
                    print(ex)
                env = dict(os.environ.items() + env.items())
                pass
            p = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=outputFile, stderr=subprocess.PIPE, env=env)
            output, error = p.communicate()
            
            output = FileUtil.readContent(outputFilePath)
            
            if ifPrint :
                print("cmd output=%s---" % output)
            elif not ifPrint or ifPrint == None :
                pass
            
            if error!=None and error!="" :
                print("cmd error=%s---" % error)
                pass
            
            if error!=None and error!="" and cmd.find(".sh") > -1:
                error = "SOE: " + str(error)
        except Exception, e :
            print(e)
        finally:
            if outputFile!=None:
                outputFile.close()
#            os.system("rm -f %s" % outputFilePath)
            pass
        
        return output,error
    
    #The type of env should be dict.
    @staticmethod
    def execCmdWithKillTimeout(cmd, ifPrint=None, kill_timeout=600, env=None):
        if not cmd:
            return
        
        output = None
        outputFile = None
        exitcode = -1
        outputFilePath = ""
        content = ""
        try :
            if kill_timeout == None :
                kill_timeout = ShellCmdExecutor.DEFAULT_TIMEOUT
                pass
            strTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            strUUID = commands.getoutput('uuidgen')
            outputFileName = "output%s.%s.log" % (strTime, strUUID)
            
            ######################################
            cmd = cmd.strip()
            if cmd.startswith("bash") :
                scriptPath = cmd.strip().lstrip("bash").strip()
                content = FileUtil.readContent(scriptPath)
                #get script name
                content = content.strip()
                if content.startswith("bash") or content.startswith("sh") or content.startswith("python") or content.startswith("ruby"):
                    strCmd = content.strip()
                    elements = strCmd.split(" ")
                    scriptName = elements[1].split("/")[-1]
                    outputFileName = "%s-%s-%s.log" % (scriptName, strTime, strUUID)
                    pass
                elif content.startswith("./"):
                    pass
                pass
            ######################################
            outputDir = "/var/log/autoopsscriptslog"
            if not os.path.exists(outputDir) :
                os.system("mkdir -p %s" % outputDir)
                pass
            
            outputFilePath = "%s/%s" % (outputDir, outputFileName)
            print("OutputFileName=%s" % outputFilePath)
            print(content)
            outputFile=open(outputFilePath, 'w')
            
            current_dir = os.path.dirname(__file__)
            print "current_dir=%s" % current_dir
            timeout3ScriptPath= "%s/timeout3.sh" % current_dir
            timeoutCmd = "bash %s -t %s -i 1 -d 1 %s" % (timeout3ScriptPath, kill_timeout, cmd)
            #print("you can check the cmd %s logs @ %s if the cmd execution time is long" % (cmd, outputFilePath))
            if env != None :
                try:
                    import inspect
                    import json
                    stack = inspect.stack()
                    the_class = stack[2][0].f_locals["self"].__class__.__name__
                    if not os.path.exists("/var/log/autoops_env.json"):
                        record_env = {the_class: env}
                        content = json.dumps(record_env, sort_keys=True, indent=4)
                    else:
                        content_data = json.load(file("/var/log/autoops_env.json"))
                        content_data[the_class] = env
                        content = json.dumps(content_data, sort_keys=True, indent=4)
                    FileUtil.writeContent("/var/log/autoops_env.json", content)
                except Exception as ex:
                    print("Save parsed Env params Failed")
                    print(ex)

                env = dict(os.environ.items() + env.items())
                pass
            p = subprocess.Popen(timeoutCmd, shell=True, close_fds=True, stdout=outputFile, stderr=subprocess.STDOUT, env=env)
            #ToDo: start a thread to print the logs to log file
            output, error = p.communicate()
            exitcode = p.returncode
            
            output = FileUtil.readContent(outputFilePath)
            
            if ifPrint :
                print("cmd output=%s---" % output)
                print("The returncode is : %s" % exitcode)
                pass
            elif not ifPrint or ifPrint == None :
                pass
        except Exception, e :
            print(e)
        finally:
            if outputFile!=None:
                outputFile.close()
            
            if(exitcode==0) :
                stdoutFilePath = outputFilePath.rstrip(".log") + "-stdout.log"
                stderrFilePath = outputFilePath.rstrip(".log") + "-stderr.log"
                os.system("mv %s %s" % (outputFilePath, stdoutFilePath))
                os.system("touch %s" % stderrFilePath)
                #print("exitcode is 0")
#                os.system("rm -f %s" % outputFilePath)
                print("you can check the cmd output logs @ %s.The exitcode=%s." % (stdoutFilePath, exitcode))
                pass
            else :
                stdoutFilePath = outputFilePath.rstrip(".log") + "-stdout.log"
                stderrFilePath = outputFilePath.rstrip(".log") + "-stderr.log"
                os.system("mv %s %s" % (outputFilePath, stderrFilePath))
                os.system("touch %s" % stdoutFilePath)
                
                print("you can check the cmd output logs @ %s.The exitcode=%s." % (stderrFilePath, exitcode))
                pass
            pass
        
        return (output, exitcode)


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
        if 'openstack-nova-metadata-api' not in fileName :
            ShellCmdExecutor.execCmd('systemctl restart %s' % fileName)
            pass
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
    result = ''
    host_name = 'cmss-node53.domain.tld'
    if '.domain.tld' in host_name:
        print 'host_name=%s---------' % host_name.rstrip('.domain.tld')
        pass
    host_name = 'cmss-node53.domain'
    if '.domain.tld' in host_name:
        print 'host_name=%s---------' % host_name.rstrip('.domain.tld')
        pass
    else :
        print host_name
#     result = execModification('/usr/lib/systemd/system', 'openstack-')
    print 'result=%s-------------' % result
    
    exit()
    
    
    

    