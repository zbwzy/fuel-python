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

if __name__ == '__main__':
    print 'hello pexpect test============'
    print 'start time: %s' % time.ctime()
    from common.yaml.YAMLUtil import YAMLUtil
    ShellCmdExecutor.execCmd('ifconfig br-data down')
    ShellCmdExecutor.execCmd('ifconfig br-storage down')
    local_data_ip = YAMLUtil.getExIP()
    local_storage_ip = YAMLUtil.getStorageIP()
    rm_data_ip = 'ip addr del %s/24 dev br-data' % local_data_ip 
    rm_storage_ip = 'ip addr del %s/24 dev br-storage' % local_storage_ip 
    ShellCmdExecutor.execCmd(rm_data_ip)
    ShellCmdExecutor.execCmd(rm_storage_ip)

    FileUtil.replaceFileContent('/etc/sysconfig/network-scripts/ifcfg-bond0.102', 'br-storage', 'br-inspector') 
    FileUtil.replaceFileContent('/etc/sysconfig/network-scripts/ifcfg-bond0.103', 'br-data', 'br-provision') 
    FileUtil.replaceFileContent('/etc/sysconfig/network-scripts/ifcfg-br-storage', 'br-storage', 'br-inspector') 
    FileUtil.replaceFileContent('/etc/sysconfig/network-scripts/ifcfg-br-data', 'br-data', 'br-provision') 
    
    ShellCmdExecutor.execCmd('mv /etc/sysconfig/network-scripts/ifcfg-br-storage /etc/sysconfig/network-scripts/ifcfg-br-inspector')
    ShellCmdExecutor.execCmd('mv /etc/sysconfig/network-scripts/ifcfg-br-provision /etc/sysconfig/network-scripts/ifcfg-br-provision')

    ShellCmdExecutor.execCmd('systemctl restart network')
    ShellCmdExecutor.execCmd('brctl delbr br-storage')
    ShellCmdExecutor.execCmd('brctl delbr br-data')
     
    exit()
    
    #when execute script,exec: python <this file absolute path>
    ###############################
    
    ####TEST yum package
    getPackage4()
#     getPackage3()
    
#     getPackage2()
    
