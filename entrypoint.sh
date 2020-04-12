#!/bin/sh

# "fix" nginx.conf to include the IP adress

sed -i -e "s/PUB_IP_FROM_ENV/$PUB_IP/g" /etc/nginx/nginx.conf
 
pkill -9 nginx
/usr/sbin/nginx
# Start the second process
/usr/bin/python3 /opt/dns.py --ip ENV --whitelist /opt/domains
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start dns: $status"
  exit $status
fi