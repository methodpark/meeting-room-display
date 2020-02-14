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

import paho.mqtt.client as mqtt
import time
import logging
import pickle
from mrd.backlight.backlight import BASE_URL, TOPIC

URL = BASE_URL + TOPIC


class AlternatingBackLightClient(object):

    def __init__(self):
        self._client = mqtt.Client()
        self._client.connect("localhost", 1883, 60)
        self._client.loop_start()
        self.loop_occupations()

    def loop_occupations(self):
        for _ in range(0, 5):
            self.set_free()
            time.sleep(3)
            self.set_occupied()
            time.sleep(3)
            self.turn_off_backlight()
            time.sleep(3)

        self.shut_down()


    def set_free(self):
        event = {'name': 'rgb', 'rgb': (0, 255, 0)}
        dumps = pickle.dumps(event)
        logging.info("set backlight to green: {0}".format(event))
        self._client.publish(URL, dumps)

    def set_occupied(self):
        event = {'name': 'rgb', 'rgb': (255, 0, 0)}
        dumps = pickle.dumps(event)
        logging.info("set backlight to red: {0}".format(event))
        self._client.publish(URL, dumps)

    def turn_off_backlight(self):
        event = {'name': 'clear'}
        dumps = pickle.dumps(event)
        logging.info("turn off backlight: {0}".format(event))
        self._client.publish(URL, dumps)

    def shut_down(self):
        event = {'name': 'quit'}
        dumps = pickle.dumps(event)
        logging.info("shut down backlight: {0}".format(event))
        self._client.publish(URL, dumps)


if __name__ == "__main__":
    AlternatingBackLightClient()
