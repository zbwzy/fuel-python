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
    PROJ_HOME_DIR = '/Users/zhangbai/Documents/AptanaWorkspace/fuel-python-icbc-dev'
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
from common.yaml.YAMLUtil import YAMLUtil
from openstack.common.serverSequence import ServerSequence


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
        yumCmd = 'yum install docker influxdb openstack-ceilometer-api openstack-ceilometer-collector \
  openstack-ceilometer-notification openstack-ceilometer-central openstack-ceilometer-alarm \
  python-ceilometerclient python2-jsonpath-rw-ext python-memcached python-oslo-policy MySQL-python python-oslo-log -y'
  
        ShellCmdExecutor.execCmd(yumCmd)
        
        ShellCmdExecutor.execCmd('systemctl restart docker')
        print 'Ceilometer.install done####'
        pass
    
    @staticmethod
    def loadGnocchi():
        ShellCmdExecutor.execCmd('docker load < /etc/puppet/modules/ceilometer/files/gnocchi-with-httpd-2016-02-04.tar')
        ShellCmdExecutor.execCmd('docker tag 075090cb04ab bcec/gnocchi-with-httpd:1.3.0')
        ShellCmdExecutor.execCmd('docker run -d -it --name gnocchi --net host --volume /apps/logs/gnocchi:/var/log/gnocchi 075090cb04ab bash')
        pass
    
    @staticmethod
    def activateGnocchiConfFile():
        gnocchi_conf_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'gnocchi')
        ShellCmdExecutor.execCmd('cp -r %s /etc/logrotate.d/' % gnocchi_conf_file_path)
        ShellCmdExecutor.execCmd('logrotate -f /etc/logrotate.d/gnocchi')
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
        enable_cmd = 'systemctl enable openstack-ceilometer-api.service openstack-ceilometer-notification.service \
        openstack-ceilometer-central.service openstack-ceilometer-collector.service \
        openstack-ceilometer-alarm-evaluator.service openstack-ceilometer-alarm-notifier.service'
        
        start_cmd = 'systemctl start openstack-ceilometer-api.service openstack-ceilometer-notification.service \
        openstack-ceilometer-central.service openstack-ceilometer-collector.service \
        openstack-ceilometer-alarm-evaluator.service openstack-ceilometer-alarm-notifier.service'
        
        ShellCmdExecutor.execCmd(enable_cmd)
        ShellCmdExecutor.execCmd(start_cmd)
        pass
    
    @staticmethod
    def configInflux():
        local_mgmt_ip = YAMLUtil.getManagementIP()
        influxdb_conf_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'influxdb.conf')
        ShellCmdExecutor.execCmd('cp -r %s /etc/influxdb/' % influxdb_conf_file_template_path)
        influxdb_conf_file_path = '/etc/influxdb/influxdb.conf'
        FileUtil.replaceFileContent(influxdb_conf_file_path, '<LOCAL_MANAGEMENT_IP>', local_mgmt_ip)
        
        ###influxdb cluster conf file
        influxdb_cluster_conf_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'influxdb')
        ShellCmdExecutor.execCmd('cp -r %s /etc/default/' % influxdb_cluster_conf_file_template_path)
        influxdb_cluseter_conf_file_path = '/etc/default/influxdb'
        ceilometer_ip_list = YAMLUtil.getRoleManagementIPList('ceilometer')
        
        servicePortList = []
        for ip in ceilometer_ip_list :
            servicePort = ip + ':8091'
            servicePortList.append(servicePort)
            pass
        
        servicePortString = ','.join(servicePortList)
        FileUtil.replaceFileContent(influxdb_cluseter_conf_file_path, '<SERVICE_STRING>', servicePortString)
        pass
    
    @staticmethod
    def startInflux():
        start_cmd = 'systemctl start influxdb'
        ShellCmdExecutor.execCmd(start_cmd)
        pass
    
    @staticmethod
    def initInflux():
        vipParmasDict = JSONUtility.getRoleParamsDict('vip')
        influxdb_vip = vipParmasDict['influxdb_vip']
        print 'influxdb_vip=%s--' % influxdb_vip
        cmd1 = 'create database gnocchi'
        Ceilometer.execInfluxCmd(influxdb_vip, cmd1)
        Ceilometer.execInfluxCmd(influxdb_vip, 'use gnocchi')

        ceilometerParamsDict = JSONUtility.getRoleParamsDict('ceilometer')
        gnocchi_influxdb_password = ceilometerParamsDict['gnocchi_influxdb_password']
        cmd2 = 'CREATE USER root WITH PASSWORD \'%s\' WITH ALL PRIVILEGES' % gnocchi_influxdb_password
        print 'cmd2=%s--' % cmd2
        Ceilometer.execInfluxCmd(influxdb_vip, cmd2)

        cmd3 = 'GRANT ALL PRIVILEGES ON gnocchi TO root'
        Ceilometer.execInfluxCmd(influxdb_vip, cmd3)
        pass
    
    @staticmethod
    def execInfluxCmd(host, influx_cmd):
        cmd = 'influx -host {host} -execute \"{cmd}\"'.format(host=host,cmd=influx_cmd)
        output,exitcode = ShellCmdExecutor.execCmd(cmd)
        print 'output=%s---' % output
        pass
    
    @staticmethod
    def getGnocchiContainerID():
        containerID = ''
        cmd = 'docker ps --all | grep gnocchi  | awk \'{print $1}\''
        output, exitcode = ShellCmdExecutor.execCmd(cmd)
        containerID = output.strip()
        return containerID
    
    @staticmethod
    def execDockerCmd(container_id, cmd):
        dockerCmd = "docker exec -it {container_id} bash -c '{cmd}'".format(container_id=container_id,cmd=cmd)
        output, exitcode = ShellCmdExecutor.execCmd(dockerCmd)
        print 'execDockerCmd.output=%s' % output
        print 'execDockerCmd.exitcode=%s' % exitcode
        
        pass
    
    @staticmethod
    def configGnocchi():
        local_mgmt_ip = YAMLUtil.getManagementIP()
        gnocchi_conf_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'gnocchi.conf')
        
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/' % gnocchi_conf_file_template_path)
        gnocchi_conf_dest_file = '/opt/openstack_conf/gnocchi.conf'
        '''
        <GNOCCHI_DBPASS>
        <GNOCCHI_VIP>
        <KEYSTONE_VIP>
        <KEYSTONE_GNOCCHI_PASSWORD>
        <INFLUXDB_VIP>
        <INFLUXDB_PASSWORD>
        '''
        ceilometerParamsDict = JSONUtility.getRoleParamsDict('ceilometer')
        
        gnocchi_influxdb_password = ceilometerParamsDict['gnocchi_influxdb_password']
        gnocchi_dbpass = ceilometerParamsDict['gnocchi_dbpass']
        
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict['keystone_vip']
        influxdb_vip = vipParamsDict['influxdb_vip']
        gnocchi_vip = vipParamsDict['gnocchi_vip']
        
        keystone_gnocchi_password = JSONUtility.getValue("keystone_gnocchi_password")
        
        FileUtil.replaceFileContent(gnocchi_conf_dest_file, '<GNOCCHI_DBPASS>', gnocchi_dbpass)
        FileUtil.replaceFileContent(gnocchi_conf_dest_file, '<GNOCCHI_VIP>', gnocchi_vip)
        FileUtil.replaceFileContent(gnocchi_conf_dest_file, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(gnocchi_conf_dest_file, '<KEYSTONE_GNOCCHI_PASSWORD>', keystone_gnocchi_password)
        FileUtil.replaceFileContent(gnocchi_conf_dest_file, '<INFLUXDB_VIP>', influxdb_vip)
        FileUtil.replaceFileContent(gnocchi_conf_dest_file, '<INFLUXDB_PASSWORD>', gnocchi_influxdb_password)
        
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'docker cp /opt/openstack_conf/gnocchi.conf {container_id}:/etc/gnocchi/'.format(container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def configGnocchiApiPaste():
        local_mgmt_ip = YAMLUtil.getManagementIP()
        gnocchi_conf_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'api-paste.ini')
        
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'docker cp {src_file_path} {container_id}:/etc/gnocchi/'.format(src_file_path=gnocchi_conf_file_template_path, container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def configGnocchiHttpConfFile():
        container_id = Ceilometer.getGnocchiContainerID()
        httpd_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'httpd.conf')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/' % httpd_conf_template_file_path)
        
        cmd = 'docker cp /opt/openstack_conf/httpd.conf {container_id}:/etc/httpd/conf/'.format(container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def configGnocchiWsgiConfFile():
        local_mgmt_ip = YAMLUtil.getManagementIP()
        container_id = Ceilometer.getGnocchiContainerID()
        gnocchi_wsgi_conf_template_file_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'gnocchi-wsgi.conf')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/' % gnocchi_wsgi_conf_template_file_path)
        FileUtil.replaceFileContent('/opt/openstack_conf/gnocchi-wsgi.conf', '<LOCAL_MANAGEMENT_IP>', local_mgmt_ip)
        
        cmd = 'docker cp /opt/openstack_conf/gnocchi-wsgi.conf {container_id}:/etc/httpd/conf.d/'.format(container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def startGnocchiHttp():
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'chmod 777 /var/log/gnocchi/'
        Ceilometer.execDockerCmd(container_id, cmd)
        
        start_cmd = 'httpd'
        Ceilometer.execDockerCmd(container_id, start_cmd)
        pass
    
    @staticmethod
    def initIndexerDB():
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'gnocchi-upgrade'
        Ceilometer.execDockerCmd(container_id, cmd)
        #
        cmd = 'docker cp /opt/openstack_conf/admin-openrc.sh {container_id}:/root'.format(container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        #
        pass
    
    @staticmethod
    def configArchivePolicy():
        archive_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'archive_policy.sh')
        ShellCmdExecutor.execCmd('cp -r %s /opt/openstack_conf/' % archive_file_template_path)
        
        admin_token = JSONUtility.getValue('admin_token')
        vipParamsDict = JSONUtility.getValue('vip')
        
        keystone_admin_password = JSONUtility.getValue('keystone_admin_password')
        keystone_vip = vipParamsDict["keystone_vip"]
        
        archive_policy_file_path = '/opt/openstack_conf/archive_policy.sh'
        FileUtil.replaceFileContent(archive_policy_file_path, '<ADMIN_TOKEN>', admin_token)
        FileUtil.replaceFileContent(archive_policy_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(archive_policy_file_path, '<KEYSTONE_ADMIN_PASSWORD>', keystone_admin_password)
        
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'docker cp /opt/openstack_conf/archive_policy.sh {container_id}:/root'.format(container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        pass
    
    @staticmethod
    def resetGnocchiApiPasteFile():
        api_paste_file_template_path = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'ceilometer', 'api-paste.ini.original')
        
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'docker cp {src_file_path} {container_id}:/etc/gnocchi'.format(src_file_path=api_paste_file_template_path, container_id=container_id)
        ShellCmdExecutor.execCmd(cmd)
        
        Ceilometer.execDockerCmd(container_id, 'rm -rf /etc/gnocchi/api-paste.ini')
        Ceilometer.execDockerCmd(container_id, 'mv /etc/gnocchi/api-paste.ini.original /etc/gnocchi/api-paste.ini')
        Ceilometer.execDockerCmd(container_id, 'killall -e httpd')
        Ceilometer.execDockerCmd(container_id, 'httpd')
        pass
    
    @staticmethod
    def createArchivePolicy():
        container_id = Ceilometer.getGnocchiContainerID()
        cmd = 'bash /root/archive_policy.sh'
        Ceilometer.execDockerCmd(container_id, cmd)
        pass
    
    @staticmethod
    def configConfFile():
        vipParamsDict = JSONUtility.getValue('vip')
        keystone_vip = vipParamsDict['keystone_vip']
        gnocchi_vip = vipParamsDict['gnocchi_vip']
        mysql_vip = vipParamsDict["mysql_vip"]

        rabbit_params_dict = JSONUtility.getRoleParamsDict('rabbitmq')
        rabbit_hosts = rabbit_params_dict["rabbit_hosts"]
        rabbit_userid = rabbit_params_dict["rabbit_userid"]
        rabbit_password = rabbit_params_dict["rabbit_password"]
        ceilometer_dbpass = JSONUtility.getValue("ceilometer_dbpass")
        keystone_ceilometer_password = JSONUtility.getValue("keystone_ceilometer_password")
        
        ceilometer_params_dict = JSONUtility.getRoleParamsDict('ceilometer')
        metering_secret = ceilometer_params_dict['ceilometer_metering_secret']
        
        openstackConfPopertiesFilePath = PropertiesUtility.getOpenstackConfPropertiesFilePath()
        local_mgmt_ip = YAMLUtil.getManagementIP()
        
        ceilometer_params_dict = JSONUtility.getRoleParamsDict('ceilometer')
        ceilometer_ip_list = ceilometer_params_dict["mgmt_ips"]
        memcached_service_list = []
        for ip in ceilometer_ip_list:
            memcached_service_list.append(ip.strip() + ':11211')
            pass
        memcached_service_string = ','.join(memcached_service_list)
        
        print 'mysql_vip=%s' % mysql_vip
        print 'rabbit_hosts=%s' % rabbit_hosts
        print 'rabbit_userid=%s' % rabbit_userid
        print 'rabbit_password=%s' % rabbit_password
        print 'keystone_vip=%s' % keystone_vip
        
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
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<CEILOMETER_DBPASS>', ceilometer_dbpass)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<MEMCACHED_LIST>', memcached_service_string)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<GNOCCHI_VIP>', gnocchi_vip)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<MYSQL_VIP>', mysql_vip)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<RABBIT_HOSTS>', rabbit_hosts)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<RABBIT_PASSWORD>', rabbit_password)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<KEYSTONE_CEILOMETER_PASSWORD>', keystone_ceilometer_password)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<KEYSTONE_VIP>', keystone_vip)
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<METERING_SECRET>', metering_secret)
        
        FileUtil.replaceFileContent(ceilometer_conf_file_path, '<LOCAL_MANAGEMENT_IP>', local_mgmt_ip)
        
        ShellCmdExecutor.execCmd("chmod 640 %s" % ceilometer_conf_file_path)
        ShellCmdExecutor.execCmd("chown -R root:ceilometer %s" % ceilometer_conf_file_path)
        pass
    
    @staticmethod
    def getServerIndex():
        local_management_ip = YAMLUtil.getManagementIP() 
        ceilometer_params_dict = JSONUtility.getRoleParamsDict('ceilometer')
        ceilometer_server_ip_list = ceilometer_params_dict["mgmt_ips"]
        index = ServerSequence.getIndex(ceilometer_server_ip_list, local_management_ip)
        return index
    pass


