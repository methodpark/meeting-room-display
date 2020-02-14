# Copyright 2018-2019 Method Park Engineering GmbH
#
# This file is part of Meeting-Room Display.
#
# Meeting-Room Display is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Meeting-Room Display is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Meeting-Room Display.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod

import logging
import socket
import struct


class NetworkConnectivity(object, metaclass=ABCMeta):
    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def get_ip_address(self):
        pass

    @abstractmethod
    def get_hostname(self):
        pass


class DefaultWifi(NetworkConnectivity):
    dev = "wlan0"

    def is_connected(self):
        try:
            ret = open('/sys/class/net/{0}/operstate'.format(self.dev), 'r').read().strip()
            if ret == "up":
                return True
            else:
                logging.warning("no connection to network: %s", self.dev)
                return False
        except Exception as e:
            logging.error("Error in checking network connection %s", e)
            return False

    def get_ip_address(self):
        import fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ipaddr = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,  # SIOCGIFADDR
            struct.pack('256s', self.dev[:15]))[20:24])

        return ipaddr

    def get_hostname(self):
        return socket.gethostname()


class AlwaysConnected(NetworkConnectivity):
    def is_connected(self):
        return True

    def get_ip_address(self):
        return "0.0.0.0"

    def get_hostname(self):
        return ""


class DummyGPIO(object):
    BOARD = None
    IN = 0
    PUD_UP = 0
    HIGH = 0
    LOW = 0

    def setmode(self, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        pass

    def input(self, *args, **kwargs):
        pass
