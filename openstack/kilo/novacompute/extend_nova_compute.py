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
from common.yaml.YAMLUtil import YAMLUtil


class ExtendNovaCompute(object):
    '''
    classdocs
    '''
    NOVA_CONF_FILE_PATH = "/etc/nova/nova.conf"
    
    
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
    

if __name__ == '__main__':
    
    print 'Start to extend compute node(s)============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.

    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/novacompute_extended'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-compute extended####'
        print 'exit===='
        pass
    else :
        compute_node_ips = sys.argv
        print 'compute_node_ips=%s--' % compute_node_ips
        compute_node_ips.pop(0)
        print 'compute_node_ips=%s--' % compute_node_ips
        if len(compute_node_ips) == 0 :
            print 'Usage: python extend_nova_compute.py <compute_ip1> <compute_ip2> ... \nNote: The compute node ip should be management ip.'
            sys.exit(1)
            pass
        
        print 'compute_node_ips=%s--' % compute_node_ips
        
        #/etc/hosts
        ExtendNovaCompute.extendEtcHosts(compute_node_ips)
        
        #prepare original cluster info
        ExtendNovaCompute.prepareCurClusterParams(compute_node_ips)
        
        #configure nova compute
        ExtendNovaCompute.configConfFile()
        
        
        #
        if not os.path.exists('/opt/openstack_conf/tag/install') :
            os.system('mkdir -p /opt/openstack_conf/tag/install')
            pass
        
        #mark: nova-compute is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:nova-compute#######'
    pass

