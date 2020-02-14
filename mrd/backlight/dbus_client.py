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
import pydbus

DBUS_SERVICE = "de.methodpark.er.meeting_room_display.Backlight"


class BackLightDbusClient(object):

    def __init__(self):
        try:
            bus = pydbus.SystemBus()
            self._obj = bus.get(DBUS_SERVICE)
        except gi.repository.GLib.Error:
            logging.warning("Failed to retrieve D-BUS service from system bus; falling back to session bus")
            bus = pydbus.SessionBus()
            self._obj = bus.get(DBUS_SERVICE)

    def publish(self, dumps):
        self._obj.set_state(dumps)
