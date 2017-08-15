spawn lvcreate -L600GB -n mysql_lv dbvg
expect "signature detected on" { send "y\r" }