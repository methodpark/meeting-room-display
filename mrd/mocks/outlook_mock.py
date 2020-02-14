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

import calendar
import mrd.rooms as rooms
import time

from O365 import Calendar

class OutlookRoomRepositoryMock(rooms.RoomRepositoryPort):
    _seconds_per_hour = 60*60
    _begin_for_state_changing_appointment = 0

    def __init__(self, id, password):
        pass

    def fetch_calendar(self):
        pass

    def get_next_state_changing_appointment_up_to_midnight(self, time_in_sec_since_epoch):
        """return a current running or the next upcoming event until midnight

        :param int time_in_sec_since_epoch: the current time
        :param int begin: mock returns elapsed -1, currently running 0 or upcoming 1 appointment"""
        begin = self._begin_for_state_changing_appointment
        if begin < 0:
            return None
        elif begin == 0:
            time_from = time_in_sec_since_epoch - 0.25 * self._seconds_per_hour
            time_to = time_in_sec_since_epoch + 0.25 * self._seconds_per_hour
        else:
            time_from = time_in_sec_since_epoch + 0.25 * self._seconds_per_hour
            time_to = time_in_sec_since_epoch + 0.75 * self._seconds_per_hour

        return rooms.Appointment(time_from, time_to, "Mock Appointment")

    def book_room(self, time_from, time_to):
        return rooms.Appointment(time_from, time_to, "Mock Appointment")

    def cancel_appointment(self, time_in_sec_since_epoch=time.time()):
        pass

    def _get_calender(self, name="Calendar"):
        return Calendar()

    def incorrect_configuration(self):
        pass

    def no_network_connection(self):
        pass

    def occupation_changed(self, _):
        pass
