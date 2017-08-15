# WHAT TO DO (install fresh system rather than upgrade)
# Install OS instead of upgrade
install

# INSTALLATION SOURCE (centos repository)
# Use network installation
url --url=$tree
#if $varExists('repo_metadata')
# REPOSITORIES FROM Nailgun
## Expected repo_metadata format Name1=Value1,Name2=Value2
#set repo_list = dict(item.split("=") for item in $repo_metadata.split(","))
#for $repo_name, $repo_url in $repo_list.items()
repo --name=$repo_name --baseurl=$repo_url
#end for
#else
# ALTERNATIVE REPOSITORIES (PRESET)

repo --name=Nailgun --baseurl=$tree

#end if

# KEYBOARD AND LANGUAGE CUSTOMIZATION
lang en_US.UTF-8
keyboard us

# WHICH TIMEZONE TO USE ON INSTALLED SYSTEM
timezone --utc Etc/UTC

# REBOOT AFTER INSTALLATION
reboot

# Firewall configuration
firewall --disable

# Clear the Master Boot Record
zerombr

# SET ROOT PASSWORD DEFAULT IS r00tme
rootpw --iscrypted $6$tCD3X7ji$1urw6qEMDkVxOkD33b4TpQAjRiCeDZx0jmgMhDYhfB9KuGfqO9OcMaKyUxnGGWslEDQ4HxTw7vcAMP85NxQe61


# AUTHENTICATION CUSTOMIZATION
authconfig --enableshadow --passalgo=sha512

# DISABLE SELINUX ON INSTALLED SYSTEM
selinux --disabled

# INSTALL IN TEXT MODE
text

# Do not configure the X Window System
skipx

# Suppress "unsupported hardware" warning
unsupported_hardware

# SSH user and some unknown random password,
# we're going to use SSH keys anyway
sshpw --username root --iscrypted $6$tCD3X7ji$1urw6qEMDkVxOkD33k2jjklHSDG2hg2234kJHESJ3hwhsjHshSJshHSJSh333je34DHJHDr4je4AMP85NxQe61

%include /tmp/partition.ks

# COBBLER EMBEDDED SNIPPET: 'network_config'
# CONFIGURES NETWORK INTERFACES DEPENDING ON
# COBBLER SYSTEM PARAMETERS
$SNIPPET('network_config')

# PREINSTALL SECTION
# HERE ARE COMMANDS THAT WILL BE LAUNCHED BEFORE
# INSTALLATION PROCESS ITSELF
%pre

# COBBLER EMBEDDED SNIPPET: 'log_ks_pre'
# CONFIGURES %pre LOGGING
$SNIPPET('log_ks_pre')

# DOWNLOADS send2syslog.py AND LAUNCHES IT
# IN ORDER TO MONITOR LOG FILES AND SEND
# LINES FROM THOSE FILES TO SYSLOG
$SNIPPET('send2syslog')

# SNIPPET: 'kickstart_ntp'
# SYNC LOCAL TIME VIA NTP
$SNIPPET('kickstart_ntp')

# COBBLER EMBEDDED SNIPPET: 'kickstart_start'
# LAUNCHES %pre TRIGGERS IF THOSE INSTALLED
$SNIPPET('kickstart_start')

# COBBLER EMBEDDED SNIPPET: 'pre_install_network_config'
# PRECONFIGURES NETWORK INTERFACES DEPENDING ON
# COBBLER SYSTEM PARAMETERS
# IN PARTICULAR IT WRITES KICKSTART NETWORK CONFIGURATION
# INTO /tmp/pre_install_network_config WHICH IS INCLUDED
# INTO KICKSTART BY 'network_config' SNIPPET
$SNIPPET('pre_install_network_config')

# CONFIGURES SSH KEY ACCESS FOR SSHD CONSOLE
# DURING OPERATING SYSTEM INSTALLATION
$SNIPPET('anaconda_ssh_console')

# COBBLER EMBEDDED SNIPPET: 'pre_install_partition'
# DETECTS HARD DRIVES AND SETS FIRST OF THEM
# AS INSTALLATION TARGET AND BOOTLOADER INSTALLATION TARGET
$SNIPPET('pre_install_partition_lvm_new')

# CONFIGURE ANACONDA YUM SETTINGS
$SNIPPET('anaconda-yum')

%end

# PACKAGES SECTION
# HERE ARE LIST OF PACKAGES THAT WILL BE INSTALLED
# FIXME --ignoremissing
%packages --nobase --ignoremissing
$SNIPPET('centos_pkg_kernel_lt_if_enabled')
authconfig
bind-utils
cronie
crontabs
curl
gcc
gdisk
make
mlocate
nmap-ncat
ntp
openssh
openssh-clients
openssh-server
perl
rsync
system-config-firewall-base
tcpdump
telnet
virt-what
vim
wget
yum
yum-utils
parted
expect

# fuel packages
bfa-firmware
daemonize
libselinux-ruby
ruby
ruby-augeas
ruby-devel
rubygem-netaddr
ruby21-rubygem-openstack

