$fuel_settings = parseyaml($astute_settings_yaml)
$mysql_vip = $fuel_settings['mysql']['mysql_vip']
$local_ip = $::ipaddress
$master_ip = $fuel_settings['masterip']
$installDir ='/home/app'
$role = $fuel_settings['role']

stage {'zero': } ->

stage {'first': } 

class {'initParams': stage => 'zero'}
class {'begin_deploy': stage=> 'first'}


class initParams{

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



exec {"openstack_yaml":
     path => "/usr/bin:/bin",
     command => "python /etc/puppet/fuel-python/common/yaml/ParamsProducer.py"
}




}

class begin_deploy {



notify {">>>>>>>>>>>>>【$keystone_role】------------------------------":}

  case $role {
      'mysql' : {
		
	if file('/opt/is_keystone_role') == 'false'
	{
	  class { 'mysql_galera':
        installDir => $installDir,
       root_passwd => "123456",
        mysql_vip => $mysql_vip,
        master_ip => $master_ip,
        nodes_ip => $nodes_ip
       }
	}
      }

      'keystone' : {
	if file('/opt/is_mysql_role') =='true'
		{
       exec{"keystone_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/keystone/keystone.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
	}
		}
	else
	{

	Exec<| title == 'initDB' |> -> Exec['keystone_install2']
        class { 'mysql_galera':
        installDir => $installDir,
       root_passwd => "123456",
        mysql_vip => $mysql_vip,
        master_ip => $master_ip,
        nodes_ip => $nodes_ip,
	before => Exec['keystone_install2'],
        require => Exec['openstack_yaml']
       }
	
	 exec{"keystone_install2":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/keystone/keystone.py",
       timeout => 3600,
        }


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
       
       'mongodb' : {
       exec{"mongodb_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/mongodb/mongodb.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
        }

      'ceilometer' : {
       exec{"ceilometer_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/ceilometer/ceilometer.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
        }
       
      'nova-api' : {
       exec{"nova_api_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/nova/nova.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
        }
       
      'nova-compute' : {
       exec{"nova_compute_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/novacompute/novacompute.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
        }
        
       'neutron-server' : {
       exec{"neutron_server_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/neutronserver/neutronserver.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
        }
        
        'neutron-agent' : {
       exec{"neutron_agent_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/icehouse/network/network.py",
       timeout => 3600,
       require => Exec['openstack_yaml']
             }
        }


      'rabbitmq' :
	{
      $rabbitmq_vip = $fuel_settings['rabbitmq']
      class { 'rabbitmq_clu':
        installDir => $installDir,
        guest_passwd => "123456",
        rabbitmq_vip => $rabbitmq_vip,
        master_ip => $master_ip,
       require => Exec['openstack_yaml']
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

      default  : {
     #   fail("Unsupported osfamily: ${osfamily} for os ${operatingsystem}")
	notify {"other $role...................................":}
      }



}
      }

