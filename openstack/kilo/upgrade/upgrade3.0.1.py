#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author yanxianghui

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author yanxianghui

DEST_VERSION='3.0.1'
import subprocess
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

def execute_cmd(cmd, customer_errmsg):
	#print(cmd)
	res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	res.wait()
	readmsg = res.stdout.read().strip()
	errormsg = res.stderr.read()

	if errormsg:
		print(errormsg)
		print(customer_errmsg)
		sys.exit()
	else:
		return readmsg

print("Start to upgrade to the version:%s..............." %(DEST_VERSION))
set_version_cmd = "echo %s > /root/VERSION" %(DEST_VERSION)
execute_cmd(set_version_cmd, "set current version error")

#add by zhangbai
def prepare():	
	current_dir = os.getcwd()
	rpm_src_path = os.path.join(current_dir, 'packages', 'bclinux7.2')
	dest_path='/var/www/nailgun/2014.2-6.0/centos'
	cp_rpms_cmd = 'cp -r %s %s' % (rpm_src_path, dest_path)
	execute_cmd(cp_rpms_cmd, 'cp rpms error')
	
	#cp comps.xml
	compsxml_src_path = os.path.join(current_dir, 'code', 'comps.xml')
	cp_compsxml_cmd = 'cp -r %s /var/www/nailgun/2014.2-6.0/centos/' % compsxml_src_path
	execute_cmd(cp_compsxml_cmd, 'cp comps.xml error')
	
	#rm old rpms
	execute_cmd('rm -rf /var/www/nailgun/2014.2-6.0/centos/bclinux7.2/', 'rm rpms error')
        
        #cp new rpms
	rpms_dir_path = os.path.join(current_dir, 'packages', 'bclinux7.2')
        cp_rpms_cmd = 'cp -r %s /var/www/nailgun/2014.2-6.0/centos/' % rpms_dir_path
	execute_cmd(cp_rpms_cmd, 'cp new rpms error')
	
	#create repo
	print 'start to create repo=========='
	execute_cmd('bash ./code/create_repo.sh','create repo error')
	print 'done create repo#####'
	
	#update fuel-python
	if os.path.exists('/etc/puppet/modules/fuel-python') :
		execute_cmd('cp -r /etc/puppet/modules/fuel-python /home/fuel-python.bak', 'backup fuel-python error')
		pass
	
	execute_cmd('rm -rf /etc/puppet/modules/fuel-python', 'rm fuel-python error')
	fuel_python_dir_path = os.path.join(current_dir,'code', 'fuel-python')
	gnocchi_dir_path = os.path.join(current_dir,'packages', 'gnocchi-with-httpd-2016-02-04.tar')
	cp_file_cmd = 'cp -r %s /etc/puppet/modules' % fuel_python_dir_path
	execute_cmd(cp_file_cmd, 'cp fuel-python error')

	cp_gnocchi_cmd = 'cp -r %s /etc/puppet/modules/ceilometer/files' % gnocchi_dir_path
	execute_cmd(cp_gnocchi_cmd, 'cp gnocchi error')
        
        extend_compute_script_path = os.path.join(current_dir,'code', 'extend_compute_node.sh')
        cp_file_cmd = 'cp -r %s /root/rm_node' % extend_compute_script_path
        execute_cmd(cp_file_cmd, 'cp extend_compute_script_path error')
	pass

def upgrade_ostf():
	ostfcmd="docker inspect -f '{{.ID}}' fuel-core-6.0-ostf"
	ostferrmsg="Get ostf container id failure."
	ostfcid = execute_cmd(ostfcmd, ostferrmsg)
	ostfPythonPwd = "/var/lib/docker/devicemapper/mnt/%s/rootfs/usr/lib/python2.6/site-packages" % (ostfcid,)
	
	mv_ostf_cmd = "rm -fr %s/fuel_health" %(ostfPythonPwd,)
	mverrmsg = "rm fuel_health dir in ostf docker container failure." 
	execute_cmd(mv_ostf_cmd, mverrmsg)
	
	cp_ostf_cmd= "cp -r code/fuel_health %s/" %(ostfPythonPwd,)
	cperrmsg = "cp fuel_health to ostf docker failure." 
	execute_cmd(cp_ostf_cmd, cperrmsg)
	
	restart_ostf_cmd = "docker restart %s" %(ostfcid,)
	execute_cmd(restart_ostf_cmd, "restart ostf docker failure.") 
	pass

