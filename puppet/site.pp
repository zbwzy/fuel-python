$fuel_settings = parseyaml($astute_settings_yaml)
$mysql_vip = $fuel_settings['mysql']['mysql_vip']
$local_ip = $::ipaddress
$master_ip = $fuel_settings['masterip']
$installDir ='/home/app'
$role = $fuel_settings['role']
$mysql_role = $fuel_settings['mysql']


exec {"fuel_python_dir":
     path => "/usr/bin:/bin",
     command => "cp -r /etc/puppet/modules/fuel-python /etc/puppet",
}

exec {"openstack_config":
path => "/usr/bin:/bin",
command => "mkdir -p /etc/puppet/openstack_conf",
before  => Exec["openstack_yaml"],
require => Exec["fuel_python_dir"],
creates => "/tmp/test1"
}

#exec {"openstack_json":
#     path => "/usr/bin:/bin",
#     command => "cp -f /etc/puppet/fuel-python/conf/openstack_params.json /etc/puppet/openstack_conf ",
#}

exec {"openstack_yaml":
     path => "/usr/bin:/bin",
     command => "python /etc/puppet/fuel-python/common/yaml/ParamsProducer.py"
}


#########################################################
######haproxy keepalived
###########################################################
notify {"$local_ip==$master_ip":}

  case $role {
  
      'mysql' : {
          class { 'mysql_galera':
        installDir => $installDir,
       root_passwd => "123456",
        mysql_vip => $mysql_vip,
        master_ip => $master_ip,
        nodes_ip => $nodes_ip
       }
      }

      'keystone' : {
       exec{"keystone_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/keystone/keystone.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
        }
      }

      'glance' : {
       exec{"glance_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/glance/glance.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
             }

      'cinder-api' : {
        exec{"cinder_api_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/cinder/cinder.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
              }
        }

       'cinder-storage' : {
        exec{"cinder_storage_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/cinderstorage/cinderstorage.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
               }
        }

      'heat' : {
        exec{"heat_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/heat/heat.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
               }
        }
      'neutron' : {
      
        }
      'compute' : {

        }

      'rabbitmq' :
        {
      $rabbitmq_vip = $fuel_settings['rabbitmq']
      class { 'rabbitmq_clu':
        installDir => $installDir,
        guest_passwd => "123456",
        rabbitmq_vip => $rabbitmq_vip,
        master_ip => $master_ip,
            }
        }

        'horizon':
        {
           exec{"horizon_install":
           path => "/usr/bin:/bin",
           command => "python /etc/puppet/fuel-python/openstack/icehouse/dashboard/dashboard.py",
           timeout => 3600,
           require => Exec['openstack_yaml']
           }

        }

      default  :
     #   fail("Unsupported osfamily: ${osfamily} for os ${operatingsystem}")
        notify {"other $role...................................":}
      }
      }