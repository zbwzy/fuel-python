# System default settings live in /usr/lib/sysctl.d/00-system.conf.
# To override those settings, enter new settings here, or in an /etc/sysctl.d/<name>.conf file
#
# For more information, see sysctl.conf(5) and sysctl.d(5).
net.nf_conntrack_max=1048576
kernel.core_pattern=/var/log/coredump/core.%e.%p.%h.%t
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1

net.bridge.bridge-nf-call-iptables=1
net.ipv4.ip_nonlocal_bind=1
net.nf_conntrack_max=1048576
net.ipv4.tcp_keepalive_intvl=3
net.ipv4.tcp_keepalive_time=45
net.ipv4.tcp_keepalive_probes=8
net.ipv4.tcp_retries2=5
net.ipv4.conf.all.accept_redirects=0

net.ipv4.ip_forward = 1
net.ipv4.conf.default.rp_filter = 0
net.ipv4.conf.default.send_redirects=0
net.ipv4.conf.default.accept_redirects=0
