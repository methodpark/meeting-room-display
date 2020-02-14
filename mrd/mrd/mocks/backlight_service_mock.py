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

import dbus
import dbus.service
import dbus.mainloop.glib

from gi.repository import GObject
import sys
import atexit

import logging


@atexit.register
def goodbye():
    logging.error("service crashed, shutting down unicorn back light")
    #logging.error("unexpected error:", sys.exc_info()[0])
    sys.exit(1)


class BackLightService(dbus.service.Object):

    def __init__(self, url):
        print(getattr(dbus, 'version'))
        self._url = url

    def run(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName("de.methodpark.er.meeting_room_display.backlight", dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/de/methodpark/er/meeting_room_display/backlight")

        self._loop = GObject.MainLoop()
        print("Service running...")
        self._loop.run()

    @dbus.service.method("de.methodpark.er.meeting_room_display.backlight.message", in_signature='', out_signature='s')
    def get_message(self):
        return "message"

    @dbus.service.method("de.methodpark.er.meeting_room_display.backlight.green", in_signature='', out_signature='')
    def do_green(self):
        print("set backlight to green")

    @dbus.service.method("de.methodpark.er.meeting_room_display.backlight.red", in_signature='', out_signature='')
    def do_red(self):
        print("set backlight to red")

    @dbus.service.method("de.methodpark.er.meeting_room_display.backlight.quit", in_signature='', out_signature='')
    def quit(self):
        print("shutting down service")
        self._loop.quit()

if __name__ == "__main__":
    BackLightService("de.methodpark.er.meeting_room_display.backlight").run()