prepare()

##################upgrade ostf
upgrade_ostf()
############


cmd="docker inspect -f '{{.ID}}' fuel-core-6.0-nailgun"
cobblercmd="docker inspect -f '{{.ID}}' fuel-core-6.0-cobbler"

nailgunerrmsg="Get nailgun container id failure."
cobblererrmsg="Get cobbler container id failure."
nailguncid = execute_cmd(cmd, nailgunerrmsg)
cobblercid = execute_cmd(cobblercmd,cobblererrmsg)

nailgunPythonPwd = "/var/lib/docker/devicemapper/mnt/%s/rootfs/usr/lib/python2.6/site-packages" % (nailguncid,)
nailgunOptPwd= "/var/lib/docker/devicemapper/mnt/%s/rootfs/opt/"  % (nailguncid,)
kickstartPwd = "/var/lib/docker/devicemapper/mnt/%s/rootfs/var/lib/cobbler/kickstarts" %(cobblercid,)


cpstartpycmd ="cp -r code/start.py %s" %(nailgunOptPwd)
execute_cmd(cpstartpycmd, "cp start.py to nailgun docker failure.") 

cpkickstartcmd="cp -r code/bclinux7.2.ks %s" % (kickstartPwd,)
execute_cmd(cpkickstartcmd, "cp bclinux7.2.ks to cobbler failure.") 

chmodcmd ="chmod 777 %s/bclinux7.2.ks" %(kickstartPwd,)
execute_cmd(chmodcmd, "chmod bclinux7.2.ks 777 failure.") 


restartcobblercmd = "docker restart %s" %(cobblercid,)
execute_cmd(restartcobblercmd, "restart cobbler docker failure.") 
print "start to upgrade nailgun......."

mvcmd = "rm -fr %s/nailgun" %(nailgunPythonPwd,)
mverrmsg = "rm nailgun dir in nailgun docker container failure." 
execute_cmd(mvcmd, mverrmsg)

cpcmd= "cp -r code/nailgun %s/" %(nailgunPythonPwd,)
cperrmsg = "cp nailgun to nailgun docker failure." 
execute_cmd(cpcmd, cperrmsg)
print "upgrade nailgun done#####"

print "start to upgrade static......"
static_cmd="docker inspect -f '{{.Volumes}}' fuel-core-6.0-nailgun | awk '{printf(\"%s\\n\", $5);}'"
restr = execute_cmd(static_cmd, "find static dir error")
reslist=restr.split(":")
if len(reslist)>=2:
	delcmd = "rm -fr %s/*" % (reslist[1])
	cpcmd = "cp -r code/static/* %s" % (reslist[1])
	execute_cmd(delcmd, "del static error.")
	execute_cmd(cpcmd, "cp static error.")
else:
	print("cp static error.")
	sys.exit()

print "upgrade static done####"
print "upgrade database..........."

if os.path.exists('/usr/lib/python2.6/site-packages/sqlalchemy'):
	print("Current node has installed sqlalchemy,skip...")
else:
	sqlalchemycmd = "cp -r packages/sqlalchemy /usr/lib/python2.6/site-packages"
	execute_cmd(sqlalchemycmd, "error to install sqlalchemy.")

	pg2cmd = "cp -r packages/psycopg2 /usr/lib/python2.6/site-packages"
	execute_cmd(pg2cmd, "error to install database driver psycopg2.")

import json
import yaml
from sqlalchemy import create_engine

fr = open('/etc/fuel/astute.yaml', 'r')
data = yaml.load(fr)
dbpassword=data["postgres"]["nailgun_password"]
fr.close()
engine = create_engine("postgresql://nailgun:{0}@127.0.0.1:5432/nailgun".format(dbpassword),client_encoding="utf-8")

