'''
Created on Sep 9, 2015

@author: zhangbai
'''  
import os
import subprocess
import datetime
import commands

from common.file.FileUtil import FileUtil

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
#1.Implement execute cmd with timeout, it will return the output including both stdout and stderr.





