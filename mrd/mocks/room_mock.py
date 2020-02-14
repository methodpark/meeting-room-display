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
import random
import time

import mrd.rooms as rooms
import mrd.time_util as datetime


class AlternatingOccupation(rooms.RoomRepositoryPort):
    def __init__(self):
        self._is_occupied = False

    def _update_occupation(self):
        new_occupation = not self._is_occupied
        self._is_occupied = new_occupation
        return new_occupation

    def fetch_calendar(self):
        pass

    def book_room(self, time_from, time_to):
        logging.info("AlternatingOccupation: mock received booking request time_from %s, time_to %s",
                     time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time_from)),
                     time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time_to)))
        self._update_occupation()

    def get_next_state_changing_appointment_up_to_midnight(self, time_in_sec_since_epoch):
        if self._is_occupied:
            in_minutes = -10
            appointment = self._next_meeting_today(in_minutes)
        else:
            if random.random() < 0.3:
                appointment = None
            else:
                in_minutes = random.randint(15, 75)
                appointment = self._next_meeting_today(in_minutes)

        self._update_occupation()
        return appointment

    def _next_meeting_today(self, start_in_min_from_now):
        return rooms.Appointment(
            date_from=time.time() + datetime.minutes(start_in_min_from_now),
            date_until=time.time() + datetime.minutes(start_in_min_from_now + 45),
            title="Mock Title",
            num_attendees=5
        )
