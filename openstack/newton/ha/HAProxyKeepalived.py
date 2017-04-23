'''
Created on Mar 11, 2016

@author: zhangbai
'''
import sys
import os
import time

debug = False
if debug == True :
    #MODIFY HERE WHEN TEST ON HOST
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python'
    pass
else :
    # The real dir in which this project is deployed on PROD env.
    PROJ_HOME_DIR = '/etc/puppet/fuel-python'   
    pass

OPENSTACK_VERSION_TAG = 'newton'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil
from openstack.common.serverSequence import ServerSequence
from common.yaml.YAMLUtil import YAMLUtil

class HA(object):
    '''
    classdocs
    '''
    HaproxyConfFilePath = '/etc/haproxy/haproxy.cfg'
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        ShellCmdExecutor.execCmd('yum install keepalived ipvsadm haproxy -y')
        pass
    
    @staticmethod
    def configKeepalived():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        ha_vip1_interface = haParamsDict['ha_vip1_interface']
        ha_vip2_interface = haParamsDict['ha_vip2_interface']
        
        mask_bits = haParamsDict['mgmt_network_mask_bits']
        
        virtual_router_id = haParamsDict['virtual_router_id']
        auth_pass = haParamsDict['auth_pass']
        
        #The id is generated on nailgun, and the range should be 0 ~ 255, we use 3-bits: e.g. 320,789.
        virtual_router_id_1 = virtual_router_id
        virtual_router_id_2 = virtual_router_id - 1
    
        keepalived_conf_1_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ha', 'keepalived.conf.1')
        keepalived_conf_2_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ha', 'keepalived.conf.2')
        
        keepalived_conf_dest_path = '/etc/keepalived/keepalived.conf'
        haproxy_keepalived_ip_list = haParamsDict['mgmt_ips']
        
        local_management_ip = YAMLUtil.getManagementIP()
        serverIndex = ServerSequence.getIndex(haproxy_keepalived_ip_list, local_management_ip)
        if serverIndex == 0 :
            ShellCmdExecutor.execCmd('cp -r %s %s' % (keepalived_conf_1_template_path, keepalived_conf_dest_path))
            pass
        
        if serverIndex == 1 :
            ShellCmdExecutor.execCmd('cp -r %s %s' % (keepalived_conf_2_template_path, keepalived_conf_dest_path))
            pass
        
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<HA_VIP1>', ha_vip1)
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<HA_VIP1_INTERFACE>', ha_vip1_interface)
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<HA_VIP2>', ha_vip2)
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<HA_VIP2_INTERFACE>', ha_vip2_interface)
        
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<MASK_BITS>', mask_bits)
        
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<VIRTUAL_ROUTER_ID_1>', str(virtual_router_id_1))
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<VIRTUAL_ROUTER_ID_2>', str(virtual_router_id_2))
        FileUtil.replaceFileContent(keepalived_conf_dest_path, '<AUTH_PASS>', str(auth_pass))
        
        haproxy_check_script_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ha', 'haproxy_check.sh')
        ShellCmdExecutor.execCmd('cp -r %s /etc/keepalived/' % haproxy_check_script_path)
        ShellCmdExecutor.execCmd('chmod 644 %s' % keepalived_conf_dest_path)
        ShellCmdExecutor.execCmd('chmod 644 /etc/keepalived/haproxy_check.sh')
        pass
    
    @staticmethod
    def startKeepalived():
        ShellCmdExecutor.execCmd('systemctl restart keepalived.service')
        pass
    
    @staticmethod
    def restartKeepalived():
        ShellCmdExecutor.execCmd('systemctl restart keepalived.service')
        ShellCmdExecutor.execCmd('systemctl restart keepalived.service')
        pass
    
    @staticmethod
    def configHaproxy():
        haproxyTemplatePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ha', 'haproxy.cfg')
        ShellCmdExecutor.execCmd('cp -r %s /etc/haproxy/' % haproxyTemplatePath)
        
        if YAMLUtil.hasRoleInNodes('mysql') :
            HA.setMysqlHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('rabbitmq') :
            HA.setRabbitHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('keystone') :
            HA.setKeystoneHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('glance') :
            HA.setGlanceHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('nova-api') :
            HA.setNovaHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('neutron-server') :
            HA.setNeutronHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('horizon') :
            HA.setHorizonHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('cinder-api') :
            HA.setCinderHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('ceilometer') :
            HA.setCeilometerHaproxyString()
            pass
        
        if YAMLUtil.hasRoleInNodes('heat') :
            HA.setHeatHaproxyString()
            pass
        pass
    
    @staticmethod
    def startHaproxy():
        cmd = '/usr/bin/systemctl restart haproxy.service'
        timeout = 20
        time_count = 0
        os.system(cmd)
        
        while True :
            output, exitcode = ShellCmdExecutor.execCmd('ps aux | grep haproxy | grep -v grep')
            output = output.strip()
            if output == None or output == '' :
                print 'restart haproxy: %d count(s).' % time_count
                os.system(cmd)
                pass
            else :
                print 'HAProxy process exists!'
                break
            
            if time_count == timeout :
                print 'It is timeout when restart haproxy, and timeout=%s.' % timeout
                break
            
            time.sleep(1)
            time_count += 1
            pass
        pass
    
    @staticmethod
    def start():
        HA.startKeepalived()
        HA.startHaproxy()
        HA.restartKeepalived()
        pass
    
    @staticmethod
    def config():
        HA.configKeepalived()
        HA.configHaproxy()
        pass
    
    @staticmethod
    def appendBackendStringToHaproxyCfg(backendString):
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % HA.HaproxyConfFilePath)
        haproxyNativeContent = output.strip()

        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        haproxyContent += backendString
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        
        if os.path.exists(HA.HaproxyConfFilePath):
            ShellCmdExecutor.execCmd("rm -rf %s" % HA.HaproxyConfFilePath)
            pass
        
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % HA.HaproxyConfFilePath)
        pass
    
    @staticmethod
    def setMysqlHaproxyString():
        localIP = YAMLUtil.getManagementIP()
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        ha_ip_list = haParamsDict['mgmt_ips']
        
        mysqlBackendApiStringTemplate = '''
listen rdb_mysql
  bind <HA_VIP1>:3306
  balance  leastconn
  mode  tcp
  option  mysql-check user haproxy
  option  tcpka
  option  tcplog
  option  clitcpka
  option  srvtcpka
  timeout client  28801s
  timeout server  28801s
  <RDB_MYSQL_SERVER_LIST>
        '''
        
        mysqlBackendApiStringTemplate2 = '''
listen rdb_mysql
  bind <HA_VIP1>:3306
  balance  leastconn
  mode  tcp
  option  mysql-check user haproxy
  option  tcpka
  option  tcplog
  option  clitcpka
  option  srvtcpka
  timeout client  28801s
  timeout server  28801s
  <RDB_MYSQL_SERVER_LIST>
        '''
        
        mysqlParams = JSONUtility.getRoleParamsDict('mysql')
        mysql_ip_list = mysqlParams['mgmt_ips']
        
        if ServerSequence.getIndex(ha_ip_list, localIP) == 0 :
            mysqlBackendString = mysqlBackendApiStringTemplate.replace('<HA_VIP1>', ha_vip1)
            pass
        else :
