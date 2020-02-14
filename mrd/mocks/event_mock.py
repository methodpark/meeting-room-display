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
import mrd.time_util as datetime
from enum import Enum
from mrd.outlook import AuthenticationFailureError, to_appointment
import random
import time


_raise_error = False

class EventStates(Enum):
    ELAPSED = 1
    RUNNING = 2
    UPCOMING = 3
    FUTURE = 4
    ADHOC = 5


def set_auth_error_true():
    global _raise_error
    _raise_error = True


class ScheduleMock(object):

    def __init__(self, auth, verify=True):
        self.auth = auth
        self.calendars = []

        self.verify = verify

        global _raise_error
        _raise_error = False

    def getCalendars(self):
        if _raise_error:
            raise AuthenticationFailureError('incorrect authentication')

        calendar = {'Color': 'Auto', 'Name': 'Calendar'}
        self.calendars.append(CalendarMock(calendar, self.auth))
        return True


class CalendarMock(object):

    def __init__(self, json=None, auth=None, verify=True):
        self.json = json
        self.auth = auth

        self.events = []

        # mock behavior
        self._event_state = 0

    def _set_event_state(self, state):
        self._event_state = state

    def _delete_event(self, event):
        self.events.remove(event)
        self._set_event_state(0)

    def getEvents(self, start=None, end=None, eventCount=10):
        if start is None:
            start = time.time()

        subject = 'Mock Driver'
        date_from = datetime.convert_string_to_secs_since_epoch(start)

        if self._event_state == EventStates.ELAPSED:
            date_until = date_from - 15 * 60
            date_from = date_from - 45 * 60
        elif self._event_state == EventStates.RUNNING:
            date_until = date_from + 15 * 60
            date_from = date_from - 15 * 60
        elif self._event_state == EventStates.UPCOMING:
            date_until = date_from + 45 * 60
            date_from = date_from + 15 * 60
        elif self._event_state == EventStates.FUTURE:
            date_until = date_from + 60 * 60
            date_from = date_from + 30 * 60
        elif self._event_state == EventStates.ADHOC:
            date_until = date_from + 15 * 60
            date_from = date_from - 15 * 60
            subject = 'Ad-Hoc Meeting'
        else:
            return True

        start = datetime.convert_secs_since_epoch_to_string(date_from)
        end = datetime.convert_secs_since_epoch_to_string(date_until)

        json = { 'Start': start, 'End': end, 'Subject': subject }
        self.events.append(EventMock(json, self.auth, self))

        return True

    def getName(self):
        return self.json['Name']


class EventMock(object):
    time_string = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, json=None, auth=None, cal=None, verify=True):
        self.auth = auth
        self.calendar = cal
        self.attendees = []

        if json is None:
            self.json = {}
        else:
            self.json = json

        self.verify = verify

    def getStart(self):
        return time.strptime(self.json['Start'], self.time_string)

    def getEnd(self):
        return time.strptime(self.json['End'], self.time_string)

    def getSubject(self):
        return self.json['Subject']

    def setStart(self, val):
        self.json['Start'] = time.strftime(self.time_string, time.gmtime(val))

    def setEnd(self, val):
        self.json['End'] = time.strftime(self.time_string, time.gmtime(val))

    def setSubject(self, val):
        self.json['Subject'] = val

    def create(self, calendar=None):
        return to_appointment(EventMock(self.json, self.auth, self.calendar))

    def delete(self):
        self.calendar._delete_event(self)

    def fullcalendarioJson(self):
        ret = {}
        ret['title'] = self.json['Subject']
        if self.calendar._event_state == EventStates.ADHOC:
            ret['driver'] = self.auth[0]
            ret['driverEmail'] = self.auth[0]
        else:
            ret['driver'] = self.json['Subject']
            ret['driverEmail'] = "dummy_drive@example.org"
        ret['start'] = self.json['Start']
        ret['end'] = self.json['End']
        return ret


if __name__ == '__main__':
    import mrd.outlook as outlook

    id = "test_room@example.org"
    password = "********"

    backend = outlook.OutlookRoomRepository(id, password)
    appointment = backend.get_next_state_changing_appointment_up_to_midnight(time.time())

    print(datetime.convert_secs_since_epoch_to_string(appointment.date_from))
    print(datetime.convert_secs_since_epoch_to_string(appointment.date_until))
    print(appointment.title)
