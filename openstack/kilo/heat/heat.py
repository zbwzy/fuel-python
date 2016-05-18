'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python heat.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
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
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

class Prerequisites(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def prepare():
        Network.Prepare()
        
        cmd = 'yum install openstack-utils -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install openstack-selinux -y'
        ShellCmdExecutor.execCmd(cmd)
        
        cmd = 'yum install python-openstackclient -y'
        ShellCmdExecutor.execCmd(cmd)
        pass
    pass

class Network(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def Prepare():
        Network.stopIPTables()
        Network.stopNetworkManager()
        pass
    
    @staticmethod
    def stopIPTables():
        stopCmd = "service iptables stop"
        ShellCmdExecutor.execCmd(stopCmd)
        pass
    
    @staticmethod
    def stopNetworkManager():
        stopCmd = "service NetworkManager stop"
        chkconfigOffCmd = "chkconfig NetworkManager off"
        
        ShellCmdExecutor.execCmd(stopCmd)
        ShellCmdExecutor.execCmd(chkconfigOffCmd)
        pass
    
'''
TODO:
in /etc/heat/heat.conf======
[DEFAULT]
...
heat_metadata_server_url = http://controller:8000
heat_waitcondition_server_url = http://controller:8000/v1/waitcondition

'''
class Heat(object):
    '''
    classdocs
    '''
    HEAT_CONF_FILE_PATH = "/etc/heat/heat.conf"
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Heat.install start===='
        yumCmd = 'yum install openstack-heat-api openstack-heat-api-cfn openstack-heat-engine python-heatclient -y'
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Heat.install done####'
        pass

    @staticmethod
    def restart():
        #restart heat service
        ShellCmdExecutor.execCmd("service openstack-heat-api restart")
        ShellCmdExecutor.execCmd("service openstack-heat-api-cfn restart")
        ShellCmdExecutor.execCmd("service openstack-heat-engine restart")
        pass
    
    
    @staticmethod
    def start():    
        ShellCmdExecutor.execCmd("service openstack-heat-api start")
        ShellCmdExecutor.execCmd("service openstack-heat-api-cfn start")
        ShellCmdExecutor.execCmd("service  openstack-heat-engine  start")
            
        ShellCmdExecutor.execCmd("chkconfig openstack-heat-api on")
        ShellCmdExecutor.execCmd("chkconfig openstack-heat-api-cfn on")
        ShellCmdExecutor.execCmd("chkconfig  openstack-heat-engine on")
        pass
    
    @staticmethod
    def configConfFile():
        vipParamsDict = JSONUtility.getValue('vip')
        mysql_vip = vipParamsDict["mysql_vip"]
        
        mysql_params_dict = JSONUtility.getRoleParamsDict('mysql')
        mysql_password = mysql_params_dict["mysql_password"]
        
        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        
        keystone_vip = vipParamsDict["keystone_vip"]
        glance_vip = vipParamsDict["glance_vip"]
        heat_mysql_password = JSONUtility.getValue("heat_mysql_password")
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        heat_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'heat', 'heat.conf')
        print 'heat_conf_template_file_path=%s' % heat_conf_template_file_path
        
        heatConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HEAT_CONF_DIR')
        print 'heatConfDir=%s' % heatConfDir #/etc/heat
        
        heat_conf_file_path = os.path.join(heatConfDir, 'heat.conf')
        print 'heat_conf_file_path=%s' % heat_conf_file_path
        
        if not os.path.exists(heatConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % heatConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 /etc/heat")
        
        if os.path.exists(heat_conf_file_path) :
            ShellCmdExecutor.execCmd("rm -rf %s" % heat_conf_file_path)
            pass
        
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (heat_conf_template_file_path, heatConfDir))
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/heat.conf' % heat_conf_template_file_path)
        ShellCmdExecutor.execCmd('mv /tmp/heat.conf /etc/heat/')
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % heat_conf_file_path)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        FileUtil.replaceFileContent(heat_conf_file_path, '<MYSQL_PASSWORD>', mysql_password)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<HEAT_MYSQL_PASSWORD>', heat_mysql_password)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(heat_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(heat_conf_file_path, '<GLANCE_VIP>', glance_vip)
        
        FileUtil.replaceFileContent(heat_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % heat_conf_file_path)
        pass
    pass

    
