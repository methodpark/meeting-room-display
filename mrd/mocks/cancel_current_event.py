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
import mrd.time_util as datetime
import time
from O365 import Event, Schedule
from mrd.display_main import read_room_information
from mrd.outlook import MissingCalendarError


def _cancel_current_event():

    time_in_sec_since_epoch = time.time()
    start = datetime.convert_secs_since_epoch_to_string(time_in_sec_since_epoch)
    end = datetime.convert_secs_since_epoch_to_string(time_in_sec_since_epoch + 5)

    cal = _get_calender()
    cal.getEvents(start=start, end=end)

    if len(cal.events) > 0:
        event = cal.events[0]
        event.delete()
        logging.info("cancel current event: {0}".format(event.getSubject()))
    else:
        logging.info("no current event found")


def _get_calender(name="Calendar"):

    room_information = read_room_information()

    schedule = Schedule((room_information.id, room_information.password))
    schedule.getCalendars()
    calendars = []
    for cal in schedule.calendars:
        calendars.append(cal)
        if cal.getName() == name:
            return cal
    if len(calendars) == 0:
        raise MissingCalendarError('no calendar found for room ' + room_information.room_id)
    return calendars[0]


if __name__ == '__main__':
    _cancel_current_event()