#     getPackage()
#     getAllPackage()
    
    ####TEST 
    
    exit()
    
    
    #TEST:wc -l ====
    output, exitcode = ShellCmdExecutor.execCmd('ls -lt /opt/openstack_conf/tag/ | grep bcrdb_ | wc -l')
    bcrdb_mark_num = output.strip()
    print 'output=%s--' % bcrdb_mark_num
    if bcrdb_mark_num == "2" :
        print 'exist file regex:bcrdb.'
        pass
    else :
        print "TTTT"
        pass
    #itoa
    num = 66
    str1 = "%d" % num
    print str1
    print type(str1)
    arr = [1,2,3]
    bb = '%d'% len(arr)
    print 'array num:%s' % bb
    print type(bb)
    
    print 'FFFFFFFFFFFFFFFFFFFFFF===================='
    fileObj = open('testfile.txt', 'a')
    fileObj.write('Hello world')
    fileObj.close()
    print 'FFFFFF#####'
    
    
    print 'databases=================='
    
    databaseNamesString = '''
| dns_domains                                |
| fixed_ips                                  |
| floating_ips                               |
| instance_actions                           |
| instance_actions_events                    |
| instance_extra                             |
| instance_faults                            |
| instance_group_member                      |
| instance_group_policy                      |
| instance_groups                            |
| instance_id_mappings                       |
| instance_info_caches                       |
| instance_metadata                          |
| instance_system_metadata                   |
| instance_type_extra_specs                  |
| instance_type_projects                     |
| instance_types                             |
| instances                                  |
| iscsi_targets                              |
| key_pairs                                  |
| migrate_version                            |
| migrations                                 |
| networks                                   |
| pci_devices                                |
| project_user_quotas                        |
| provider_fw_rules                          |
| quota_classes                              |
| quota_usages                               |
| quotas                                     |
| reservations                               |
| s3_images                                  |
| security_group_default_rules               |
| security_group_instance_association        |
| security_group_rules                       |
| security_groups                            |
| services                                   |
| shadow_agent_builds                        |
| shadow_aggregate_hosts                     |
| shadow_aggregate_metadata                  |
| shadow_aggregates                          |
| shadow_block_device_mapping                |
| shadow_bw_usage_cache                      |
| shadow_cells                               |
| shadow_certificates                        |
| shadow_compute_nodes                       |
| shadow_console_pools                       |
| shadow_consoles                            |
| shadow_dns_domains                         |
| shadow_fixed_ips                           |
| shadow_floating_ips                        |
| shadow_instance_actions                    |
| shadow_instance_actions_events             |
| shadow_instance_extra                      |
| shadow_instance_faults                     |
| shadow_instance_group_member               |
| shadow_instance_group_policy               |
| shadow_instance_groups                     |
| shadow_instance_id_mappings                |
| shadow_instance_info_caches                |
| shadow_instance_metadata                   |
| shadow_instance_system_metadata            |
'''
    sqlString = ''
    print databaseNamesString.strip().split('|')
    for e in  databaseNamesString.strip().split('|') :
        print e.strip()
        if e.strip() != '' :
            sqlString += 'select * from %s;' % e.strip()
            pass
        
        pass
    
    print 'sqlString=%s' % sqlString
    
    databaseNamesString = '''
| artifact_blob_locations          |
| artifact_blobs                   |
| artifact_dependencies            |
| artifact_properties              |
| artifact_tags                    |
| artifacts                        |
| image_locations                  |
| image_members                    |
| image_properties                 |
| image_tags                       |
| images                           |
| metadef_namespace_resource_types |
| metadef_namespaces               |
| metadef_objects                  |
| metadef_properties               |
| metadef_resource_types           |
| metadef_tags                     |
| migrate_version                  |
| task_info                        |
| tasks                            |
    '''
    sqlString = ''
    print databaseNamesString.strip().split('|')
    for e in  databaseNamesString.strip().split('|') :
        print e.strip()
        if e.strip() != '' :
            sqlString += 'select * from %s;' % e.strip()
            pass
    print 'sqlString=%s' % sqlString
    print 'databases#################'
    
    exit()
    #TEST:wc -l ####
    #TEST:array===
    b = []
    a = [1,2,3]
    b = a[1:]
    print b
    
   
    exit()
    #TEST:array####
    
    #TEST:wait unitl file exists==
    file_path = '/tmp/tt.txt'
    timeout = 20
    time_count = 0
    print 'test timeout==='
    while True:
        flag = os.path.exists(file_path)
        if flag == True :
            print 'wait time: %s second(s).' % time_count
            print 'do something......'
            break
        else :
            step = 1
#             print 'wait %s second(s)......' % step
            time_count += step
            time.sleep(1)
            pass
        
        if time_count == timeout :
            print 'Do nothing!timeout=%s.' % timeout
            break
        pass
    exit()
    #TEST:wait unitl file exists####
    ###########
    
#     a = ['10.20.0.91','10.20.0.92','10.20.0.93']
#     a.pop(0)
#     print a
#     exit()


    #exit()
    #Test data
    ShellCmdExecutor.execCmd('touch /tmp/tt.txt')
    imageFilePath = '/tmp/tt.txt'
    ip = '10.20.0.192'

    scpCmd = 'scp {imageFilePath} root@{glance_ip}:/home/'.format(imageFilePath=imageFilePath, glance_ip=ip)
    print 'scpCmd=%s--' % scpCmd

    '''
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.20.0.192' (RSA) to the list of known hosts.
root@10.20.0.192's password:
    '''
    try:
        import pexpect

#         child = pexpect.spawn(scpCmd)
        child = pexpect.spawn('bash /opt/createNeutronUser.sh')
#         child.expect('Are you sure you want to continue connecting.*')

        password = "123456"
        child.expect('User Password:')

        child.sendline('123456')

        expect_pass_string = "root@{ip}'s password:".format(ip=ip)
        #password = "123456"
#         child.expect(expect_pass_string)
        child.expect('Repeat User Password:')
        child.sendline(password)

        while True :
            regex = "[\\s\\S]*"
            index = child.expect([regex , pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                break
            elif index == 1:
                pass   #continue to wait
            elif index == 2:
                pass    #continue to wait

        child.sendline('exit')
        child.sendcontrol('c')
        #child.interact()
    except OSError:
        print 'Catch exception %s when sync glance image.' % OSError.strerror
        sys.exit(0)
        pass

    ###########################
    #ShellCmdExecutor.execCmd('rm -rf /tmp/tt.txt')
    print 'hello pexpect test#######'
    pass


    