class HeatHA(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def isExistVIP(vip, interface):
        cmd = 'ip addr show dev {interface} | grep {vip}'.format(interface=interface, vip=vip)
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == None or output == '':
            print 'Do no exist vip %s on interface %s.' % (vip, interface)
            return False
        
        if debug == True :
            output = '''
            xxxx
            inet 192.168.11.100/32 scope global eth0
            xxxx
            '''
            pass
        
        newString = vip + '/'
        if newString in output :
            print 'exist vip %s on interface %s.' % (vip, interface)
            return True
        else :
            print 'Do no exist vip %s on interface %s.' % (vip, interface)
            return False
        pass
    
    #return value: 192.168.11.100/32
    @staticmethod
    def getVIPFormatString(vip, interface):
        vipFormatString = ''
        if HeatHA.isExistVIP(vip, interface) :
            print 'getVIPFormatString====exist vip %s on interface %s' % (vip, interface) 
            cmd = 'ip addr show dev {interface} | grep {vip}'.format(interface=interface, vip=vip)
            output, exitcode = ShellCmdExecutor.execCmd(cmd)
            vipFormatString = output.strip()
            if debug == True :
                fakeVIPFormatString = 'inet 192.168.11.100/32 scope global eth0'
                vipFormatString = fakeVIPFormatString
                pass
            
            result = vipFormatString.split(' ')[1]
            pass
        else :
            #construct vip format string
            print 'getVIPFormatString====do not exist vip %s on interface %s, to construct vip format string' % (vip, interface) 
            vipFormatString = '{vip}/32'.format(vip=vip)
            print 'vipFormatString=%s--' % vipFormatString
            result = vipFormatString
            pass
        
        return result
    
    @staticmethod
    def addVIP(vip, interface):
        result = HeatHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not HeatHA.isExistVIP(vip, interface) :
            print 'NOT exist vip %s on interface %s.' % (vip, interface)
            addVIPCmd = 'ip addr add {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'addVIPCmd=%s--' % addVIPCmd
            ShellCmdExecutor.execCmd(addVIPCmd)
            pass
        else :
            print 'The VIP %s already exists on interface %s.' % (vip, interface)
            pass
        pass
    
    @staticmethod
    def deleteVIP(vip, interface):
        result = HeatHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if HeatHA.isExistVIP(vip, interface) :
            deleteVIPCmd = 'ip addr delete {format_vip} dev {interface}'.format(format_vip=result, interface=interface)
            print 'deleteVIPCmd=%s--' % deleteVIPCmd
            ShellCmdExecutor.execCmd(deleteVIPCmd)
            pass
        else :
            print 'The VIP %s does not exist on interface %s.' % (vip, interface)
            pass
        pass
    
    @staticmethod
    def isKeepalivedInstalled():
        KEEPALIVED_CONF_FILE_PATH = '/etc/keepalived/keepalived.conf'
        if os.path.exists(KEEPALIVED_CONF_FILE_PATH) :
            return True
        else :
            return False
        
    @staticmethod
    def isHAProxyInstalled():
        HAPROXY_CONF_FILE_PATH = '/etc/haproxy/haproxy.cfg'
        if os.path.exists(HAPROXY_CONF_FILE_PATH) :
            return True
        else :
            return False
    
    @staticmethod
    def install():
        if debug == True :
            print "DEBUG is True.On local dev env, do test==="
            yumCmd = "ls -lt"
            ShellCmdExecutor.execCmd(yumCmd)
            pass
        else :
            if not HeatHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not HeatHA.isHAProxyInstalled() :
                haproxyInstallCmd = 'yum install haproxy -y'
                ShellCmdExecutor.execCmd(haproxyInstallCmd)
                
                #prepare haproxy conf file template
                openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
                haproxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
                haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
                print 'haproxyTemplateFilePath=%s' % haproxyTemplateFilePath
                print 'haproxyConfFilePath=%s' % haproxyConfFilePath
                if not os.path.exists('/etc/haproxy') :
                    ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
                    pass
                
                ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (haproxyTemplateFilePath, '/etc/haproxy'))
                pass
            pass
        pass
    
    @staticmethod
    def configure():
        HeatHA.configureHAProxy()
        HeatHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        #server heat-01 192.168.1.137:8004 check inter 10s
        vipParamsDict = JSONUtility.getValue('vip')
        heat_vip = vipParamsDict["heat_vip"]
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        HAProxyTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'haproxy.cfg')
        haproxyConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'HAPROXY_CONF_FILE_PATH')
        print 'haproxyConfFilePath=%s' % haproxyConfFilePath
        if not os.path.exists('/etc/haproxy') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/haproxy')
            pass
        
        if not os.path.exists(haproxyConfFilePath) :
            ShellCmdExecutor.execCmd('cat %s > /tmp/haproxy.cfg' % HAProxyTemplateFilePath)
            ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        #############
        heatBackendApiStringTemplate = '''
listen heat_api_cluster
  bind <HEAT_VIP>:8004
  balance source
  <HEAT_API_SERVER_LIST>
  '''
        heatBackendApiString = heatBackendApiStringTemplate.replace('<HEAT_VIP>', heat_vip)
        
        ################new
        heat_ips = JSONUtility.getValue("heat_ips")
        heat_ip_list = heat_ips.strip().split(',')
        
        serverHeatAPIBackendTemplate   = 'server heat-<INDEX> <SERVER_IP>:8004 check inter 2000 rise 2 fall 5'
        
        heatAPIServerListContent = ''
        
        index = 1
        for heat_ip in heat_ip_list:
            print 'heat_ip=%s' % heat_ip
            heatAPIServerListContent += serverHeatAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', heat_ip)
            
            heatAPIServerListContent += '\n'
            heatAPIServerListContent += '  '
            
            index += 1
            pass
        
        heatAPIServerListContent = heatAPIServerListContent.strip()
        print 'heatAPIServerListContent=%s--' % heatAPIServerListContent
        
        heatBackendApiString = heatBackendApiString.replace('<HEAT_API_SERVER_LIST>', heatAPIServerListContent)
        
        print 'heatBackendApiString=%s--' % heatBackendApiString
        
        #append