rubygem-cstruct
rubygem-mixlib-log
rubygem-mixlib-config
rubygem-mixlib-cli
rubygem-yajl-ruby
nailgun-agent

nailgun-mcagents

nailgun-net-check


# COBBLER EMBEDDED SNIPPET: 'centos_ofed_prereq_pkgs_if_enabled'
# LISTS ofed prereq PACKAGES IF mlnx_plugin_mode VARIABLE IS SET TO enabled
$SNIPPET('centos_ofed_prereq_pkgs_if_enabled')

# COBBLER EMBEDDED SNIPPET: 'puppet_install_if_enabled'
# LISTS puppet PACKAGE IF puppet_auto_setup VARIABLE IS SET TO 1
$SNIPPET('puppet_install_if_enabled')

# COBBLER EMBEDDED SNIPPET: 'mcollective_install_if_enabled'
# LISTS mcollective PACKAGE IF mco_auto_setup VARIABLE IS SET TO 1
$SNIPPET('mcollective_install_if_enabled')

%end

# POST INSTALLATION PARTITIONING
# THERE ARE SOME COMMANDS TO CREATE LARGE (>1TB) VOLUMES
# AND INSTALL GRUB BOOTLOADER TO MAKE NODES ABLE TO BOOT FROM ANY HARDDRIVE
%include /tmp/post_partition.ks

# POSTINSTALL SECTION
# HERE ARE COMMANDS THAT WILL BE LAUNCHED JUST AFTER
# INSTALLATION ITSELF COMPLETED
%post
yum-config-manager --disableplugin=fastestmirror --save &>/dev/null

echo -e "modprobe nf_conntrack_ipv4\nmodprobe nf_conntrack_ipv6" >> /etc/rc.modules
chmod +x /etc/rc.modules
echo -e "net.nf_conntrack_max=1048576" >> /etc/sysctl.conf
mkdir -p /var/log/coredump
echo -e "kernel.core_pattern=/var/log/coredump/core.%e.%p.%h.%t" >> /etc/sysctl.conf
chmod 777 /var/log/coredump
echo -e "* soft core unlimited\n* hard core unlimited" >> /etc/security/limits.conf
sed -i '/\*.*soft.*nproc.*1024$/s/1024/10240/' /etc/security/limits.d/90-nproc.conf

# COBBLER EMBEDDED SNIPPET: 'log_ks_post'
# CONFIGURES %post LOGGING
$SNIPPET('log_ks_post')

# COBBLER EMBEDDED SNIPPET: 'post_install_kernel_options'
# CONFIGURES KERNEL PARAMETERS ON INSTALLED SYSTEM
$SNIPPET('post_install_kernel_options')

# COBBLER EMBEDDED SNIPPET: 'post_install_network_config'
# CONFIGURES NETWORK INTERFACES DEPENDING ON
# COBBLER SYSTEM PARAMETERS
$SNIPPET('post_install_network_config_fuel')

# COBBLER EMBEDDED SNIPPET: 'puppet_conf'
# CONFIGURES PUPPET AGENT
$SNIPPET('puppet_conf')

# COBBLER EMBEDDED SNIPPET: 'puppet_register_if_enabled'
# CREATES CERTIFICATE REQUEST AND SENDS IT TO PUPPET MASTER
$SNIPPET('puppet_register_if_enabled_fuel')

# COBBLER EMBEDDED SNIPPET: 'mcollective_conf'
# CONFIGURES MCOLLECTIVE AGENT
$SNIPPET('mcollective_conf')

# COBBLER EMBEDDED SNIPPET: 'python_pip_conf'
# CONFIGURES PYTHON_PIP
# SNIPPET('python_pip_conf')

# SNIPPET: 'kickstart_ntp'
# SYNC LOCAL TIME VIA NTP
$SNIPPET('kickstart_ntp')

# SNIPPET: 'ntp_to_masternode'
# CONFIGURES NTPD POOL TO MASTER NODE
$SNIPPET('ntp_to_masternode')

# Let's not to use separate snippet for just one line of code. Complexity eats my time.
chmod +x /etc/rc.d/rc.local
echo 'flock -w 60 -o /var/lock/nailgun-agent.lock -c "/usr/bin/nailgun-agent >> /var/log/nailgun-agent.log 2>&1"' >> /etc/rc.local
echo '* * * * * root flock -w 60 -o /var/lock/nailgun-agent.lock -c "/usr/bin/nailgun-agent 2>&1 | tee -a /var/log/nailgun-agent.log  | /usr/bin/logger -t nailgun-agent"' > /etc/cron.d/nailgun-agent

# It is for the internal nailgun using
echo target > /etc/nailgun_systemtype

# COBBLER EMBEDDED SNIPPET: 'authorized_keys'
# PUTS authorized_keys file into /root/.ssh/authorized_keys
$SNIPPET('centos_authorized_keys')

# COBBLER EMBEDDED SNIPPET: 'nailgun_repo'
# REMOVES ALL *.repo FILES FROM /etc/yum.repos.d AND
# CREATES /etc/yum.repos.d/nailgun.repo FILE AND
# PUTS IN IT ALL THE REPOSITORIES DEFINED IN ks_repo VARIABLE
$SNIPPET('nailgun_repo')



