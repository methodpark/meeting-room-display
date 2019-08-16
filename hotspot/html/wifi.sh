#!/bin/bash

# make sure web server is disabled before rebooting device
#sudo /usr/bin/mrd_hotspot stop
sudo systemctl disable lighttpd.service

sleep 0.5
sudo reboot now