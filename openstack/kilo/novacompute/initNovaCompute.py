'''
Created on Oct 18, 2015

@author: zhangbai
'''

'''
usage:

python cinder.py

NOTE: the params is from conf/openstack_params.json, this file is initialized when user drives FUEL to install env.
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

OPENSTACK_VERSION_TAG = 'kilo'
OPENSTACK_CONF_FILE_TEMPLATE_DIR = os.path.join(PROJ_HOME_DIR, 'openstack', OPENSTACK_VERSION_TAG, 'configfile_template')
SOURCE_NOVA_API_CONF_FILE_TEMPLATE_PATH = os.path.join(OPENSTACK_CONF_FILE_TEMPLATE_DIR,'nova', 'nova.conf')

sys.path.append(PROJ_HOME_DIR)


from common.shell.ShellCmdExecutor import ShellCmdExecutor
from common.json.JSONUtil import JSONUtility
from common.properties.PropertiesUtil import PropertiesUtility
from common.file.FileUtil import FileUtil

from openstack.kilo.novacompute.novacompute import NovaCompute
from openstack.kilo.ssh.SSH import SSH
    
if __name__ == '__main__':
    print 'hello openstack-kilo:nova-compute============'
    print 'start time: %s' % time.ctime()
    #when execute script,exec: python <this file absolute path>
    ###############################
    INSTALL_TAG_FILE = '/opt/openstack_conf/tag/install/init_novacompute'
    if os.path.exists(INSTALL_TAG_FILE) :
        print 'nova-compute initted####'
        print 'exit===='
        pass
    else :
        NovaCompute.start()
        
        #add ssh mutual trust for nova user
        if NovaCompute.getServerIndex() == 0 :
            NovaCompute.sshMutualTrust()
            NovaCompute.sshNovaUserTrust()
            pass
        else :
            nova_compute_params_dict = JSONUtility.getRoleParamsDict('nova-compute')
            nova_compute_ip_list = nova_compute_params_dict['mgmt_ips']
            src_ip = nova_compute_ip_list[0]
            if len(nova_compute_ip_list) > 1 :
                NovaCompute.scpSSHNovaTrustFiles(src_ip)
                pass
            
        #start ceilometer compute
#         ShellCmdExecutor.execCmd('systemctl enable openstack-ceilometer-compute.service')
#         ShellCmdExecutor.execCmd('systemctl restart openstack-ceilometer-compute.service')
        
        #open limits of file & restart always
        from common.openfile.OpenFile import OpenFile
        OpenFile.execModification('/usr/lib/systemd/system', 'openstack-nova-compute')
#         OpenFile.execModification('/usr/lib/systemd/system', 'openstack-ceilometer-compute')
        
        ####################ICBC
        from openstack.kilo.neutronserver.neutronserver import NeutronServer
        from openstack.kilo.common.net import Net
        Net.implement_lldp()
#         Net.rmBusinessNet()
        ####################ICBC
        #mark: nova-compute is installed
        os.system('touch %s' % INSTALL_TAG_FILE)
    print 'hello nova-compute kilo#######'
    pass