#             mysqlBackendString = mysqlBackendApiStringTemplate2.replace('<HA_VIP2>', ha_vip2)
            mysqlBackendString = mysqlBackendApiStringTemplate2.replace('<HA_VIP1>', ha_vip1)
            pass
        
        #mysql master
        serverMysqlBacendString1 = 'server mysql1 %s:3305 check inter 2000 rise 2 fall 3' % mysql_ip_list[0]
        serverMysqlBackendTemplate   = 'server mysql<INDEX> <SERVER_IP>:3305 backup check inter 2000 rise 2 fall 3'
        
        mysqlServerListContent = ''
        mysqlServerListContent += serverMysqlBacendString1
        mysqlServerListContent += '\n'
        mysqlServerListContent += '  '
        
        index = 2
        if len(mysql_ip_list) > 1 :
            for mysql_ip in mysql_ip_list[1:] :
                print 'mysql_ip=%s' % mysql_ip
                mysqlServerListContent += serverMysqlBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', mysql_ip)
                
                mysqlServerListContent += '\n'
                mysqlServerListContent += '  '
                
                index += 1
                pass
        
        mysqlServerListContent = mysqlServerListContent.strip()
        print 'mysqlServerListContent=%s--' % mysqlServerListContent
        
        mysqlBackendString = mysqlBackendString.replace('<RDB_MYSQL_SERVER_LIST>', mysqlServerListContent)
        print 'mysqlBackendString=%s--' % mysqlBackendString
        HA.appendBackendStringToHaproxyCfg(mysqlBackendString)
        pass
        

    
    @staticmethod
    def setKeystoneHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        keystoneBackendPublicApiStringTemplate = '''
listen keystone_common
  bind <HA_VIP1>:5000
  balance  roundrobin
  option  httplog
  <KEYSTONE_PUBLIC_API_SERVER_LIST>
  '''
        keystoneBackendAdminApiStringTemplate = '''
listen keystone_admin
  bind <HA_VIP1>:35357
  balance  roundrobin
  option  httplog
  <KEYSTONE_ADMIN_API_SERVER_LIST>
  '''
        
        keystoneBackendAdminApiString = keystoneBackendAdminApiStringTemplate.replace('<HA_VIP1>', ha_vip1)
        keystoneBackendPublicApiString = keystoneBackendPublicApiStringTemplate.replace('<HA_VIP1>', ha_vip1)
        
        keystone_params_dict = JSONUtility.getRoleParamsDict('keystone')
        keystone_ip_list = keystone_params_dict['mgmt_ips']
        
        serverKeystoneAdminAPIBackendTemplate   = 'server keystone<INDEX> <SERVER_IP>:35357 check inter 2000 rise 2 fall 3'
        serverKeystonePublicAPIBackendTemplate  = 'server keystone<INDEX> <SERVER_IP>:5000 check inter 2000 rise 2 fall 3'
        
        keystoneAdminAPIServerListContent = ''
        keystonePublicAPIServerListContent = ''
        
        index = 1
        for keystone_ip in keystone_ip_list:
            print 'keystone_ip=%s' % keystone_ip
            keystoneAdminAPIServerListContent += serverKeystoneAdminAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            keystonePublicAPIServerListContent += serverKeystonePublicAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', keystone_ip)
            
            keystoneAdminAPIServerListContent += '\n'
            keystoneAdminAPIServerListContent += '  '
            
            keystonePublicAPIServerListContent += '\n'
            keystonePublicAPIServerListContent += '  '
            index += 1
            pass
        
        keystoneAdminAPIServerListContent = keystoneAdminAPIServerListContent.strip()
        keystonePublicAPIServerListContent = keystonePublicAPIServerListContent.strip()
        print 'keystoneAdminAPIServerListContent=%s--' % keystoneAdminAPIServerListContent
        print 'keystonePublicAPIServerListContent=%s--' % keystonePublicAPIServerListContent
        
        keystoneBackendAdminApiString = keystoneBackendAdminApiString.replace('<KEYSTONE_ADMIN_API_SERVER_LIST>', keystoneAdminAPIServerListContent)
        keystoneBackendPublicApiString = keystoneBackendPublicApiString.replace('<KEYSTONE_PUBLIC_API_SERVER_LIST>', keystonePublicAPIServerListContent)
        
        print 'keystoneBackendAdminApiString=%s--' % keystoneBackendAdminApiString
        print 'keystoneBackendPublicApiString=%s--' % keystoneBackendPublicApiString
        
        HA.appendBackendStringToHaproxyCfg(keystoneBackendPublicApiString)
        HA.appendBackendStringToHaproxyCfg(keystoneBackendAdminApiString)
        pass
    
    @staticmethod
    def setGlanceHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        glanceBackendApiStringTemplate = '''
listen glance_api
  bind <HA_VIP1>:9292
  balance  roundrobin
  option  httplog
  <GLANCE_API_SERVER_LIST>
  '''
        
        glanceBackendRegistryApiStringTemplate = '''
listen glance_registry
  bind <HA_VIP1>:9191
  balance  roundrobin
  option  httplog
  <GLANCE_REGISTRY_API_SERVER_LIST>
  '''
        glance_params_dict = JSONUtility.getRoleParamsDict('glance')
        glance_ip_list = glance_params_dict["mgmt_ips"]
        glanceBackendApiString = glanceBackendApiStringTemplate.replace('<HA_VIP1>', ha_vip1)
        glanceBackendRegistryApiString = glanceBackendRegistryApiStringTemplate.replace('<HA_VIP1>', ha_vip1)
        ###############
        serverGlanceRegistryAPIBackendTemplate = 'server glance<INDEX> <SERVER_IP>:9191 check inter 2000 rise 2 fall 3'
        serverGlanceAPIBackendTemplate         = 'server glance<INDEX> <SERVER_IP>:9292 check inter 2000 rise 2 fall 3'
        
        glanceRegistryAPIServerListContent = ''
        glanceAPIServerListContent = ''
        
        index = 1
        for glance_ip in glance_ip_list:
            print 'glance_ip=%s' % glance_ip
            glanceRegistryAPIServerListContent += serverGlanceRegistryAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            glanceAPIServerListContent += serverGlanceAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', glance_ip)
            
            glanceRegistryAPIServerListContent += '\n'
            glanceRegistryAPIServerListContent += '  '
            
            glanceAPIServerListContent += '\n'
            glanceAPIServerListContent += '  '
            
            index += 1
            pass
        
        glanceRegistryAPIServerListContent = glanceRegistryAPIServerListContent.strip()
        glanceAPIServerListContent = glanceAPIServerListContent.strip()
        print 'glanceRegistryAPIServerListContent=%s--' % glanceRegistryAPIServerListContent
        print 'glanceAPIServerListContent=%s--' % glanceAPIServerListContent
        
        glanceBackendRegistryApiString = glanceBackendRegistryApiString.replace('<GLANCE_REGISTRY_API_SERVER_LIST>', glanceRegistryAPIServerListContent)
        glanceBackendApiString = glanceBackendApiString.replace('<GLANCE_API_SERVER_LIST>', glanceAPIServerListContent)
        
        HA.appendBackendStringToHaproxyCfg(glanceBackendApiString)
        HA.appendBackendStringToHaproxyCfg(glanceBackendRegistryApiString)
        pass
    
    @staticmethod
    def setNovaHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        novaComputeApiBackendStringTemplate = '''
listen nova_compute_api
  bind <HA_VIP1>:8774
  balance  roundrobin
  option  httplog
  <NOVA_COMPUTE_API_SERVER_LIST>
  '''
        
        novaMetadataApiBackendStringTemplate = '''
listen nova_metadata_api
  bind <HA_VIP1>:8775
  balance  roundrobin
  option  httplog
  <NOVA_METADATA_API_SERVER_LIST>
        '''
        
        novaNovncproxyBackendStringTemplate = '''
listen nova_novncproxy
  bind <HA_VIP1>:6080
  balance  roundrobin
  option  httplog
  <NOVA_NOVNCPROXY_SERVER_LIST>
        '''
        
        nova_api_params_dict = JSONUtility.getRoleParamsDict('nova-api')
        nova_api_ip_list = nova_api_params_dict["mgmt_ips"]
        
        novaComputeApiBackendString = novaComputeApiBackendStringTemplate.replace('<HA_VIP1>', ha_vip1)
        novaMetadataApiBackendString = novaMetadataApiBackendStringTemplate.replace('<HA_VIP1>', ha_vip1)
        novaNovncproxyBackendString = novaNovncproxyBackendStringTemplate.replace('<HA_VIP1>', ha_vip1)
        ###############
        serverNovaMetadataAPIBackendTemplate = 'server coreapi<INDEX> <SERVER_IP>:8775 check inter 2000 rise 2 fall 3'
        serverNovaComputeAPIBackendTemplate  = 'server coreapi<INDEX> <SERVER_IP>:8774 check inter 2000 rise 2 fall 3'
        serverNovaNovncproxyBackendTemplate  = 'server coreapi<INDEX> <SERVER_IP>:6080 check inter 2000 rise 2 fall 3'
        
        novaMetadataAPIServerListContent = ''
        novaComputeAPIServerListContent = ''
        novaNovncproxyServerListContent = ''
        
        index = 1
        for nova_api_ip in nova_api_ip_list:
            print 'nova_api_ip=%s' % nova_api_ip
            novaMetadataAPIServerListContent += serverNovaMetadataAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            novaComputeAPIServerListContent += serverNovaComputeAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            novaNovncproxyServerListContent += serverNovaNovncproxyBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', nova_api_ip)
            
            novaMetadataAPIServerListContent += '\n'
            novaMetadataAPIServerListContent += '  '
            
            novaComputeAPIServerListContent += '\n'
            novaComputeAPIServerListContent += '  '
            
            novaNovncproxyServerListContent += '\n'
            novaNovncproxyServerListContent += '  '
            
            index += 1
            pass
        
        novaMetadataAPIServerListContent = novaMetadataAPIServerListContent.strip()
        novaComputeAPIServerListContent = novaComputeAPIServerListContent.strip()
        novaNovncproxyServerListContent = novaNovncproxyServerListContent.strip()
        print 'novaMetadataAPIServerListContent=%s--' % novaMetadataAPIServerListContent
        print 'novaComputeAPIServerListContent=%s--' % novaComputeAPIServerListContent
        print 'novaNovncproxyServerListContent=%s--' % novaNovncproxyServerListContent
        
        novaMetadataApiBackendString = novaMetadataApiBackendString.replace('<NOVA_METADATA_API_SERVER_LIST>', novaMetadataAPIServerListContent)
        novaComputeApiBackendString = novaComputeApiBackendString.replace('<NOVA_COMPUTE_API_SERVER_LIST>', novaComputeAPIServerListContent)
        novaNovncproxyBackendString = novaNovncproxyBackendString.replace('<NOVA_NOVNCPROXY_SERVER_LIST>', novaNovncproxyServerListContent)
        print 'novaMetadataApiBackendString=\n%s\n--' % novaMetadataApiBackendString
        print 'novaComputeApiBackendString=\n%s\n--' % novaComputeApiBackendString
        print 'novaNovncproxyBackendString=\n%s\n--' % novaNovncproxyBackendString
        HA.appendBackendStringToHaproxyCfg(novaComputeApiBackendString)
        HA.appendBackendStringToHaproxyCfg(novaMetadataApiBackendString)
        HA.appendBackendStringToHaproxyCfg(novaNovncproxyBackendString)
        pass
    
    @staticmethod
    def setNeutronHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        neutronServerBackendApiStringTemplate = '''
listen neutron_api
  bind <HA_VIP1>:9696
  balance  roundrobin
  option  httplog
  <NEUTRON_SERVER_LIST>
        '''
        neutronServerBackendString = neutronServerBackendApiStringTemplate.replace('<HA_VIP1>', ha_vip1)
        
        neutron_params_dict = JSONUtility.getRoleParamsDict('neutron-server')
        neutron_ip_list = neutron_params_dict["mgmt_ips"]
        
        serverNeutronServerBackendTemplate   = 'server coreapi<INDEX> <SERVER_IP>:9696 check inter 2000 rise 2 fall 3'
        
        neutronServerListContent = ''
        index = 1 
        for ip in neutron_ip_list :
            neutronServerListContent += serverNeutronServerBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            
            neutronServerListContent += '\n'
            neutronServerListContent += '  '
            
            index += 1
            pass
        
        neutronServerListContent = neutronServerListContent.strip()
        print 'neutronServerListContent=%s--' % neutronServerListContent
        
        neutronServerBackendString = neutronServerBackendString.replace('<NEUTRON_SERVER_LIST>', neutronServerListContent)
        print 'neutronServerBackendString=%s--' % neutronServerBackendString
        HA.appendBackendStringToHaproxyCfg(neutronServerBackendString)
        pass
    
    @staticmethod
    def setHorizonHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        horizonServerBackendString = '''
listen horizon
  bind <HA_VIP1>:80
  balance  source
  capture  cookie vgnvisitor= len 32
  cookie  SERVERID insert indirect nocache
  mode  http
  option  forwardfor
  option  httpchk
  option  httpclose
  option  httplog
  rspidel  ^Set-cookie:\ IP=
  timeout  client 3h
  timeout  server 3h
  <HORIZON_SERVER_LIST>
        '''
        horizonServerBackendString = horizonServerBackendString.replace('<HA_VIP1>', ha_vip1)
        
        horizon_params_dict = JSONUtility.getRoleParamsDict('horizon')
        horizon_ip_list = horizon_params_dict["mgmt_ips"]

        serverHorizonServerBackendTemplate   = 'server coreapi<INDEX> <SERVER_IP>:80 cookie coreapi<INDEX> check inter 2000 rise 2 fall 3'

        horizonServerListContent = ''
        index = 1
        for ip in horizon_ip_list :
            horizonServerListContent += serverHorizonServerBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            horizonServerListContent += '\n'
            horizonServerListContent += '  '
            index += 1
            pass

        horizonServerListContent = horizonServerListContent.strip()
        print 'horizonServerListContent=%s--' % horizonServerListContent

        horizonServerBackendString = horizonServerBackendString.replace('<HORIZON_SERVER_LIST>', horizonServerListContent)
        print 'horizonServerBackendString=%s--' % horizonServerBackendString
        HA.appendBackendStringToHaproxyCfg(horizonServerBackendString)
        pass
    
    @staticmethod
    def setCinderHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        cinderServerBackendString = '''
listen cinder_api
  bind <HA_VIP1>:8776
  balance  roundrobin
  option  httplog
  <CINDER_SERVER_LIST>
        '''
        cinderServerBackendString = cinderServerBackendString.replace('<HA_VIP1>', ha_vip1)
        cinder_params_dict = JSONUtility.getRoleParamsDict('cinder-api')
        cinder_ip_list = cinder_params_dict["mgmt_ips"]

        serverCinderBackendTemplate   = 'server cinder<INDEX> <SERVER_IP>:8776 check inter 2000 rise 2 fall 3'

        cinderServerListContent = ''
        index = 1
        for ip in cinder_ip_list :
            cinderServerListContent += serverCinderBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            cinderServerListContent += '\n'
            cinderServerListContent += '  '
            index += 1
            pass

        cinderServerListContent = cinderServerListContent.strip()
        print 'cinderServerListContent=%s--' % cinderServerListContent

        cinderServerBackendString = cinderServerBackendString.replace('<CINDER_SERVER_LIST>', cinderServerListContent)
        print 'cinderServerBackendString=%s--' % cinderServerBackendString
        HA.appendBackendStringToHaproxyCfg(cinderServerBackendString)
        pass
    
    @staticmethod
    def setCeilometerHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        ceilometerServerBackendString = '''
listen ceilometer_api
  bind <HA_VIP1>:8777
  balance  roundrobin
  option  httplog
  <CEILOMETER_SERVER_LIST>
        '''
        ceilometerServerBackendString = ceilometerServerBackendString.replace('<HA_VIP1>', ha_vip1)