#         ShellCmdExecutor.execCmd('sudo echo "%s" >> %s' % (heatBackendApiString, haproxyConfFilePath))

        if os.path.exists(haproxyConfFilePath) :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % haproxyConfFilePath)
        else :
            output, exitcode = ShellCmdExecutor.execCmd('cat %s' % HAProxyTemplateFilePath)
            pass
        
        haproxyNativeContent = output.strip()

        haproxyContent = ''
        haproxyContent += haproxyNativeContent
        haproxyContent += '\n\n'
        haproxyContent += heatBackendApiString
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        if os.path.exists(haproxyConfFilePath):
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % haproxyConfFilePath)
            pass
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
        
        ShellCmdExecutor.execCmd('sudo chmod 644 %s' % haproxyConfFilePath)
        pass
    
    @staticmethod
    def configureKeepalived():
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        ###################configure keepalived
        keepalivedTemplateFilePath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'keepalived.conf')
        keepalivedConfFilePath = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'KEEPALIVED_CONF_FILE_PATH')
        print 'keepalivedConfFilePath=%s' % keepalivedConfFilePath
        if not os.path.exists('/etc/keepalived') :
            ShellCmdExecutor.execCmd('sudo mkdir /etc/keepalived')
            pass
        
        #configure haproxy check script in keepalived
        checkHAProxyScriptPath = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'check_haproxy.sh')
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (checkHAProxyScriptPath, '/etc/keepalived'))
        if os.path.exists(keepalivedConfFilePath) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % keepalivedConfFilePath)
            pass
        
        ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (keepalivedTemplateFilePath, keepalivedConfFilePath))
        print 'keepalivedTemplateFilePath=%s==========----' % keepalivedTemplateFilePath
        print 'keepalivedConfFilePath=%s=============----' % keepalivedConfFilePath
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % keepalivedConfFilePath)
        ##configure
        '''keepalived template====
        global_defs {
  router_id LVS-DEVEL
}
vrrp_script chk_haproxy {
   script "/etc/keepalived/check_haproxy.sh"
   interval 2
   weight  2
}

vrrp_instance 42 {
  virtual_router_id 42
  # for electing MASTER, highest priority wins.
  priority  <KEYSTONE_WEIGHT>
  state     <KEYSTONE_STATE>
  interface <INTERFACE>
  track_script {
    chk_haproxy
}
  virtual_ipaddress {
        <VIRTURL_IPADDR>
  }
}
        '''
        #WEIGHT is from 300 to down, 300 belongs to MASTER, and then 299, 298, ...etc, belong to SLAVE
        ##Here: connect to ZooKeeper to coordinate the weight
        heat_vip = '' 
        heat_vip_interface = JSONUtility.getValue("heat_vip_interface")
        
        weight_counter = 300
        if HeatHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = HeatHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass
        
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', heat_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', heat_vip)
        
        ##temporary: if current user is not root
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % keepalivedConfFilePath)
        
        #If keepalived need to support more VIP: append here
        pass
    
    @staticmethod
    def isHAProxyRunning():
        cmd = 'ps aux | grep haproxy | grep -v grep | wc -l'
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == '0' :
            return False
        else :
            return True
        
    @staticmethod
    def isKeepalivedRunning():
        cmd = 'ps aux | grep keepalived | grep -v grep | wc -l'
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        output = output.strip()
        if output == '0' :
            return False
        else :
            return True
        pass
    
    @staticmethod
    def getIndex(): #get host index, the ips has been sorted ascended.
        print 'To get this host index of role %s==============' % "heat" 
        heat_ips = JSONUtility.getValue('heat_ips')
        heat_ip_list = heat_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'heat_ip_list=%s--------------' % heat_ip_list
        index = heat_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if HeatHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            heat_vip_interface = JSONUtility.getValue("heat_vip_interface")
            heat_vip = '' 
            
            HeatHA.addVIP(heat_vip, heat_vip_interface)
            
            if HeatHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
            if HeatHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            ShellCmdExecutor.execCmd('service haproxy restart')
            
            isMasterNode = HeatHA.isMasterNode()
            if isMasterNode == True :
                HeatHA.restart()
                pass
            else :
                HeatHA.deleteVIP(heat_vip, heat_vip_interface)
                pass
            pass
        
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
    @staticmethod
    def restart():
        ShellCmdExecutor.execCmd('service haproxy restart')
        ShellCmdExecutor.execCmd('service keepalived restart')
        pass
    
    
if __name__ == '__main__':
    print 'hello openstack-icehouse:heat============'
    print 'start time: %s' % time.ctime()
    #DEBUG
    debug = False
    if debug :
        print 'start to debug======'
        
        print 'end debug######'
        exit()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/heat_installed'
    #DEBUG
#     if False :
#         ShellCmdExecutor.execCmd('rm -rf %s' % INSTALL_TAG_FILE)
#         pass
        
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'heat installed####'
        print 'exit===='
        pass
    else :
        Prerequisites.prepare()
        Heat.install()
        Heat.configConfFile()
    #     Heat.start()
    #     
    #     ## Heat HA
    #     HeatHA.install()
    #     HeatHA.configure()
    #     HeatHA.start()
        #
        #mark: heat is installed
        from openstack.kilo.common.adminopenrc import AdminOpenrc
        AdminOpenrc.prepareAdminOpenrc()
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:heat#######'
    pass

