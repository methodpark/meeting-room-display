#!/bin/bash

sudo /bin/cat /etc/wpa_supplicant/wpa_supplicant.conf > /tmp/remdata

#check for given ssid
if grep -q "ssid=\"$1\"" -B1 -A4 /tmp/remdata; then

    #remove ssid and its surrounding block
    sed -n "1 !H;1 h;$ {x;s/[[:space:]]*network={\n[[:space:]]*ssid=\"${1}\"[^}]*}//g;p;}" /tmp/remdata > /tmp/wifidata

    sudo /bin/mv /tmp/wifidata /etc/wpa_supplicant/wpa_supplicant.conf

    echo "success"
else
    echo "not_found"
fi

#cleanup
rm -f /tmp/remdata
