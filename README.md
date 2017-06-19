# fuel-python
1).This project deployment dir:
/etc/puppet

2).Use real env:
In conf/openstack_env.conf:
OPENSTACK_CONF_BASE_DIR = /opt/openstack_conf

3).Before execute this project:
init openstack params, and the parameters are put into /opt/openstack_conf/openstack_params.json like below:
{
    "mysql_vip": "192.168.11.128",
    "rabbit_host": "192.168.11.128",
    "keystone_vip": "192.168.11.100",
    "keystone_ips": "192.168.11.128,192.168.11.129",
    "glance_vip" : "192.168.11.100",
    "glance_ips": "192.168.11.128,192.168.11.129",
    "nova_vip" : "192.168.11.100",
    "nova_ips": "192.168.11.128,192.168.11.129",
    "glance_vip_interface" : "eth0",
    "keystone_vip_interface" : "eth0",
    "nova_vip_interface" : "eth0"
......    
}

4).For each component python script:
debug = False

5).Prepare local ip(Management IP) on localhost:
/opt/localip


Deployment init on fuel-master:
1).On nailgun container:
Use nailgun/start.py in this project to update /opt/start.py on nailgun docker container.

2).For puppet:
Use puppet/site.pp to update /etc/puppet/manifests/site.pp.

3).For fuel-python:
Deploy this project to /etc/puppet/modules/.



how to adjust rdb when disk is mounted done
---------------------------------------------
e.g.  mount point is /apps/

1.stop rdb service:
cd /opt/bcrdb/support-files
./mysql.server stop

2. backup original rdb data:
mkdir /apps/backup
mv /opt/bcrdb/data  /apps/backup

3.adjust data and log to new disk for rdb:
mkdir /apps/bcrdb/
mkdir /apps/bcrdb/log/
cp -r /apps/backup/data /apps/bcrdb/
chown -R bcrdb:bcrdb /apps/bcrdb

4.adjust rdb conf file:
vim /opt/bcrdb/conf/my.cnf
-------
...
datadir                                = /apps/bcrdb/data
...
general_log_file                       = /apps/bcrdb/log/general.log
log_error                              = /apps/bcrdb/log/error.log
...
slow_query_log_file                    = /apps/bcrdb/log/slow.log
...

5.launch rdb:
if exist other running rdb:
------
cd /opt/bcrdb/support-files
./mysql.server start


if not exist other running rdb:
launch first rdb:
cd /opt/bcrdb/support-files
./mysql.server bootstrap

launch another rdb:
cd /opt/bcrdb/support-files
./mysql.server start
