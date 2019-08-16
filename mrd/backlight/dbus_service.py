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

import gi.repository.GLib
import logging
import pickle
import pydbus
from mrd.backlight.dbus_client import DBUS_SERVICE
import mrd.backlight.backlight_wrapper as backlight


class BackLightDbusService(object):
    """
        <node>
            <interface name='de.methodpark.er.meeting_room_display.Backlight'>
                <method name='set_state'>
                    <arg type='ay' name='msg' direction='in'/>
                </method>
            </interface>
        </node>
    """

    def __init__(self, state_port):
        self.state_port = state_port
        loop = gi.repository.GLib.MainLoop()
        try:
            bus = pydbus.SystemBus()
            bus.publish(DBUS_SERVICE, self)
        except gi.repository.GLib.Error:
            logging.warning("Failed to publish D-BUS service on system bus; falling back to session bus")
            bus = pydbus.SessionBus()
            bus.publish(DBUS_SERVICE, self)
        loop.run()

    def set_state(self, msg):
        event = pickle.loads(bytes(msg))
        logging.info("new message: {0}".format(event))

        name = event.get('name')
        rgb = event.get('rgb')
        state = backlight.LEDState(name, rgb)
        self.state_port.state_changed(state)


if __name__ == "__main__":
    wrapper = backlight.BacklightWrapper()
    port = backlight.CompositeLEDPort()
    port.add_adapter(wrapper)
    BackLightDbusService(port)
