$fuel_settings = parseyaml($astute_settings_yaml)
$mysql_vip = $fuel_settings['mysql']['mysql_vip']
$local_ip = $::ipaddress
$master_ip = $fuel_settings['masterip']
$nodes_ip = '10.20.0.3,10.20.0.4'
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
      exec{"keystone_init":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/keystone/keystone.py",
       timeout => 3600,
        }
      }
      'glance' : {
        exec{"glance_ha":
        path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/mysql/glanceHAProxy.py",
       timeout => 3600,
        }

        exec{"glance_init":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/glance/glance.py",
       timeout => 3600,
        require =>Exec['glance_ha']
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
        'dashboard':

        {


#         exec{"dash_ha":
#       path => "/usr/bin:/bin",
#       command => "python /etc/puppet/fuel-python/openstack/icehouse/dashboard/dashboardHAProxy.py",
#       timeout => 3600,
#        }


#         exec{"dash_init":
#       path => "/usr/bin:/bin",
#       command => "python /etc/puppet/fuel-python/openstack/icehouse/dashboard/dashboard.py",
 #      timeout => 3600,
#       require => Exec['dash_ha']
#               }

        }
      default  : {
        fail("Unsupported osfamily: ${osfamily} for os ${operatingsystem}")
        notify {"keystone $role....................................":}
      }
      }
        

