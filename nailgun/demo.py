'''
Created on Nov 5, 2015

@author: zhangbai
'''

from nailgun.common.ssh import Client as SSHClient

class OpenStackCmd(object):
    
    
    pass

def main():
    ip = '10.20.0.151'
    ssh_user = 'root'
    ssh_password = 'r00tme'
    key_filename = '/root/.ssh/id_rsa'
    timeout = 1000
    ssh_client = SSHClient(ip, ssh_user, ssh_password, timeout, key_filename)
    
    cmd = 'echo `date` >> /tmp/hello.txt'
    result = ssh_client.exec_command(cmd)
    
    cmd = 'service openstack-glance-api restart'
    result = ssh_client.exec_command(cmd)
    print 'start glance-api=%s--' % result
    
    cmd = 'service openstack-glance-registry restart'
    result = ssh_client.exec_command(cmd)
    print 'start glance-registry=%s--' % result

    cmd = 'service haproxy restart'
    result = ssh_client.exec_command(cmd)
    print result
    pass
    
    ## Dashboard
    #Before start
    cmd = 'setsebool -P httpd_can_network_connect on'
    result = ssh_client.exec_command(cmd)
    print result
    
    cmd = 'chown -R apache:apache /usr/share/openstack-dashboard/static'
    result = ssh_client.exec_command(cmd)
    print result
    
    cmd = 'chmod 777 /usr/share/openstack-dashboard/openstack_dashboard/local'
    result = ssh_client.exec_command(cmd)
    print result
    
    cmd = 'service httpd restart'
    result = ssh_client.exec_command(cmd)
    print result
    
    cmd = 'service memcached restart'
    result = ssh_client.exec_command(cmd)
    print result
    
    #python /etc/puppet/fuel-python/openstack/icehouse/dashboard/dashboard.py
    
    ## cinder-api
    cmd = "service openstack-cinder-api start"
    result = ssh_client.exec_command(cmd)
    print result
    
    cmd = 'service openstack-cinder-scheduler start'
    result = ssh_client.exec_command(cmd)
    print result
    
    cmd = 'service haproxy restart'
    result = ssh_client.exec_command(cmd)
    print result
    

if __name__ == '__main__':
    main()
    
    pass
