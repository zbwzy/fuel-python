'''
Created on Nov 22, 2017

@author: zhangbai
'''
import sys
import os
import time
import traceback

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
SOURCE_RDB_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR, 'mysql', 'my.cnf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.file.FileUtil import FileUtil
from openstack.common.role import Role
from common.yaml.YAMLUtil import YAMLUtil

class ControllerServiceInit(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def initKeystone():
        if Role.isKeystoneRole() :
            from openstack.kilo.keystone.keystone import Keystone
            ShellCmdExecutor.execCmd('chmod 777 /etc/keystone')
            
            #wait the file /etc/keystone/fernet-keys produced on first keystone
            Keystone.scpFernetKeys()
            time.sleep(5)

            cmd1 = 'chown -R keystone:keystone /var/log/keystone'
            cmd2 = 'chown -R keystone:keystone /etc/keystone/fernet-keys'
            cmd3 = 'chmod -R o-rwx /etc/keystone/fernet-keys'
            ShellCmdExecutor.execCmd(cmd1)
            ShellCmdExecutor.execCmd(cmd2)
            ShellCmdExecutor.execCmd(cmd3)
            
            Keystone.start()
            pass
        pass
    
    @staticmethod
    def initGlance():
        if Role.isGlanceRole() :
            from openstack.kilo.glance.glance import Glance
            Glance.start()
            pass
        pass
    
    @staticmethod
    def initNovaApi():
        if Role.isNovaApiRole() :
            from openstack.kilo.nova.nova import Nova
            Nova.start()
        pass
    
    @staticmethod
    def initNeutronServer():
        if Role.isNeutronServerRole() :
            from openstack.kilo.neutronserver.neutronserver import NeutronServer
            NeutronServer.start()
            from common.openfile.OpenFile import OpenFile
            OpenFile.execModificationBy('/usr/lib/systemd/system', 'neutron-server.service')
            pass
        pass
    
    @staticmethod
    def initNeutronAgent():
        if Role.isNeutronAgentRole() :
            from openstack.kilo.network.network import Network
            Network.finalizeInstallation()
            #mark: network is initted
            #open limits of file & restart always
            if not Network.isNeutronServerNode() :
                from common.openfile.OpenFile import OpenFile
                OpenFile.execModification('/usr/lib/systemd/system', 'openstack-')
                OpenFile.execModificationBy('/usr/lib/systemd/system', 'neutron-dhcp-agent.service')
                pass
            pass
        pass
    
    @staticmethod
    def initCeilometer():
        if Role.isCeilometerRole() :
            from openstack.kilo.ceilometer.ceilometer import Ceilometer
            #init influxdb
            Ceilometer.initInflux()
            #load gnocchi image
            Ceilometer.loadGnocchi()
            
            Ceilometer.activateGnocchiConfFile()
            Ceilometer.configGnocchi()
           
            Ceilometer.configGnocchiHttpConfFile()
            Ceilometer.configGnocchiWsgiConfFile()
            Ceilometer.configArchivePolicy()
            
            if Ceilometer.getServerIndex() == 0 :
                Ceilometer.configGnocchiApiPaste()
                pass
            
            Ceilometer.startGnocchiHttp()
            
            Ceilometer.start()
            pass
        pass
    
    @staticmethod
    def initHorizon():
        if Role.isHorizonRole() :
            from openstack.kilo.dashboard.dashboard import Dashboard
            Dashboard.start()
            pass
        pass
    
    @staticmethod
    def initCinder():
        if Role.isCinderRole() :
            from openstack.kilo.cinder.cinder import Cinder
            Cinder.start()
        pass
    
    
    
if __name__ == '__main__':
    print 'Start to init extended controller node============'
    
    print 'start time: %s' % time.ctime()

    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/init_extended_controller'
    if not os.path.exists(INSTALL_TAG_FILE) :
        from common.lock.FileBasedLock import FileBasedLock
        file_lock = FileBasedLock(lockFilePath='/opt/openstack_conf/lock/extend_controller_lock')
        if file_lock.acquire(acquireTimeout=600) == True :
            try :
                local_mgmt_ip = YAMLUtil.getManagementIP()
                print 'start to init controller service=========='
                print 'start to init keystone====='
                ControllerServiceInit.initKeystone()
                print 'start to init glance====='
                ControllerServiceInit.initGlance()
                print 'start to init nova-api====='
                ControllerServiceInit.initNovaApi()
                print 'start to init neutron-server====='
                ControllerServiceInit.initNeutronServer()
                print 'start to init neutron-agent====='
                ControllerServiceInit.initNeutronAgent()
                print 'start to init ceilometer====='
                ControllerServiceInit.initCeilometer()
                print 'start to init horizon====='
                ControllerServiceInit.initHorizon()
                print 'start to init cinder====='
                ControllerServiceInit.initCinder()
                
                print 'start to implement lldp===='
                ####################ICBC
                from openstack.kilo.common.net import Net
                Net.implement_lldp()
                print 'done to implement lldp####'
                
                ########set hosts
                cmd = 'python /etc/puppet/fuel-python/openstack/kilo/novacompute/set_host_4controller.py {controller_ip}'.format(controller_ip=local_mgmt_ip)
                print 'cmd=%s' % cmd
                output, exitcode = ShellCmdExecutor.execCmd(cmd)
                print 'output=%s--' % output
                print 'exitcode=%s--' % exitcode
                
                os.system('touch %s' % INSTALL_TAG_FILE)
                pass
            except Exception, e :
                print 'ERROR: %s' % e
                print traceback.format_exc()
            finally: 
                file_lock.release()
                pass
            pass
        else :
            print 'There is file lock.'
            pass
        pass
    else :
        
        pass
    pass
    print 'end time: %s' % time.ctime()
    print 'done to init controller service######'
    pass





