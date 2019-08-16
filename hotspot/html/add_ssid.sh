#!/bin/bash

#sudo /bin/cat /etc/wpa_supplicant/wpa_supplicant.conf > /tmp/wifidata

sudo /bin/cat /etc/wpa_supplicant/wpa_supplicant.conf > /tmp/wifidata

if [ $( wc -l < /tmp/wifidata ) -eq 0 ]; then
	echo "country=DE" > /tmp/wifidata
	echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" >> /tmp/wifidata
	echo "update_config=1" >> /tmp/wifidata
fi

#wpa_passphrase "$1" "$2" | grep -v "#psk" >> /tmp/wifidata
wpa_passphrase "$1" "$2" >> /tmp/wifidata

sudo /bin/mv /tmp/wifidata /etc/wpa_supplicant/wpa_supplicant.conf
