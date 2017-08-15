set influxdb_space [exec vgs | grep dbvg | cut -d " " -f 18]
spawn lvcreate -L${influxdb_space} -n influxdb_lv dbvg
expect "signature detected on" { send "y\r" }
