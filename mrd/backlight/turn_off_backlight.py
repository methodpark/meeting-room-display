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

import logging
import paho.mqtt.client as mqtt
import pickle

from mrd.backlight.backlight import BASE_URL, TOPIC, HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='w')

client = mqtt.Client()
client.connect(HOST, PORT, 60)
url = BASE_URL + TOPIC

event = {'name': 'quit'}
dumps = pickle.dumps(event)
logging.info("turn off backlight: {0}".format(event))

client.publish(url, dumps)
client.disconnect()

logging.info("exiting script")
