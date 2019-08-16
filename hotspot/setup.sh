#!/bin/bash

#script based on:
#http://www.raspberryconnect.com/network/item/330-raspberry-pi-auto-wifi-hotspot-switch-internet
#https://www.instructables.com/id/Setup-a-Raspberry-Pi-PHP-web-server/

set -e
set -u
#set -x

echo "setup MRD autohotspot on '$(hostname)' Raspberry PI"
echo "beware: running setup will probably overwrite your local files"

usage()
{
	echo "Usage: sudo bash ${0} <DIRECTORY> [-i --install] [-u --update]" >&2
}

if [ "${UID}" -ne 0 ]; then
	echo "bash: ./setup.sh: Permission denied"
	echo "please run script with root privileges!"
	usage
	exit 1
fi

if [ "${#}" -lt 1 ] || ! [ -d "${1}" ]; then
	usage
	exit 1
elif [ "${#}" -eq 1 ]; then
	cmd="-i"
else
	cmd="${2}"
fi

MRD_BASEDIR="${1}"

if [ ! -f "${MRD_BASEDIR}/hotspot/mrd_hotspot" ]; then
	echo "${MRD_BASEDIR}/hotspot/mrd_hotspot: No such file or directory"
	exit 1
elif [ ! -f "${MRD_BASEDIR}/hotspot/hostapd.conf" ]; then
	echo "${MRD_BASEDIR}/hotspot/hostapd.conf: No such file or directory"
	exit 1
elif [ ! -f "${MRD_BASEDIR}/hotspot/rc.local" ]; then
	echo "${MRD_BASEDIR}/hotspot/rc.local: No such file or directory"
	exit 1
elif [ ! -d "${MRD_BASEDIR}/hotspot/html" ]; then
	echo "${MRD_BASEDIR}/hotspot/html: No such file or directory"
	exit 1
fi

make_update()
{
	echo "update Raspbian with the latest updates"

	apt-get update
	apt-get upgrade -y
}

configure_startup_screen()
{
	echo "make rc.local file to display network on startup"

	cp "${MRD_BASEDIR}/hotspot/rc.local" /etc/rc.local
}

install_services()
{

	echo "install hostapd hotspot client and dnsmasq lightweight dns server"

	apt-get install -y hostapd
	apt-get install -y dnsmasq

	#disable automatic startup
	systemctl disable hostapd
	systemctl disable dnsmasq

	echo "install lighttpd web server and php scripting language"

	apt-get -y install lighttpd
	apt-get -y install php-cgi

	#enable the fastcgi module which will handle the PHP pages
	lighty-enable-mod fastcgi
	lighty-enable-mod fastcgi-php

	#restart lighttpd service
	service lighttpd force-reload
}

configure_hostapd()
{
	echo "hostapd configuration"

	fhostapd="/etc/default/hostapd"

	cp "${MRD_BASEDIR}/hotspot/hostapd.conf" /etc/hostapd/hostapd.conf

    # rename ssid
    hostname=$(hostname)
    sed -i "s|^ssid=.*|ssid=${hostname^^}_HOTSPOT|g" /etc/hostapd/hostapd.conf

	#update defaults file to point to where the config file is stored
	if grep -q '#DAEMON_CONF=""' ${fhostapd}; then
		sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|g' ${fhostapd}
	fi

	if grep -q '^DAEMON_OPTS=""' ${fhostapd}; then
		sed -i 's|DAEMON_OPTS=""|#DAEMON_OPTS=""|g' ${fhostapd}
	fi

}

configure_dnsmasq()
{
	echo "DNSmasq configuration"

	fdnsmasq="/etc/dnsmasq.conf"

	#allow the RPi to act as a router and issue ip addresses
	echo "" >> ${fdnsmasq}
	echo "# AutoHotspot config" >> ${fdnsmasq}
	echo "interface=wlan0" >> ${fdnsmasq}
	echo "bind-dynamic" >> ${fdnsmasq}
	echo "server=8.8.8.8" >> ${fdnsmasq}
	echo "domain-needed" >> ${fdnsmasq}
	echo "bogus-priv" >> ${fdnsmasq}
	echo "dhcp-range=192.168.50.150,192.168.50.200,255.255.255.0,12h" >> ${fdnsmasq}
}

configure_interfaces()
{
	echo "clearing interfaces file"

	finterfaces="/etc/network/interfaces"

	#interfaces file is not required and should be empty of any network config
	if [ $( wc -l < ${finterfaces} ) -gt 5 ]; then
		echo "saving old interfaces to ${finterfaces}.old"
		mv ${finterfaces} ${finterfaces}.old
	fi

	echo "# interfaces(5) file used by ifup(8) and ifdown(8)" > ${finterfaces}
	echo "# Please note that this file is written to be used with dhcpcd" >> ${finterfaces}
	echo "# For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'" >> ${finterfaces}
	echo "# Include files from /etc/network/interfaces.d:" >> ${finterfaces}
	echo "source-directory /etc/network/interfaces.d" >> ${finterfaces}
}

