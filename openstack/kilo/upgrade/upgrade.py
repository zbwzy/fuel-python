#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author yanxianghui

DEST_VERSION='3.0.2'
import subprocess
import sys
import os

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
	rm_guardian_cmd='rm -rf /var/www/nailgun/2014.2-6.0/centos/bclinux7.2/Packages/bigcloud/2016.01/ec3.6.1/x86_64/openstack/Packages/bc-ec/guardian-*'
	execute_cmd(rm_guardian_cmd, 'rm guardian error')
	current_dir = os.getcwd()
	guardian_src_path = os.path.join(current_dir, 'packages', 'guardian-1.0.1.dev26-1.noarch.rpm')
	dest_path='/var/www/nailgun/2014.2-6.0/centos/bclinux7.2/Packages/bigcloud/2016.01/ec3.6.1/x86_64/openstack/Packages/bc-ec/'
	cp_guardian_cmd = 'cp -r %s %s' % (guardian_src_path, dest_path)
	execute_cmd(cp_guardian_cmd, 'cp guardian error')
	
	#cp comps.xml
	compsxml_src_path = os.path.join(current_dir, 'code', 'comps.xml')
	cp_compsxml_cmd = 'cp -r %s /var/www/nailgun/2014.2-6.0/centos/' % compsxml_src_path
	execute_cmd(cp_compsxml_cmd, 'cp comps.xml error')
	
	#rm old repodata
	execute_cmd('rm -rf /var/www/nailgun/2014.2-6.0/centos/bclinux7.2/repodata', 'rm error')
	
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
	cp_file_cmd = 'cp -r %s /etc/puppet/modules' % fuel_python_dir_path
	execute_cmd(cp_file_cmd, 'cp fuel-python error')
	pass

prepare()

cmd="docker inspect -f '{{.ID}}' fuel-core-6.0-nailgun"
cobblercmd="docker inspect -f '{{.ID}}' fuel-core-6.0-cobbler"

nailgunerrmsg="获取nailgun的容器id失败,升级失败......"
nailguncid = execute_cmd(cmd, nailgunerrmsg)
cobblercid = execute_cmd(cobblercmd,"获取cobbler容器ID失败")

nailgunPythonPwd = "/var/lib/docker/devicemapper/mnt/%s/rootfs/usr/lib/python2.6/site-packages" % (nailguncid,)
nailgunOptPwd= "/var/lib/docker/devicemapper/mnt/%s/rootfs/opt/"  % (nailguncid,)
kickstartPwd = "/var/lib/docker/devicemapper/mnt/%s/rootfs/var/lib/cobbler/kickstarts" %(cobblercid,)
cobblershellPwd = "/var/lib/docker/devicemapper/mnt/%s/rootfs/var/www/cobbler/aux" %(cobblercid,)

cpstartpycmd ="cp -r code/start.py %s" %(nailgunOptPwd)
execute_cmd(cpstartpycmd, "复制start.py到opt目录下失败")

cpkickstartcmd="cp -r code/bclinux7.2.ks %s" %(kickstartPwd,)
execute_cmd(cpkickstartcmd, "复制bclinux7.2.ks出现异常")

chmodcmd ="chmod 777 %s/bclinux7.2.ks" %(kickstartPwd,)
execute_cmd(chmodcmd, "chmod bclinux7.2 出现异常")

cpinfluxdbshcmd ="cp -r code/create_influxdb_lv.sh %s" %(cobblershellPwd,)
execute_cmd(cpinfluxdbshcmd, "复制create_influxdb_lv.sh出现异常")

chmodinfluxdb="chmod 777 %s/create_influxdb_lv.sh" %(cobblershellPwd,)
execute_cmd(chmodinfluxdb, "chmod create_influxdb_lv.sh出现异常")

cpmysqldbshellcmd = "cp -r code/create_mysql_lv.sh %s" %(cobblershellPwd,)
execute_cmd(cpmysqldbshellcmd, "复制create_mysql_lv.sh出现异常")

chmodmysqlshellcmd = "chmod 777 %s/create_mysql_lv.sh" %(cobblershellPwd,)
execute_cmd(chmodmysqlshellcmd, "chmod create_mysql_lv.sh出现异常")

restartcobblercmd = "docker restart %s" %(cobblercid,)
execute_cmd(restartcobblercmd, "重启cobbler容器出现异常")

mvcmd = "rm -fr %s/nailgun" %(nailgunPythonPwd,)
mverrmsg = "删除原来的nailgun文件夹失败....."
execute_cmd(mvcmd, mverrmsg)

cpcmd= "cp -r code/nailgun %s/" %(nailgunPythonPwd,)
cperrmsg = "复制最新nailgun目录失败...."
execute_cmd(cpcmd, cperrmsg)

print("nailgun升级成功,开始升级static文件................")
static_cmd="docker inspect -f '{{.Volumes}}' fuel-core-6.0-nailgun | awk '{printf(\"%s\\n\", $5);}'"
restr = execute_cmd(static_cmd, "")
reslist=restr.split(":")
if len(reslist)>=2:
	delcmd = "rm -fr %s/*" % (reslist[1])
	cpcmd = "cp -r code/static/* %s" % (reslist[1])
	execute_cmd(delcmd, "删除原来static文件失败")
	execute_cmd(cpcmd, "更新static文件夹失败......")
