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
import pickle
# https://pypi.org/project/paho-mqtt/
import paho.mqtt.client as mqtt
from mrd.backlight.mqtt_client import BASE_URL, TOPIC, HOST, PORT
import mrd.backlight.backlight_wrapper as backlight


class BackLightMqttService(object):

    def __init__(self, state_port):
        self.state_port = state_port
        self._url = BASE_URL + TOPIC
        self._server = self._set_up_server()
        self._server.loop_forever()

    def _set_up_server(self):
        # Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
        server = mqtt.Client()
        server.enable_logger()

        server.on_connect = self.on_connect
        server.on_disconnect = self.on_disconnect
        server.on_message = self.on_message

        # connect(host, port=1883, keepalive=60, bind_address="")
        rtn = server.connect(HOST, PORT, 60)
        if rtn != 0:
            logging.warn("connection refused rtn code {0}".format(rtn))
            sys.exit(1)

        return server

    def on_connect(self, client, userdata, flags, rc):
        logging.info("connected with flags {0} rtn code {1}".format(flags, rc))
        logging.info("subscribe to {0}".format(self._url))
        self._server.subscribe(self._url)

    def on_disconnect(client, userdata, rc):
        logging.info("disconnected with rtn code {0}".format(rc))

    def on_message(self, client, userdata, msg):
        event = pickle.loads(msg.payload)
        logging.info("new message: {0}".format(event))

        name = event.get('name')
        rgb = event.get('rgb')
        state = backlight.LEDState(name, rgb)
        self.state_port.state_changed(state)


if __name__ == "__main__":
    wrapper = backlight.BacklightWrapper()
    port = backlight.CompositeLEDPort()
    port.add_adapter(wrapper)
    BackLightMqttService(port)
