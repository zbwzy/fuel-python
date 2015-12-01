'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python ceilometer.py

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

OPENSTACK_VERSION_TAG = 'icehouse'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')

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


class Ceilometer(object):
    '''
    classdocs
    '''
    METERING_SECRET_FILE_PATH = '/opt/metering_secret'
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def install():
        print 'Ceilometer.install start===='
        yumCmd = 'yum install openstack-ceilometer-api openstack-ceilometer-collector \
  openstack-ceilometer-notification openstack-ceilometer-central openstack-ceilometer-alarm \
  python-ceilometerclient -y'
  
        ShellCmdExecutor.execCmd(yumCmd)
        print 'Ceilometer.install done####'
        pass
    
    @staticmethod
    def getMeteringSecret():
        if not os.path.exists(Ceilometer.METERING_SECRET_FILE_PATH) :
            output, exitcode = ShellCmdExecutor.execCmd("openssl rand -hex 10")
            meteringSecret = output.strip()
            FileUtil.writeContent(Ceilometer.METERING_SECRET_FILE_PATH, meteringSecret)
            pass
        
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % Ceilometer.METERING_SECRET_FILE_PATH)
        
        meteringSecret = output.strip()
        
        return meteringSecret
        

    @staticmethod
    def restart():
        #restart ceilometer service
        ShellCmdExecutor.execCmd("service openstack-ceilometer-api restart")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-notification restart")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-central restart")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-collector restart")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-alarm-evaluator restart")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-alarm-notifier restart")
        pass
    
    
    @staticmethod
    def start():    
        ShellCmdExecutor.execCmd("service openstack-ceilometer-api start")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-notification start")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-central start")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-collector start")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-alarm-evaluator start")
        ShellCmdExecutor.execCmd("service openstack-ceilometer-alarm-notifier start")
            
        ShellCmdExecutor.execCmd("chkconfig openstack-ceilometer-api on")
        ShellCmdExecutor.execCmd("chkconfig openstack-ceilometer-notification on")
        ShellCmdExecutor.execCmd("chkconfig openstack-ceilometer-central on")
        ShellCmdExecutor.execCmd("chkconfig openstack-ceilometer-collector on")
        ShellCmdExecutor.execCmd("chkconfig openstack-ceilometer-alarm-evaluator on")
        ShellCmdExecutor.execCmd("chkconfig openstack-ceilometer-alarm-notifier on")
        pass
    
    @staticmethod
    def configConfFile():
        mysql_vip = JSONUtility.getValue("mysql_vip")
        mysql_password = JSONUtility.getValue("mysql_password")
        
        rabbit_host = JSONUtility.getValue("rabbit_host")
        
        rabbit_hosts = JSONUtility.getValue("rabbit_hosts")
        rabbit_userid = JSONUtility.getValue("rabbit_userid")
        rabbit_password = JSONUtility.getValue("rabbit_password")
        
        keystone_vip = JSONUtility.getValue("keystone_vip")
        
        mongodb_vip = JSONUtility.getValue("mongodb_vip")
        ceilometer_mongo_password = JSONUtility.getValue("ceilometer_mongo_password")
        
        metering_secret = JSONUtility.getValue("ceilometer_metering_secret")
#         metering_secret = Ceilometer.getMeteringSecret()
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd('cat %s' % local_ip_file_path)
        localIP = output.strip()
        
        print 'mysql_vip=%s' % mysql_vip
        print 'mysql_password=%s' % mysql_password
        print 'rabbit_host=%s' % rabbit_host
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        print 'locaIP=%s' % localIP
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        ceilometer_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'ceilometer.conf')
        print 'ceilometer_conf_template_file_path=%s' % ceilometer_conf_template_file_path
        
        ceilometerConfDir = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'CEILOMETER_CONF_DIR')
        print 'ceilometerConfDir=%s' % ceilometerConfDir #/etc/ceilometer
        
        ceilometer_conf_file_path = os.path.join(ceilometerConfDir, 'ceilometer.conf')
        print 'ceilometer_conf_file_path=%s' % ceilometer_conf_file_path
        
        if not os.path.exists(ceilometerConfDir) :
            ShellCmdExecutor.execCmd("sudo mkdir %s" % ceilometerConfDir)
            pass
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % ceilometerConfDir)
        
        if os.path.exists(ceilometer_conf_file_path) :
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % ceilometer_conf_file_path)
            pass
        
