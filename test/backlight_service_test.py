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

import unittest
import pickle
import logging
import time
import _thread
import paho.mqtt.client as mqtt

from mrd.backlight.mqtt_service import BackLightMqttService
from mrd.backlight.backlight_wrapper import LEDState, BacklightMock
from mrd.backlight.backlight import BASE_URL, TOPIC

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     filemode='w')


class PortMock(object):

    def __init__(self):
        self._unicorn = BacklightMock()

    def state_changed(self, state):
        self._unicorn.state_changed(state)

    @property
    def unicorn(self):
        return self._unicorn


def start_mqtt_thread(thread_id, port):
    logging.info("started new service thread: {0}".format(thread_id))
    BackLightMqttService(state_port=port)


def has_mqtt_server_runnig():
    try:
        client = mqtt.Client()

        client.connect("localhost", 1883, 60)
        return True
    except Exception as e:
        logging.warn("This machine is not set up with a MQTT broker %s", e)
        return False


@unittest.skipUnless(has_mqtt_server_runnig(), 'skipping tests that require a running MQTT broker')
class BacklightServiceTest(unittest.TestCase):

    def setUp(self):
        self.port = PortMock()
        _thread.start_new_thread(start_mqtt_thread, ("service-thread", self.port))
        time.sleep(.1)

    def test__set_free(self):
        client = mqtt.Client()
        url = BASE_URL + TOPIC

        client.connect("localhost", 1883, 60)
        client.subscribe(url)
        time.sleep(.1)

        self.assertEqual(self.port.unicorn.state, None)

        name = 'rgb'
        rgb = (0, 255, 0)
        event = {'name': name, 'rgb': rgb}

        dumps = pickle.dumps(event)
        client.publish(url, dumps)
        time.sleep(.1)

        self.assertEqual(self.port.unicorn.state.name, name)
        self.assertEqual(self.port.unicorn.state.rgb, rgb)

    def test__clear(self):
        client = mqtt.Client()
        url = BASE_URL + TOPIC

        client.connect("localhost", 1883, 60)
        client.subscribe(url)
        time.sleep(.1)

        self.assertEqual(self.port.unicorn.state, None)

        name = 'clear'
        rgb = None
        event = {'name': name, 'rgb': rgb}

        dumps = pickle.dumps(event)
        client.publish(url, dumps)
        time.sleep(.1)

        self.assertEqual(self.port.unicorn.state.name, name)
        self.assertEqual(self.port.unicorn.state.rgb, rgb)

    def test__turn_off(self):
        client = mqtt.Client()
        url = BASE_URL + TOPIC

        client.connect("localhost", 1883, 60)
        client.subscribe(url)
        time.sleep(.1)

        self.assertEqual(self.port.unicorn.state, None)

        name = 'quit'
        rgb = None
        event = {'name': name, 'rgb': rgb}

        dumps = pickle.dumps(event)
        client.publish(url, dumps)
        time.sleep(.1)

        self.assertEqual(self.port.unicorn.state.name, name)
        self.assertEqual(self.port.unicorn.state.rgb, rgb)
