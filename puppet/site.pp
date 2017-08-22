$fuel_settings = parseyaml($astute_settings_yaml)
$role = $fuel_settings['role']
$mysql_vip = $fuel_settings['mysql']['mysql_vip']
$local_ip = $::ipaddress
$master_ip = $fuel_settings['masterip']
$installDir ='/home/app'

stage {'zero': } ->

stage {'first': }

class {'initParam': stage => 'zero'}
class {'deploy_openstack': stage=> 'first'}


class initParam{

        exec {"fuel_python_dir":
             path => "/usr/bin:/bin:/usr/sbin",
             command => "cp -r /etc/puppet/modules/fuel-python /etc/puppet",
        }

        exec {"openstack_config":
        path => "/usr/bin:/bin:/usr/sbin",
        command => "mkdir -p /etc/puppet/openstack_conf",
        before  => Exec["prerequisites"],
        require => Exec["fuel_python_dir"],
        creates => "/tmp/test1"
        }


        exec {"prerequisites":
             path => "/usr/bin:/bin:/usr/sbin",
             command => "python /etc/puppet/fuel-python/openstack/newton/prerequisites/prerequisites.py"
        }
}


class deploy_openstack {

  notify {">>>>>>>>>>>>>?.keystone_role?.-----------------------------":}

  case $role {

      'haproxy-keepalived' : {
      exec{"ha_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/ha/HAProxyKeepalived.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
       }

      'mysql' : {
      exec{"mysql_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/mysql/bcrdb.py",
       timeout => 3600,
       require => Exec['prerequisites']
        }
       }

       'rabbitmq' : {
      exec{"rabbitmq_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/rabbitmq/rabbitmq.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
       }
      
       'keystone' : {
         exec{"keystone_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/keystone/keystone.py",
       timeout => 3600,
       require => Exec['prerequisites']
          }
       }


      'glance' : {
       exec{"glance_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/glance/glance.py",
       timeout => 3600,
       require => Exec['prerequisites']
                  }
           }
        
       'cinder-api' : {
        exec{"cinder_api_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/cinder/cinder.py",
       timeout => 3600,
       require => Exec['prerequisites']
              }
        }

       'cinder-storage' : {
        exec{"cinder_storage_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/cinderstorage/cinderstorage.py",
       timeout => 3600,
       require => Exec['prerequisites']
               }
        }
      
        'heat' : {
        exec{"heat_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/heat/heat.py",
       timeout => 3600,
       require => Exec['prerequisites']
               }
        }

       'mongodb' : {
       exec{"mongodb_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/mongodb/mongodb.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }
     
       'ceilometer' : {
       exec{"ceilometer_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/ceilometer/ceilometer.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }

      'nova-api' : {
       exec{"nova_api_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/nova/nova.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }
   
        'nova-compute' : {
       exec{"nova_compute_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/novacompute/novacompute.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }

       'neutron-server' : {
       exec{"neutron_server_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/neutronserver/neutronserver.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }

       'neutron-agent' : {
       exec{"neutron_agent_install":
       path => "/usr/bin:/bin:/usr/sbin",
       command => "python /etc/puppet/fuel-python/openstack/newton/network/network.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }
   
        'horizon':
        {
           exec{"horizon_install":
           path => "/usr/bin:/bin:/usr/sbin",
           command => "python /etc/puppet/fuel-python/openstack/newton/dashboard/dashboard.py",
           timeout => 3600,
           require => Exec['prerequisites']
           }

        }

      default  : {
     #   fail("Unsupported osfamily: ${osfamily} for os ${operatingsystem}")
            notify {"other $role...................................":}
       }
    }
}