null=None
true =True
false=False

#dynamically fix updatecon and sqlcmd,can upgrade the database
updatecon={"bonding": {"availability": [{"linux": "settings:storage.iser.value == false and settings:neutron_mellanox.plugin.value != ''ethernet''"}, {"ovs": "false"}], "properties": {"linux": {"lacp_rate": [{"for_modes": ["802.3ad"], "values": ["slow", "fast"]}], "mode": [{"values": ["balance-rr", "active-backup", "802.3ad"]}, {"values": ["balance-xor", "broadcast", "balance-tlb", "balance-alb"], "condition": "''experimental'' in version:feature_groups"}], "xmit_hash_policy": [{"for_modes": ["802.3ad", "balance-xor", "balance-tlb", "balance-alb"], "values": ["layer2", "layer2+3", "layer3+4", "encap2+3", "encap3+4"]}]}}}, "nova_network": {"config": {"floating_ranges": [["172.16.0.128", "172.16.0.254"]], "net_manager": "FlatDHCPManager", "fixed_networks_vlan_start": 103, "fixed_networks_amount": 1, "fixed_network_size": 256, "fixed_networks_cidr": "10.0.0.0/16"}, "networks": [{"name": "public", "notation": "ip_ranges", "render_type": null, "map_priority": 1, "assign_vip": true, "use_gateway": false, "vlan_start": null, "render_addr_mask": "public", "cidr": "172.16.0.0/24", "configurable": true, "gateway": "172.16.0.1", "ip_range": ["172.16.0.2", "172.16.0.127"]}, {"name": "management", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": true, "use_gateway": false, "vlan_start": 101, "render_addr_mask": "internal", "cidr": "192.168.0.0/24", "configurable": true}, {"name": "storage", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": false, "use_gateway": false, "vlan_start": 102, "render_addr_mask": "storage", "cidr": "192.168.1.0/24", "configurable": true}, {"ext_net_data": ["fixed_networks_vlan_start", "fixed_networks_amount"], "name": "fixed", "notation": null, "render_type": null, "map_priority": 2, "assign_vip": false, "use_gateway": false, "vlan_start": null, "render_addr_mask": null, "configurable": false}]}, "neutron": {"config": {"parameters": {"metadata": {"metadata_proxy_shared_secret": ""}, "keystone": {"admin_user": null, "admin_password": ""}, "amqp": {"username": null, "passwd": "", "hosts": "hostname1:5672, hostname2:5672", "provider": "rabbitmq"}, "database": {"username": null, "passwd": "", "database": null, "port": "3306", "provider": "mysql"}}, "internal_cidr": "192.168.111.0/24", "internal_gateway": "192.168.111.1", "floating_ranges": [["172.16.0.130", "172.16.0.254"]], "external_gateway": "172.16.0.1", "base_mac": "fa:16:3e:00:00:00", "gre_id_range": [2, 65535], "vlan_range": [1000, 1010]}, "networks": [{"name": "public", "notation": "cidr", "render_type": "cidr", "map_priority": 1, "assign_vip": true, "use_gateway": false, "vlan_start": 100, "render_addr_mask": "public", "cidr": "192.168.2.0/24", "configurable": true}, {"name": "management", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": true, "use_gateway": false, "vlan_start": 101, "render_addr_mask": "internal", "cidr": "192.168.0.0/24", "configurable": true}, {"name": "storage", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": false, "use_gateway": false, "vlan_start": 102, "render_addr_mask": "storage", "cidr": "192.168.1.0/24", "configurable": true}]}}
updatecon=json.dumps(updatecon)
sqlcmd1="update releases set networks_metadata='{0}'".format(updatecon)
engine.execute(sqlcmd1)


restartnailguncmd = "docker restart %s" %(nailguncid,)
execute_cmd(restartnailguncmd, "restart nailgun docker failure.")

print "Upgrade done.You should wait just several mins, then refresh the browser."