if __name__ == '__main__':
    print 'hello openstack-kilo:ceilometer============'
    print 'start time: %s' % time.ctime()
    #DEBUG
    if debug :
        print 'start to debug======'
#         Ceilometer.configInflux()
#         Ceilometer.startInflux()
#         Ceilometer.initInflux()
        print 'influx##############'
        exit()
        
        ceilometer_ip_list = ['10.142.55.54', '10.142.55.53']
        servicePortList = []
        for ip in ceilometer_ip_list :
            servicePort = ip + ':8091'
            servicePortList.append(servicePort)
            pass
        
        servicePortString = ','.join(servicePortList)
        print 'configInflux.servicePortString=%s--' % servicePortString
        print 'end debug######'
        exit()
        pass
    
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/ceilometer_installed'
    #DEBUG
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'ceilometer installed####'
        print 'exit===='
        pass
    else :
        print '============'
        Ceilometer.install()
        
        print 'start to install influxdb========'
        Ceilometer.configInflux()
        Ceilometer.startInflux()
        print 'done to install influxdb###########'
        
        print 'start to load gnocchi image======='
        
        print 'done to load gnocchi image########'
        
        #configure ceilometer
        Ceilometer.configConfFile()
        
        
    #     Ceilometer.start()
    #     
    #     ## Ceilometer HA
#         CeilometerHA.install()
#         CeilometerHA.configure()
    #     CeilometerHA.start()
        #
        #mark: ceilometer is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello openstack-kilo:ceilometer#######'
    pass

