#!/bin/bash

sudo /bin/cat /etc/wpa_supplicant/wpa_supplicant.conf > /tmp/finddata

#list all ssid

grep -o "ssid=\".*\"" /tmp/finddata | \
sed 's/ssid="//g' | sed s'/.$//'

#cleanup
rm -f /tmp/finddata