else:
	print("查找static目录失败..........")
	sys.exit()
print("static目录升级成功,开始升级database............")

if os.path.exists('/usr/lib/python2.6/site-packages/sqlalchemy'):
	print("当前节点上已经安装sqlalchemy,自动跳过安装步骤....")
else:
	sqlalchemycmd = "cp -r packages/sqlalchemy /usr/lib/python2.6/site-packages"
	execute_cmd(sqlalchemycmd, "安装sqlalchemy模块失败")

	pg2cmd = "cp -r packages/psycopg2 /usr/lib/python2.6/site-packages"
	execute_cmd(pg2cmd, "安装数据库驱动模块失败")

	#如果master上没有yaml模块才进行安装,有则无需进行安装
	#yamlcmd = "cp -r packages/yaml /usr/lib/python2.6/site-pakages"
	#execute_cmd(yamlcmd,"安装yaml模块失败")

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

#只需要动态修改updatecon和sqlcmd即可实现数据库不同功能的升级
updatecon={"bonding": {"availability": [{"linux": "settings:storage.iser.value == false and settings:neutron_mellanox.plugin.value != ''ethernet''"}, {"ovs": "false"}], "properties": {"linux": {"lacp_rate": [{"for_modes": ["802.3ad"], "values": ["slow", "fast"]}], "mode": [{"values": ["balance-rr", "active-backup", "802.3ad"]}, {"values": ["balance-xor", "broadcast", "balance-tlb", "balance-alb"], "condition": "''experimental'' in version:feature_groups"}], "xmit_hash_policy": [{"for_modes": ["802.3ad", "balance-xor", "balance-tlb", "balance-alb"], "values": ["layer2", "layer2+3", "layer3+4", "encap2+3", "encap3+4"]}]}}}, "nova_network": {"config": {"floating_ranges": [["172.16.0.128", "172.16.0.254"]], "net_manager": "FlatDHCPManager", "fixed_networks_vlan_start": 103, "fixed_networks_amount": 1, "fixed_network_size": 256, "fixed_networks_cidr": "10.0.0.0/16"}, "networks": [{"name": "public", "notation": "ip_ranges", "render_type": null, "map_priority": 1, "assign_vip": true, "use_gateway": false, "vlan_start": null, "render_addr_mask": "public", "cidr": "172.16.0.0/24", "configurable": true, "gateway": "172.16.0.1", "ip_range": ["172.16.0.2", "172.16.0.127"]}, {"name": "management", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": true, "use_gateway": true, "vlan_start": 101, "render_addr_mask": "internal", "cidr": "192.168.0.0/24", "configurable": true}, {"name": "storage", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": false, "use_gateway": false, "vlan_start": 102, "render_addr_mask": "storage", "cidr": "192.168.1.0/24", "configurable": true}, {"ext_net_data": ["fixed_networks_vlan_start", "fixed_networks_amount"], "name": "fixed", "notation": null, "render_type": null, "map_priority": 2, "assign_vip": false, "use_gateway": false, "vlan_start": null, "render_addr_mask": null, "configurable": false}]}, "neutron": {"config": {"parameters": {"metadata": {"metadata_proxy_shared_secret": ""}, "keystone": {"admin_user": null, "admin_password": ""}, "amqp": {"username": null, "passwd": "", "hosts": "hostname1:5672, hostname2:5672", "provider": "rabbitmq"}, "database": {"username": null, "passwd": "", "database": null, "port": "3306", "provider": "mysql"}}, "internal_cidr": "192.168.111.0/24", "internal_gateway": "192.168.111.1", "floating_ranges": [["172.16.0.130", "172.16.0.254"]], "external_gateway": "172.16.0.1", "base_mac": "fa:16:3e:00:00:00", "gre_id_range": [2, 65535], "vlan_range": [1000, 1010]}, "networks": [{"name": "public", "notation": "cidr", "render_type": "cidr", "map_priority": 1, "assign_vip": true, "use_gateway": false, "vlan_start": 100, "render_addr_mask": "public", "cidr": "192.168.2.0/24", "configurable": true}, {"name": "management", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": true, "use_gateway": true, "vlan_start": 101, "render_addr_mask": "internal", "cidr": "192.168.0.0/24", "configurable": true}, {"name": "storage", "notation": "cidr", "render_type": "cidr", "map_priority": 2, "assign_vip": false, "use_gateway": false, "vlan_start": 102, "render_addr_mask": "storage", "cidr": "192.168.1.0/24", "configurable": true}]}}
updatecon=json.dumps(updatecon)
sqlcmd1="update releases set networks_metadata='{0}'".format(updatecon)
engine.execute(sqlcmd1)

sqlcmd2="ALTER TABLE nodes add user_set text DEFAULT '{\"mysql_disk\":\"\"}'"
engine.execute(sqlcmd2)

restartnailguncmd = "docker restart %s" %(nailguncid,)
execute_cmd(restartnailguncmd, "重启nailgun容器失败")

print("恭喜,升级命令全部成功执行完毕,由于重启服务需要几分钟时间,请你耐心等待下再刷新浏览器！")






