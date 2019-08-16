#!/bin/bash
#https://blog.doenselmann.com/raspberry-pi-fuer-dauereinsatz-optimieren/

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

status="$(sudo systemctl is-active backlight.service)"
if [ "${status}" == "inactive" ]; then
  systemctl restart backlight.service
fi

