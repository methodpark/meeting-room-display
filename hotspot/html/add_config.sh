#!/bin/bash

echo "[RoomInformation]" > /tmp/config
echo "id: ${1}" >> /tmp/config
echo "name: ${2}" >> /tmp/config
echo "password: ${3}" >> /tmp/config
echo "adhoc: ${4}" >> /tmp/config
echo "language: ${5}" >> /tmp/config

sudo /bin/mv /tmp/config /home/pi/mrd-repo/mrd/configuration.ini
