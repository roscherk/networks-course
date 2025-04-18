#!/bin/bash
# :)

ip -4 addr | grep -v '127.0.0.1' | awk '/inet/ && $NF ~ /^wl/ {
    split($2, ip_cidr, "/")
    iface = $NF
    ip = ip_cidr[1]
    
    cmd = "ip -4 addr show dev " iface " | grep inet | awk \"{print \\$4}\""
    cmd | getline mask
    
    print "IP-адрес:  " ip
    print "Маска сети: " mask
}'