#         ShellCmdExecutor.execCmd('sudo cp -r %s %s' % (ceilometer_conf_template_file_path, ceilometerConfDir))
        
        ShellCmdExecutor.execCmd('cat %s > /tmp/ceilometer.conf' % ceilometer_conf_template_file_path)
        ShellCmdExecutor.execCmd('mv -f /tmp/ceilometer.conf /etc/ceilometer/')
        ShellCmdExecutor.execCmd('rm -rf /tmp/ceilometer.conf')
        
        ShellCmdExecutor.execCmd("sudo chmod 777 %s" % ceilometer_conf_file_path)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<MONGODB_VIP>', mongodb_vip)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<CEILOMETER_DBPASS>', ceilometer_mongo_password)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<RABBIT_HOST>', rabbit_host)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<RABBIT_USERID>', rabbit_userid)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<METERING_SECRET>', metering_secret)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<LOCAL_IP>', localIP)
        
        ShellCmdExecutor.execCmd("sudo chmod 644 %s" % ceilometer_conf_file_path)
        pass
    pass

    
class CeilometerHA(object):
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
        if CeilometerHA.isExistVIP(vip, interface) :
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
        result = CeilometerHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if not CeilometerHA.isExistVIP(vip, interface) :
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
        result = CeilometerHA.getVIPFormatString(vip, interface)
        print 'result===%s--' % result
        if CeilometerHA.isExistVIP(vip, interface) :
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
            if not CeilometerHA.isKeepalivedInstalled() :
                keepalivedInstallCmd = "yum install keepalived -y"
                ShellCmdExecutor.execCmd(keepalivedInstallCmd)
                pass
            
            if not CeilometerHA.isHAProxyInstalled() :
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
        CeilometerHA.configureHAProxy()
        CeilometerHA.configureKeepalived()
        pass
    
    @staticmethod
    def configureHAProxy():
        ####################configure haproxy
        #server heat-01 192.168.1.137:8004 check inter 10s
        ceilometer_vip = JSONUtility.getValue("ceilometer_vip")
        
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
            ShellCmdExecutor.execCmd('rm -rf /tmp/haproxy.cfg')
            pass
        
        ShellCmdExecutor.execCmd('sudo chmod 777 %s' % haproxyConfFilePath)
        
        #############
        ceilometerBackendApiStringTemplate = '''
listen ceilometer_api_cluster
  bind <CEILOMETER_VIP>:8777
  balance source
  <CEILOMETER_API_SERVER_LIST>
  '''
        ceilometerBackendApiString = ceilometerBackendApiStringTemplate.replace('<CEILOMETER_VIP>', ceilometer_vip)
        
        ################new
        ceilometer_ips = JSONUtility.getValue("ceilometer_ips")
        ceilometer_ip_list = ceilometer_ips.strip().split(',')
        
        serverCeilometerAPIBackendTemplate   = 'server ceilometer-<INDEX> <SERVER_IP>:8777 check inter 2000 rise 2 fall 5'
        
        ceilometerAPIServerListContent = ''
        
        index = 1
        for ip in ceilometer_ip_list:
            print 'ceilometer_ip=%s' % ip
            ceilometerAPIServerListContent += serverCeilometerAPIBackendTemplate.replace('<INDEX>', str(index)).replace('<SERVER_IP>', ip)
            
            ceilometerAPIServerListContent += '\n'
            ceilometerAPIServerListContent += '  '
            
            index += 1
            pass
        
        ceilometerAPIServerListContent = ceilometerAPIServerListContent.strip()
        print 'ceilometerAPIServerListContent=%s--' % ceilometerAPIServerListContent
        
        ceilometerBackendApiString = ceilometerBackendApiString.replace('<CEILOMETER_API_SERVER_LIST>', ceilometerAPIServerListContent)
        
        print 'ceilometerBackendApiString=%s--' % ceilometerBackendApiString
        
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
        haproxyContent += ceilometerBackendApiString
        FileUtil.writeContent('/tmp/haproxy.cfg', haproxyContent)
        if os.path.exists(haproxyConfFilePath):
            ShellCmdExecutor.execCmd("sudo rm -rf %s" % haproxyConfFilePath)
            pass
        ShellCmdExecutor.execCmd('mv /tmp/haproxy.cfg /etc/haproxy/')
        ShellCmdExecutor.execCmd('rm -rf /tmp/haproxy.cfg')
        
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
        ceilometer_vip = JSONUtility.getValue("ceilometer_vip")
        ceilometer_vip_interface = JSONUtility.getValue("ceilometer_vip_interface")
        
        weight_counter = 300
        if CeilometerHA.isMasterNode() :
            weight_counter = 300
            state = 'MASTER'
            pass
        else :
            index = CeilometerHA.getIndex()  #get this host index which is indexed by the gid in /etc/astutue.yaml responding with this role
            weight_counter = 300 - index
            state = 'SLAVE' + str(index)
            pass
        
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<WEIGHT>', str(weight_counter))
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<STATE>', state)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<INTERFACE>', ceilometer_vip_interface)
        FileUtil.replaceFileContent(keepalivedConfFilePath, '<VIRTURL_IPADDR>', ceilometer_vip)
        
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
        print 'To get this host index of role %s==============' % "ceilometer" 
        ceilometer_ips = JSONUtility.getValue('ceilometer_ips')
        ceilometer_ip_list = ceilometer_ips.split(',')
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_ip_file_path = PropertiesUtility.getValue(openstackConfPopertiesFilePath, 'LOCAL_IP_FILE_PATH')
        output, exitcode = ShellCmdExecutor.execCmd("cat %s" % local_ip_file_path)
        localIP = output.strip()
        print 'localIP=%s---------------------' % localIP
        print 'ceilometer_ip_list=%s--------------' % ceilometer_ip_list
        index = ceilometer_ip_list.index(localIP)
        print 'index=%s-----------' % index
        return index
        
    @staticmethod
    def isMasterNode():
        if CeilometerHA.getIndex() == 0 :
            return True
        
        return False
    
    @staticmethod
    def start():
        if debug == True :
            pass
        else :
            ceilometer_vip_interface = JSONUtility.getValue("ceilometer_vip_interface")
            ceilometer_vip = JSONUtility.getValue("ceilometer_vip")
            
            CeilometerHA.addVIP(ceilometer_vip, ceilometer_vip_interface)
            
            if CeilometerHA.isHAProxyRunning() :
                ShellCmdExecutor.execCmd('service haproxy restart')
            else :
                ShellCmdExecutor.execCmd('service haproxy start')
                pass
            
            if CeilometerHA.isKeepalivedRunning() :
                ShellCmdExecutor.execCmd('service keepalived restart')
            else :
                ShellCmdExecutor.execCmd('service keepalived start')
                pass
            
            ShellCmdExecutor.execCmd('service haproxy restart')
            
            isMasterNode = CeilometerHA.isMasterNode()
            if isMasterNode == True :
                CeilometerHA.restart()
                pass
            else :
#                 CeilometerHA.deleteVIP(ceilometer_vip, ceilometer_vip_interface)
                #remove VIP on non-master host, just keep one VIP
                ShellCmdExecutor.execCmd('service keepalived stop')
                ShellCmdExecutor.execCmd('service keepalived start')
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
    print 'hello openstack-icehouse:ceilometer============'
    print 'start time: %s' % time.ctime()
    #DEBUG
    debug = False
    if debug :
        print 'start to debug======'
#         print CeilometerHA.configure()
        print 'end debug######'
        exit()
        pass
    
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/ceilometer_installed'
    #DEBUG
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'ceilometer installed####'
        print 'exit===='
        pass
    else :
        Prerequisites.prepare()
        Ceilometer.install()
        Ceilometer.configConfFile()
    #     Ceilometer.start()
    #     
    #     ## Ceilometer HA
    #     CeilometerHA.install()
    #     CeilometerHA.configure()
    #     CeilometerHA.start()
        #
        #mark: ceilometer is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-icehouse:ceilometer#######'
    pass

