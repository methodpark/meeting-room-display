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

# https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt

# set up connection here
BASE_URL = "/de/methodpark/er/meeting_room_display"
TOPIC    = "/backlight"
HOST     = "localhost"
PORT     = 1883


class BackLightMqttClient(object):

    def __init__(self):
        self._client = mqtt.Client()
        self._client.connect(HOST, PORT, 60)
        self._url = BASE_URL + TOPIC

    def publish(self, dumps):
        self._client.publish(self._url, dumps)
