'''
Created on Nov 5, 2015

@author: zhangbai
'''
import os
import sys
import json
import time

debug = False 

#This program is used to parse ip_map_role.json on nailgun docker
if debug == False :
#     from nailgun.common.ssh import Client as SSHClient
    from nailgun.logger import logger
    pass
else :
    pass


class Params(object):
    
    OPENSTACK_ROLES = ['keystone']
#     OPENSTACK_ROLES = ['keystone', 'glance', 'cinder-api', 'cinder-storage', 'heat', 
#                        'horizon', 'nova-api', 'nova-compute','neutron-server', 'neutron', 
#                         'mongodb', 'ceilometer']
    
    CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/{cluster_id}/ip_map_role.json'
    CLUSTER_ROLE_MAP_JSON_FILE_PATH_TEMPLATE = '/opt/role_ip_map_{cluster_id}.json'
    
    def __init__(self):
        pass
    pass


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
        os.system("mkdir -p %s" % dir_path)
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
    pass

'''
Created on Sep 9, 2015

@author: zhangbai
'''  
import subprocess
import datetime
import commands


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



def example():
    from nailgun.common.ssh import Client as SSHClient
    
    ip = '10.20.0.151'
    ssh_user = 'root'
    ssh_password = 'r00tme'
    key_filename = '/root/.ssh/id_rsa'
    timeout = 1000
    ssh_client = SSHClient(ip, ssh_user, ssh_password, timeout, key_filename)
    
    cmd = 'echo `date` >> /tmp/hello.txt'
    result = ssh_client.exec_command(cmd)
    
    cmd = 'service openstack-glance-api restart'
    result = ssh_client.exec_command(cmd)
    print 'start glance-api=%s--' % result
    pass

def execRemoteCmd(ip, cmd, timeout=600):
    ssh_user = 'root'
    ssh_password = 'r00tme'
    key_filename = '/root/.ssh/id_rsa'
    if timeout == None :
        timeout = 600
        pass
    
    ssh_client = SSHClient(ip, ssh_user, ssh_password, timeout, key_filename)
    
    result = ssh_client.exec_command(cmd)
    logger.info('exec remote cmd:%s to ip:%s, the result:%s.' % (cmd, ip, result))
    return result
    pass

def getActiveRoleIPMap(cluster_id):
    if debug :
        print 'cluster_id=%s' % cluster_id
        clusterIPRoleMapFilePath = 'iprole.json'
        pass
    else :
        clusterIPRoleMapFilePath = Params.CLUSTER_IP_ROLE_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
        print 'clusterIPRoleMapFilePath=%s' % clusterIPRoleMapFilePath
        pass
    
    jsonString = FileUtil.readContent(clusterIPRoleMapFilePath)
    ipRoleMap = json.loads(jsonString)
    
    ip_list = ipRoleMap.keys()
    
    roleIPMap = {}
    for role in Params.OPENSTACK_ROLES :
        roleIPMap[role] = []
        for ip in ip_list:
            role_list = ipRoleMap[ip]
            if role in role_list :
                roleIPMap[role].append(ip)
                pass
            pass
        pass
    
    #record the active nodes by role
    activeRoleIPMap = {}
    for role in roleIPMap.keys() :
        if len(roleIPMap[role]) > 0 :
            activeRoleIPMap[role] = roleIPMap[role]
            pass
        pass
    return activeRoleIPMap

def getInitCmdByRole(role):
    ######DEBUG
    initCmd = 'hostname'
    
    if role == 'keystone' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/keystone/initKeystone.py'
        pass
    
    if role == 'glance' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/glance/initGlance.py'
        pass
    
    if role == 'cinder-api' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/cinder/initCinder.py'
        pass
    
    if role == 'cinder-storage' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/cinder/initCinderStorage.py'
        pass
    
    if role == 'horizon' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/dashboard/initDashboard.py'
        pass
    
    if role == 'heat' :
        initCmd = 'python /etc/puppet/fuel-python/openstack/icehouse/heat/initHeat.py'
        pass
    
    
    
    
    return initCmd
    
    
    
if __name__ == '__main__':
    print 'init OpenStack HA----------------------'
    TAG = '/opt/openstack_init'
    if os.path.exists(TAG) :
        logger.info('OpenStack HA has been initted-----')
        pass
    else :
        logger.info('start to init OpenStack HA----------------')
        cluster_id = ''
        argv = sys.argv
        argv.pop(0)
        print "agrv=%s--" % argv
        if debug == False :
            if len(argv) > 0 :
                cluster_id = str(argv[0])
                pass
            else :
                print "ERROR:no params, do not transter cluster_id to this init file yet."
                exit()
                pass
            pass
        else :
            print "debug mode.................."
            cluster_id = str(argv[0])
            print 'cluster_id=%s' % cluster_id
            pass
        
        activeRoleIPMap = getActiveRoleIPMap(cluster_id)
        
        CLUSTER_ROLE_MAP_JSON_FILE_PATH = Params.CLUSTER_ROLE_MAP_JSON_FILE_PATH_TEMPLATE.format(cluster_id=cluster_id)
        FileUtil.writeContent(CLUSTER_ROLE_MAP_JSON_FILE_PATH, json.dumps(activeRoleIPMap, indent=4))
                              
        activeRoles = activeRoleIPMap.keys()
        print 'activeRoles=%s' % activeRoles
        #######DO EXECUTION
        for role in Params.OPENSTACK_ROLES :
            if role in activeRoles :
                ip_list = activeRoleIPMap[role]
                cmdTemplate = 'ssh root@{ip} {cmd}'
                cmd1 = 'ps aux | grep keystone| grep -v grep'
                cmd2 = 'bash /opt/ostf/keystone/keystone_user_list'
                cmd3 = 'bash /opt/ostf/keystone/keystone_service_list'
                for ip in ip_list :
                    execRemoteCmd(ip, 'echo `date` >> /tmp/testdate.txt', timeout=600)
                    print '------%s' % ip
                    remoteCmd1 = cmdTemplate.format(ip=ip, cmd=cmd1)
                    output, exitcode = ShellCmdExecutor.execCmd(remoteCmd1)
                    result1 = output.strip()
                    
                    remoteCmd2 = cmdTemplate.format(ip=ip, cmd=cmd2)
                    output, exitcode = ShellCmdExecutor.execCmd(remoteCmd2)
                    result2 = output.strip()
                    
                    remoteCmd3 = cmdTemplate.format(ip=ip, cmd=cmd3)
                    output, exitcode = ShellCmdExecutor.execCmd(remoteCmd3)
                    result3 = output.strip()
                    
#                     result2 = execRemoteCmd(ip, cmd2, timeout=600)
#                     result3 = execRemoteCmd(ip, cmd3, timeout=600)
                    print '---------------item1'
                    print result1
                    
                    print '---------------item2'
                    print result2
                    
                    print '---------------item3'
                    print result3
                    
                    pass
                time.sleep(2)
                pass
            pass 
        
#         os.system('touch %s' % TAG)
        pass
    pass
#     
#     role = 'glance'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass   
#     
#     role = 'neutron-server'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass 
#     
#     role = 'neutron'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass 
#     
#     role = 'nova-api'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass   
#     
#     role = 'nova-compute'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass
#     
#     role = 'cinder-api'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass   
#     
#     role = 'cinder-storage'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass  
#     
#     role = 'heat'
#     if role in activeRoles :
#         ip_list = activeRoleIPMap[role]
#         for ip in ip_list :
#             ######Do something
#             pass
#         pass 
#     pass