mkdir -p /etc/nailgun-agent/
cat > /etc/nailgun-agent/config.yaml << EOA
---
url: 'http://@@server@@:8000/api'
EOA

# COBBLER EMBEDDED SNIPPET: 'kernel_lt_if_enabled'
# INSTALLS kernel-lt PACKAGE IF kernel_lt VARIABLE IS SET TO 1
$SNIPPET('centos_post_kernel_lt_if_enabled')

# COBBLER EMBEDDED SNIPPET: 'ssh_disable_gssapi'
# REMOVES "GSSAPICleanupCredentials yes" AND "GSSAPIAuthentication yes" LINES
# FROM /etc/ssh/sshd_config
$SNIPPET('ssh_disable_gssapi')

# COBBLER EMBEDDED SNIPPET: 'redhat_register'
# REGISTER AT REDHAT WITH ACTIVATION KEY
$SNIPPET('red_hat_register_satellite')
# REGISTER TO RED HAT SUBSCRIPTION MANAGER WITH LOGIN/PASSWORD
$SNIPPET('red_hat_register_rhsm')

# Let's not wait forewer when ssh'ing:
sed -i --follow-symlinks -e '/UseDNS/d' /etc/ssh/sshd_config
echo 'UseDNS no' >> /etc/ssh/sshd_config

# COBBLER EMBEDDED SNIPPET: 'sshd_auth_pubkey_only'
# DISABLE PASSWORD AUTH. ALLOW PUBKEY AUTH ONLY IN /etc/ssh/sshd_config
# SNIPPET('sshd_auth_pubkey_only')

# Copying default bash settings to the root directory
cp -f /etc/skel/.bash* /root/

# Rsyslogd should send all messages to master node
$SNIPPET('target_logs_to_master')

# Configure static IP address for admin interface
$SNIPPET('centos_static_net_new')

# Blacklist i2c_piix4 module so it does not create kernel errors
$SNIPPET('centos_blacklist_i2c_piix4')

# Install OFED components for RDMA if needed
$SNIPPET('ofed_install_with_sriov')

# ===================
# = fuel other conf =
# ===================
sed -i '/^nameserver/d' /etc/resolv.conf

# EBS conf
sed -i 's/^Defaults    requiretty/# Defaults    requiretty/' /etc/sudoers

# run nj-BugFix
wget "http://@@server@@/cobbler/aux/nj-BugFix.sh" -O /root/nj-BugFix.sh
sh /root/nj-BugFix.sh > /root/nj-BugFix.log 2>&1

# add by zhangbai
#set mysql_disk = "sdb" 

# Parted disk
#if $mysql_disk != ""
#set disktype = "/dev/" + $mysql_disk
wget "http://@@server@@/cobbler/aux/create_mysql_lv.sh" -O /tmp/create_mysql_lv.sh
wget "http://@@server@@/cobbler/aux/create_influxdb_lv.sh" -O /tmp/create_influxdb_lv.sh
if [ -e $disktype ];then
	echo "parted start...."

	/sbin/parted -s $disktype mklabel gpt
	maxsize=`/sbin/parted -s $disktype print | grep $disktype | awk '{print $3}'`
	echo "Log---> disk $disktype size: $maxsize"

	number=`echo $maxsize | awk -F'[.GB]' '{print $1}'`

        if [ $number -gt 600 ]; then
		echo "Log---> start parted ${disktype}"
		dd if=/dev/zero of=$disktype bs=1M count=10
		/sbin/parted -s $disktype mklabel gpt
		/sbin/parted -s $disktype mkpart primary 1 $maxsize
		sleep 10

		pvcreate ${disktype}1
		vgcreate dbvg ${disktype}1
		vgchange -ay dbvg

		echo "Log---> Create mysql lv"

		expect /tmp/create_mysql_lv.sh

		mkfs.ext4 /dev/mapper/dbvg-mysql_lv
		mkdir -p /var/lib/mysql
		mount /dev/mapper/dbvg-mysql_lv /var/lib/mysql
		uuid_mysql=UUID=`blkid | grep /dev/mapper/dbvg-mysql_lv | awk -F'"' '{print $2}'`
		echo $uuid_mysql /var/lib/mysql ext4 defaults 0 0 >> /etc/fstab

		echo "Log---> Create influxdb lv"

		expect /tmp/create_influxdb_lv.sh

		mkfs.ext4 /dev/mapper/dbvg-influxdb_lv
		mkdir -p /var/lib/influxdb
		mount /dev/mapper/dbvg-influxdb_lv /var/lib/influxdb
		uuid_influxdb=UUID=`blkid | grep /dev/mapper/dbvg-influxdb_lv | awk -F'"' '{print $2}'`
		echo $uuid_influxdb /var/lib/influxdb ext4 defaults 0 0 >> /etc/fstab

	fi

	echo "parted finish..."
fi
#end if

# =======
# = end =
# =======

# COBBLER EMBEDDED SNIPPET: 'kickstart_done'
# DISABLES PXE BOOTING
$SNIPPET('kickstart_done')

%end
