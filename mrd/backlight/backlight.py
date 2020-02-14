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

import time
import logging
import pickle

from mrd.backlight.dbus_client import BackLightDbusClient
from mrd.backlight.mqtt_client import BackLightMqttClient

import mrd.rooms as rooms

UNICORN = u"Unicorn User"

def is_easteregg(occupation):
    organizer = repr(occupation.current_event.title.strip())
    return organizer == repr(UNICORN)

def is_upcoming_event_in_some_minutes(occupation):
    date_diff = int(occupation.upcoming_event_today.date_from - time.time())
    return date_diff <= 15 * 60


class BackLight(rooms.EventPort):
    def occupation_changed(self, occupation):
        if occupation.is_occupied:
            logging.info("Setting backlight to occupied")
            if is_easteregg(occupation):
                self.set_rainbow()
            else:   
                self.set_occupied()
        elif occupation.upcoming_event_today != None:
            if is_upcoming_event_in_some_minutes(occupation):
                logging.info("Setting backlight event upcoming")
                self.set_event_upcoming()
            else:
                logging.info("Setting backlight to free")
                self.set_free()    
        else:
            logging.info("Setting backlight to free")
            self.set_free()

    def no_network_connection(self):
        logging.info("BackLight: Received no_network_connection from application")
        self.set_unconnected()

    def incorrect_configuration(self, _):
        self.set_unconnected()

    def render_initial_state(self):
        pass

    def __init__(self):
        try:
            #self.impl = BackLightProxy(BackLightMqttClient())
            self.impl = BackLightProxy(BackLightDbusClient())
        except Exception as e:
            logging.warning("Error while creating backlight client (%s), using dummy implementation", e)
            self.impl = BackLightDummy()

    def set_free(self):
        self.impl.set_free()

    def set_occupied(self):
        self.impl.set_occupied()

    def set_event_upcoming(self):
        self.impl.set_event_upcoming()

    def set_rainbow(self):
        self.impl.set_rainbow()

    def set_unconnected(self):
        self.impl.set_unconnected()

    def clear(self):
        self.impl.clear()

    def shut_down(self):
        self.impl.shut_down()


class BackLightProxy(object):

    def __init__(self, client):
        self._client = client

    def set_free(self):
        event = {'name': 'rgb', 'rgb': (0, 255, 0)}
        dumps = pickle.dumps(event)
        logging.info("set backlight to green: {0}".format(event))
        self._client.publish(dumps)

    def set_occupied(self):
        event = {'name': 'rgb', 'rgb': (255, 0, 0)}
        dumps = pickle.dumps(event)
        logging.info("set backlight to red: {0}".format(event))
        self._client.publish(dumps)

    def set_event_upcoming(self):
        event = {'name': 'rgb', 'rgb': (255, 95, 0)}
        dumps = pickle.dumps(event)
        logging.info("set backlight to orange: {0}".format(event))
        self._client.publish(dumps)

    def set_rainbow(self):
        event = {'name': 'rainbow'}
        dumps = pickle.dumps(event)
        logging.info("set backlight to rainbow: {0}".format(event))
        self._client.publish(dumps)

    def set_unconnected(self):
        event = {'name': 'rgb', 'rgb': (0, 0, 255)}
        dumps = pickle.dumps(event)
        logging.info("set backlight to blue: {0}".format(event))
        self._client.publish(dumps)

    def clear(self):
        event = {'name': 'clear'}
        dumps = pickle.dumps(event)
        logging.info("clear backlight: {0}".format(event))
        self._client.publish(dumps)

    def shut_down(self):
        event = {'name': 'quit'}
        dumps = pickle.dumps(event)
        logging.info("turn off backlight: {0}".format(event))
        self._client.publish(dumps)


class BackLightDummy(object):
    def set_free(self):
        logging.info("Set backlight to free")

    def set_occupied(self):
        logging.info("Set backlight to occupied")
    
    def set_event_upcoming(self):
        logging.info("set backlight to upcoming")

    def set_rainbow(self):
        logging.info("Set backlight to rainbow")

    def set_unconnected(self):
        logging.info("Set backlight to blue")

    def clear(self):
        logging.info("Clearing backlight")

    def shut_down(self):
        logging.info("Switching off backlight")