#         ceilometerServerBackendString = ceilometerServerBackendString.replace('<HA_VIP2>', ha_vip2)
        ceilometer_params_dict = JSONUtility.getRoleParamsDict('ceilometer')
        ceilometer_ip_list = ceilometer_params_dict["mgmt_ips"]

        serverCeilometerBackendTemplate   = 'server ceilometer<INDEX> <SERVER_IP>:8777 check inter 2000 rise 2 fall 3'

        ceilometerServerListContent = ''
        index = 1
        for ip in ceilometer_ip_list :
            ceilometerServerListContent += serverCeilometerBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            ceilometerServerListContent += '\n'
            ceilometerServerListContent += '  '
            index += 1
            pass

        ceilometerServerListContent = ceilometerServerListContent.strip()
        print 'ceilometerServerListContent=%s--' % ceilometerServerListContent

        ceilometerServerBackendString = ceilometerServerBackendString.replace('<CEILOMETER_SERVER_LIST>', ceilometerServerListContent)
        print 'ceilometerServerBackendString=%s--' % ceilometerServerBackendString
        HA.appendBackendStringToHaproxyCfg(ceilometerServerBackendString)
        pass
    
    @staticmethod
    def setRabbitHaproxyString():
        haParamsDict = JSONUtility.getRoleParamsDict('haproxy-keepalived')
        
        ha_vip1 = haParamsDict['ha_vip1']
        ha_vip2 = haParamsDict['ha_vip2']
        
        rabbitmqServerBackendString = '''
listen rabbitmq
  bind <HA_VIP1>:5672
  balance  roundrobin
  mode  tcp
  option  tcpka
  timeout client  48h
  timeout server  48h
  <RABBITMQ_SERVER_LIST>
        '''
        rabbitmqServerBackendString = rabbitmqServerBackendString.replace('<HA_VIP1>', ha_vip1)
        rabbitmq_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbitmq_ip_list = rabbitmq_params_dict['mgmt_ips'] 

        serverRabbitmqBackupTemplate   = 'server rabbitmq<INDEX> <SERVER_IP>:5672  backup check inter 5000 rise 2 fall 3'

        rabbitmqServerListContent = ''
        masterServerString = 'server rabbitmq1 {server_ip}:5672   check inter 5000 rise 2 fall 3'.format(server_ip=rabbitmq_ip_list[0])
        rabbitmqServerListContent += masterServerString
        rabbitmqServerListContent += '\n'
        rabbitmqServerListContent += '  '
        
        if len(rabbitmq_ip_list) > 1 :
            index = 2
            for ip in rabbitmq_ip_list[1:] :
                rabbitmqServerListContent += serverRabbitmqBackupTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
                rabbitmqServerListContent += '\n'
                rabbitmqServerListContent += '  '
                index += 1
                pass

        rabbitmqServerListContent = rabbitmqServerListContent.strip()
        print 'rabbitmqServerListContent=%s--' % rabbitmqServerListContent

        rabbitmqServerBackendString = rabbitmqServerBackendString.replace('<RABBITMQ_SERVER_LIST>', rabbitmqServerListContent)
        print 'rabbitmqServerBackendString=%s--' % rabbitmqServerBackendString
        HA.appendBackendStringToHaproxyCfg(rabbitmqServerBackendString)
        pass
    
    @staticmethod
    def setHeatHaproxyString():
        pass
    
    
    
if __name__ == '__main__':
    
    print 'hello openstack-newton:haproxy-keepalived============'
    
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    #The params are retrieved from conf/openstack_params.json: generated in init.pp in site.pp.
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/ha_installed'
    if os.path.exists(INSTALL_TAG_FILE) :
        pass
    else :
        HA.install()
        HA.config()
        HA.start() 
        
        os.system('touch %s' % INSTALL_TAG_FILE)
        pass
    print 'hello openstack-newton:haproxy-keepalived########'
    
    
    

