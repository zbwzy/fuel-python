$fuel_settings = parseyaml($astute_settings_yaml)
$mysql_vip = $fuel_settings['mysql']['mysql_vip']
$local_ip = $::ipaddress
$master_ip = $fuel_settings['masterip']
$installDir ='/home/app'
$role = $fuel_settings['role']

stage {'zero': } ->

stage {'first': } 

class {'initParam': stage => 'zero'}
class {'deploy_openstack': stage=> 'first'}


class initParam{

	exec {"fuel_python_dir":
	     path => "/usr/bin:/bin",
	     command => "cp -r /etc/puppet/modules/fuel-python /etc/puppet",
	}

	exec {"openstack_config":
	path => "/usr/bin:/bin",
	command => "mkdir -p /etc/puppet/openstack_conf",
	before  => Exec["prerequisites"],
	require => Exec["fuel_python_dir"],
	creates => "/tmp/test1"
	}


	exec {"prerequisites":
	     path => "/usr/bin:/bin",
	     command => "python /etc/puppet/fuel-python/openstack/kilo/prerequisites/prerequisites.py"
	}

}

class deploy_openstack {

  notify {">>>>>>>>>>>>>【$keystone_role】------------------------------":}

  case $role {
      'mysql' : {
      exec{"mysql_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/mysql/bcrdb.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
       }
		

      'keystone' : {
	 exec{"keystone_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/keystone/keystone.py",
       timeout => 3600,
       require => Exec['prerequisites']
          }
       }
   

      'glance' : {
       exec{"glance_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/glance/glance.py",
       timeout => 3600,
       require => Exec['prerequisites']
 	          }
	   }

      'cinder-api' : {
        exec{"cinder_api_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/cinder/cinder.py",
       timeout => 3600,
       require => Exec['prerequisites']
              }
        }
       
       'cinder-storage' : {
        exec{"cinder_storage_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/cinderstorage/cinderstorage.py",
       timeout => 3600,
       require => Exec['prerequisites']
               }
        }

      'heat' : {
        exec{"heat_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/heat/heat.py",
       timeout => 3600,
       require => Exec['prerequisites']
               }
        }
       
       'mongodb' : {
       exec{"mongodb_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/mongodb/mongodb.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }

      'ceilometer' : {
       exec{"ceilometer_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/ceilometer/ceilometer.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }
       
      'nova-api' : {
       exec{"nova_api_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/nova/nova.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }
       
      'nova-compute' : {
       exec{"nova_compute_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/novacompute/novacompute.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }
        
       'neutron-server' : {
       exec{"neutron_server_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/neutronserver/neutronserver.py",
       timeout => 3600,
       require => Exec['prerequisites']
             }
        }

       'neutron-agent' : {
       exec{"neutron_agent_install":
       path => "/usr/bin:/bin",
       command => "python /etc/puppet/fuel-python/openstack/kilo/network/network.py",
       timeout => 3600,
       require => Exec['prerequisites']
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
       require => Exec['prerequisites']
            }
	}

	'horizon':
	{
           exec{"horizon_install":
           path => "/usr/bin:/bin",
           command => "python /etc/puppet/fuel-python/openstack/kilo/dashboard/dashboard.py",
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

