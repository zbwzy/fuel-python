'''
Created on May 2, 2017

@author: zhangbai
'''

'''
usage:

python nova.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
'''
import sys
import os
import time
import json
import traceback

reload(sys)
sys.setdefaultencoding('utf8')

debug = False
if debug == True :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python-shanghai'
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

class ExtendNovaCompute(object):
    '''
    classdocs
    '''
    EXTENDED_INFO_FILE = '/root/rm_node/extended_history.json'
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def getCurClusterParamsDict():
        cwd_dir_path = os.getcwd()
        print 'cwd_dir_path=%s--' % cwd_dir_path
        original_cluster_json = os.path.join(cwd_dir_path, "original_cluster.json")
        print 'original_cluster_json=%s--' % original_cluster_json
        jsonDict = json.loads(FileUtil.readContent(original_cluster_json))
        return jsonDict
    
    @staticmethod
    def getComputeNodes():
        dict = ExtendNovaCompute.getCurClusterParamsDict()
        return dict["compute_nodes"]
    
    @staticmethod
    def getControllerNodes():
        dict = ExtendNovaCompute.getCurClusterParamsDict()
        return dict["controller_nodes"]
    
    @staticmethod
    def getHostNameBy(ip):
        cmd = 'ssh root@{ip} hostname'.format(ip=ip)
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        if output != None and output != "" :
            output = output.strip()
            host = output.split('\n')[-1]
            return host
            pass
        else :
            return None
        pass
    
    @staticmethod
    def extendEtcHosts(extended_compute_node_ips):
        originalHostLines = ''
        cmd = 'ssh root@{ip} cat /etc/hosts'.format(ip=ExtendNovaCompute.getControllerNodes()[0])
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if 'Warning' in output :
            lineList = output.split('\n')
            for line in lineList :
                if 'Warning' not in line :
                    originalHostLines += line + '\n'
                    pass
                pass
            pass
        else :
            originalHostLines = output
            pass
        
        originalHostLines = originalHostLines.strip()
        print 'originalHostLines=%s--' % originalHostLines
        
        
        extendComputeHostlines = ''
        for ip in extended_compute_node_ips :
            hostname = ExtendNovaCompute.getHostNameBy(ip)
            traditionHostName = hostname.rstrip(".tld").rstrip(".domain")
            line = ip + ' ' + traditionHostName + ' ' + hostname + '\n'
            extendComputeHostlines += line
            pass
        
        hostLines = originalHostLines + '\n' + extendComputeHostlines
        
        for ip in ExtendNovaCompute.getControllerNodes() :
            setHostInfoCmd = 'ssh root@{ip} \'echo "{hostLines}" > /etc/hosts\''.format(ip=ip,hostLines=hostLines)
            ShellCmdExecutor.execCmd(setHostInfoCmd)
            pass
        
        for ip in ExtendNovaCompute.getComputeNodes() :
            setHostInfoCmd = 'ssh root@{ip} \'echo "{hostLines}" > /etc/hosts\''.format(ip=ip,hostLines=hostLines)
            ShellCmdExecutor.execCmd(setHostInfoCmd)
            pass
        
        for ip in extended_compute_node_ips :
            setHostInfoCmd = 'ssh root@{ip} \'echo "{hostLines}" > /etc/hosts\''.format(ip=ip,hostLines=hostLines)
            ShellCmdExecutor.execCmd(setHostInfoCmd)
            pass
        
        print 'extendComputeHostlines=%s---' % extendComputeHostlines
        pass
    
    @staticmethod
    def prepareCurClusterParams(extend_compute_ips):
        controllerNodesList = ExtendNovaCompute.getControllerNodes()
        controllerNodeIP = controllerNodesList[0]
        paramsFilePath = '/opt/openstack_conf/openstack_params.json'
        for compute_ip in extend_compute_ips :
            scp_cmd = 'ssh root@{controller_ip} scp -r /opt/openstack_conf/openstack_params.json root@{extend_compute_ip} /opt/openstack_conf/cur_openstack_params.json'\
            .format(extend_compute_ip=compute_ip)
            ShellCmdExecutor.execCmd(scp_cmd)
            pass
        pass
    
    @staticmethod
    def configAfterNetworkNodeConfiguration():
        '''
1.on Controller node: moidfy /etc/nova/nova.conf, enabled metadata:

[DEFAULT]
service_neutron_metadata_proxy=true
neutron_metadata_proxy_shared_secret=123456

2. on Controller node: moidfy /etc/nova/nova.conf:to support VMs creation if vif_plug fails
vif_plugging_is_fatal=false
vif_plugging_timeout=0

        '''
        pass
    
    @staticmethod
    def reconfigLibvirtd():
        ###libvirtd :  /etc/libvirt/libvirtd.conf
        ### /etc/sysconfig/libvirtd
        libvirtdConfFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'libvirtd', 'libvirtd.conf')
        libvirtdFileTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'libvirtd', 'libvirtd.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/libvirt/' % libvirtdConfFileTemplatePath)
        ShellCmdExecutor.execCmd('cp -r %s /etc/sysconfig/' % libvirtdFileTemplatePath)
        
        ShellCmdExecutor.execCmd('chown -R root:root /etc/libvirt/libvirtd.conf')
        ShellCmdExecutor.execCmd('chown -R root:root /etc/sysconfig/libvirtd')
        
        ShellCmdExecutor.execCmd('systemctl restart libvirtd.service')
        pass
    
    @staticmethod
    def getValue(key):
        openstackConfFileDir = PropertiesUtility.getOpenstackConfBaseDir()
        openstack_params_file_path = os.path.join(openstackConfFileDir, "cur_openstack_params.json")
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
            print 'ERROR:no key %s in openstack_params.json.' % str(key)
            pass
        
        #refactor: if key='admin_email', value = 'admin@cmss.chinamobile.com'
        if key == 'admin_email' :
            value = 'admin@cmss.chinamobile.com'
            pass
            
        return value
    
    @staticmethod
    def configConfFile(extend_compute_ips):
        for ip in extend_compute_ips :
            configCmd = 'ssh root@{ip} python /etc/puppet/fuel-python/openstack/kilo/novacompute/novacompute_extend.py'\
            .format(ip=ip)
            ShellCmdExecutor.execCmd(configCmd)
            pass
        pass
    
    @staticmethod
    def start(extend_compute_ips):
        for ip in extend_compute_ips :
            configCmd = 'ssh root@{ip} python /etc/puppet/fuel-python/openstack/kilo/novacompute/novacompute_extend.py'\
            .format(ip=ip)
            ShellCmdExecutor.execCmd(configCmd)
            pass
        pass
    
    @staticmethod
    def getHistoryNodeIPs(key):
        extened_info_history_file_path = ExtendNovaCompute.EXTENDED_INFO_FILE
        if os.path.exists(extened_info_history_file_path) :
            jsonContent = JSONUtility.getContent(extened_info_history_file_path)
            pass
        else :
            print 'The file path: %s not exists!' % extened_info_history_file_path
            return None
            pass
        
        try :
            jsonDict = json.loads(jsonContent)
            print 'jsonDict=%s--' % jsonDict
        except Exception, e :
            print 'Exception happens when do json loads file %s' % extened_info_history_file_path
            print 'Exception:%s' % str(e)
        
        value = ''    
        if jsonDict.has_key(key):
            value = jsonDict[key]
            pass
        else :
            print 'ERROR:no key %s in %s.' % (str(key), ExtendNovaCompute.EXTENDED_INFO_FILE)
            pass
        
        return value
    
    @staticmethod
    def isComputeNodeExistInHistory(mgmt_ip):
        compute_node = ExtendNovaCompute.getHistoryNodeIPs('compute_node')
        if compute_node == None :
            print 'history info is NONE!!'
            return False
        
        if mgmt_ip.strip() in compute_node:
            print 'The compute node[%s] has been extended.' % mgmt_ip
            return True
        else :
            print 'The compute node[%s] has NOT been extended.' % mgmt_ip
            return False
        pass
    
    @staticmethod
    def appendToExtendHistory(mgmt_ip):
        compute_node_list = []
        cur_compute_node_list = ExtendNovaCompute.getHistoryNodeIPs('compute_node')
        if cur_compute_node_list == None:
            compute_node_list.append(mgmt_ip)
            pass
        else :
            cur_compute_node_list.append(mgmt_ip)
            compute_node_list = cur_compute_node_list
            pass

        json_dict = {}
        json_dict["compute_node"] = compute_node_list
        json_str = json.dumps(json_dict, indent=2)
        
        json_file_path = ExtendNovaCompute.EXTENDED_INFO_FILE
        if not os.path.exists(os.path.dirname(json_file_path)) :
            os.mkdir(os.path.dirname(json_file_path))
            pass
        
        FileUtil.writeContent(json_file_path, json_str)
        pass
    
    