activate_ip_forwarding()
{
	echo "activating ip forwarding"

	fsysctl="/etc/sysctl.conf"

	#ip forwarding needs to be on so the internet works when an ethernet cable is attached
	if grep -q "#net.ipv4.ip_forward=1" ${fsysctl}; then
		sed -i "s|#net.ipv4.ip_forward=1|net.ipv4.ip_forward=1|g" ${fsysctl}
	elif ! ( grep -q "net.ipv4.ip_forward=1" ${fsysctl} ); then
		echo "" >> ${fsysctl}
		echo "# Uncomment the next line to enable packet forwarding for IPv4" >> ${fsysctl}
		echo "net.ipv4.ip_forward=1" >> ${fsysctl}
	fi
}

stop_dhcpcd()
{
	echo "stop dhcpcd network setup service"

	fdhcpcd="/etc/dhcpcd.conf"

	#stop dhcpcd from starting the wifi network
	if ! ( grep -q "^nohook wpa_supplicant" ${fdhcpcd} ) \
	|| ( grep -q "#nohook wpa_supplicant" ${fdhcpcd} ); then
		echo "" >> ${fdhcpcd}
		echo "" >> ${fdhcpcd}
		echo "# Stop dhcpcd from starting the wifi network" >> ${fdhcpcd}
		echo "nohook wpa_supplicant" >> ${fdhcpcd}
	fi

}

create_autohotspot()
{
	echo "create autohotspot"

	cp "${MRD_BASEDIR}/hotspot/mrd_hotspot" /usr/bin/mrd_hotspot
	chmod +x /usr/bin/mrd_hotspot
}

copy_html_files()
{
	echo "copying html files"

	cp -r "${MRD_BASEDIR}/hotspot/html" /var/www/
}

configure_lighttpd()
{
	echo "setting permissions for lighttpd"

	groupadd -f www-data
	usermod -G www-data -a pi
	chown -R www-data:www-data /var/www/html
	chmod -R 775 /var/www/html

	mkdir -p "/etc/lighttpd/certs"
	cp "${MRD_BASEDIR}/hotspot/lighttpd.pem" "/etc/lighttpd/certs/lighttpd.pem"

	flighttpd="/etc/lighttpd/lighttpd.conf"

	echo "" >> ${flighttpd}
	echo '$SERVER["socket"] == ":443" {' >> ${flighttpd}
	echo -e '\tssl.engine = "enable"' >> ${flighttpd}
	echo -e '\tssl.pemfile = "/etc/lighttpd/certs/lighttpd.pem"' >> ${flighttpd}
	echo '}' >> ${flighttpd}

	# service lighttpd force-reload
	systemctl disable lighttpd
}

configure_sudoers()
{
	echo "update sudoers file"

	fsudoers="/etc/sudoers"

	echo "" >> ${fsudoers}
	echo "mrd ALL=(ALL) NOPASSWD: ALL" >> ${fsudoers}
	echo "" >>  ${fsudoers}
	echo "# Allow lighttpd server to execute commands" >>  ${fsudoers}
	echo "www-data ALL=(ALL) NOPASSWD:/bin/cat /etc/wpa_supplicant/wpa_supplicant.conf" >> ${fsudoers}
	echo "www-data ALL=(ALL) NOPASSWD:/bin/mv /tmp/wifidata /etc/wpa_supplicant/wpa_supplicant.conf" >> ${fsudoers}
	echo "www-data ALL=(ALL) NOPASSWD:/bin/mv /tmp/config /home/pi/mrd-repo/mrd/configuration.ini" >> ${fsudoers}
	echo "www-data ALL=(ALL) NOPASSWD:/usr/bin/mrd_hotspot" >> ${fsudoers}
	echo "www-data ALL=(ALL) NOPASSWD:/bin/cat /var/log/syslog" >> ${fsudoers}
	echo "www-data ALL=(ALL) NOPASSWD:/sbin/reboot" >> ${fsudoers}
}

main()
{
	make_update
	configure_startup_screen

	#Step 1:
	#To start with hostapd hotspot client and dnsmasq lightweight dns server need to be installed.

	install_services
	configure_hostapd
	configure_dnsmasq

	#Step 2:
	#make some changes to the interfaces file, setup ip_forwarding and dhcpcd.conf

	configure_interfaces
	activate_ip_forwarding
	#stop_dhcpcd

	#creating the autohotspot script and make it executable
	create_autohotspot

	#Step 3:
	#configure lighttpd web server

	copy_html_files
	configure_lighttpd
	configure_sudoers
}

if [ "${cmd}" == "-u" ] || [ "${cmd}" == "--update" ]; then
	echo "update dependecies for hotspot mode"
	configure_startup_screen
	create_autohotspot
	copy_html_files
elif [ -d "/var/www/html" ]; then
	echo "warning: hotspot mode already installed"
	usage
else
	echo "run complete setup for hotspot mode"
	main
fi

echo "setup done"
echo "please restart RPi"

exit 0