if __name__ == '__main__':
    print 'Start to extend compute node(s)============'
    
    print 'start time: %s' % time.ctime()

    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/novacompute_extended'
    
    compute_node_ips = sys.argv
    compute_node_ips.pop(0)
    print 'compute_node_ips=%s--' % compute_node_ips
    if len(compute_node_ips) == 0 :
        print '++++++++++++++++++++++++++++++++++++++++++++++'
        print 'Usage: \npython extend_compute_node.py <compute_ip1> <compute_ip2> ... \n\nNote: \nThe compute node ip should be management ip.'
        print '++++++++++++++++++++++++++++++++++++++++++++++'
        sys.exit(1)
        pass
    
    from common.lock.FileBasedLock import FileBasedLock
    file_lock = FileBasedLock(lockFilePath='/opt/openstack_conf/lock/extend_compute_lock')
    if file_lock.acquire(acquireTimeout=60) == True :
        try :
            for ip in compute_node_ips:
                if ExtendNovaCompute.isComputeNodeExistInHistory(ip) :
                    print 'Do nothing......'
                    pass
                else :
                    cmd = 'ssh root@{compute_ip} python /etc/puppet/fuel-python/openstack/kilo/novacompute/initNovaCompute.py'.format(compute_ip=ip)
                    print 'cmd=%s' % cmd
                    output, exitcode = ShellCmdExecutor.execCmd(cmd)
                    print 'output=%s--' % output
                    print 'exitcode=%s--' % exitcode
                    
                    cmd1 = 'ssh root@{compute_ip} python /etc/puppet/fuel-python/openstack/kilo/novacompute/initNovaCompute.py'.format(compute_ip=ip)
                    print 'cmd1=%s' % cmd1
                    output1, exitcode1 = ShellCmdExecutor.execCmd(cmd1)
                    print 'output1=%s--' % output1
                    print 'exitcode1=%s--' % exitcode1
                    if exitcode == 0 :
                        ExtendNovaCompute.appendToExtendHistory(ip)
                        pass
                    #mark that the compute node is extended
                    pass
                pass
            pass
        except Exception, e :
            print 'ERROR: %s' % e
            print traceback.format_exc()
        finally: 
            file_lock.release()
            pass
        pass
        
        
        #/etc/hosts
#         ExtendNovaCompute.extendEtcHosts(compute_node_ips)
        
        #prepare original cluster info
#         ExtendNovaCompute.prepareCurClusterParams(compute_node_ips)
        
        #configure nova compute
#         ExtendNovaCompute.configConfFile()
        
        
    print 'hello openstack-kilo:nova-compute extended done#######'
    pass

