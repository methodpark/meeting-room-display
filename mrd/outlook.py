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

import datetime
import logging
import pathlib
import time

from . import rooms
from . import time_util


def to_appointment(event, is_adhoc=False):
    if event is None:
        return event
    else:
        num_attendees = len(event.attendees) if not is_adhoc else 0
        return rooms.Appointment(time_util.convert_datetime_to_secs_since_epoch(event.start),
                                 time_util.convert_datetime_to_secs_since_epoch(event.end),
                                 event.subject, num_attendees, is_adhoc)


class MissingPasswordForRoomIdError(Exception):
    pass


class CorruptArgumentError(Exception):
    def __init__(self, message):
        self.message = message


class MissingCalendarError(Exception):
    def __init__(self, message):
        self.message = message


class AuthenticationFailureError(Exception):
    def __init__(self, message):
        self.message = message


class OutlookRoomRepository(rooms.RoomRepositoryPort):
    _seconds_per_day = 60 * 60 * 24
    _scopes = ['offline_access', 'https://graph.microsoft.com/Calendars.ReadWrite']
    _ad_hoc_subject = "Ad-hoc Meeting"

    def __init__(self, room_id, client_id, client_secret, use_mock=False):
        self._room_id = room_id
        self._credentials = (client_id, client_secret)
        self.calendar = None

        global Account, FileSystemTokenBackend

        if use_mock:
            logging.warning("mock behavior not implemented yet, using O365 library anyway")
            # from mrd.mocks.event_mock import AccountMock as Account
            # from mrd.mocks.event_mock import EventMock as Event
            from O365 import Account, FileSystemTokenBackend
        else:
            from O365 import Account, FileSystemTokenBackend

    def fetch_calendar(self):
        if self.calendar is not None:
            return

        try:
            self.calendar = self._get_calendar()
        except RuntimeError as e:
            raise AuthenticationFailureError(e)

    def _fetch_event_from_outlook_calendar(self, time_in_sec_since_epoch):
        start = time_util.convert_secs_since_epoch_to_datetime(time_in_sec_since_epoch)
        midnight_in_secs = time_in_sec_since_epoch - (time_in_sec_since_epoch % self._seconds_per_day) + self._seconds_per_day - 1
        # midnight: same day 23:59:59
        midnight_datetime = time_util.convert_secs_since_epoch_to_datetime(midnight_in_secs)

        calendar = self._get_calendar()

        query = calendar.new_query('start').greater_equal(start)
        query.chain('and').on_attribute('end').less_equal(midnight_datetime)

        events = calendar.get_events(limit=25, query=query, include_recurring=True)

        event = None
        for e in events:
            end = time_util.convert_datetime_to_secs_since_epoch(e.end)
            start = time_util.convert_datetime_to_secs_since_epoch(e.start)
            # event out of range
            if end < time_in_sec_since_epoch or start > midnight_in_secs:
                continue
            # event begins earlier than recently remembered event
            if event is None or e.start < event.end:
                event = e

        return event

    def get_next_state_changing_appointment_up_to_midnight(self, time_in_sec_since_epoch):
        '''
            this method return the current running or next upcoming event until midnight.

            IMPORTANT: It returns an Appointment or None if no upcoming event was found.

            time_in_sec_since_epoch -- timestamp for which the next upcoming event should get searched, now on default.
        '''
        event = self._fetch_event_from_outlook_calendar(time_in_sec_since_epoch)

        if event is None:
            # no upcoming event found or room already occupied: return None
            logging.info("OutlookRoomRepository: no event found for %s", self._room_id)
        else:
            logging.info("OutlookRoomRepository: found event {0}, {1}, {2}".format(
                event.start,
                event.end,
                event.subject))

        return to_appointment(event, self._is_adhoc(event))

    def book_room(self, time_from, time_to):
        logging.info("OutlookRoomRepository: received booking request from %s, to %s",
                     time_util.convert_secs_since_epoch_to_string(time_from),
                     time_util.convert_secs_since_epoch_to_string(time_to))

        calendar = self._get_calendar()
        event = calendar.new_event()

        event.start = time_util.convert_secs_since_epoch_to_datetime(time_from)
        event.end = time_util.convert_secs_since_epoch_to_datetime(time_to)
        event.subject = self._ad_hoc_subject
        event.save()

        return to_appointment(event, is_adhoc=True)

    def cancel_running_adhoc_meeting(self):
        time_in_sec_since_epoch = time.time()
        event = self._fetch_event_from_outlook_calendar(time_in_sec_since_epoch)
        if event is None or time_util.is_in_future(time_util.convert_datetime_to_secs_since_epoch(event.start)):
            logging.info("OutlookRoomRepository: no currently running event")
        elif not self._is_adhoc(event):
            logging.info("OutlookRoomRepository: current event is no ad hoc booking")
        else:
            now = datetime.datetime.now(datetime.timezone.utc)
            delta = now - event.start
            if delta > datetime.timedelta(minutes=1):
                # only retain events in calendar that took more than a minute
                event.end = now
                event.save()
            else:
                event.delete()
            logging.info("OutlookRoomRepository: cancelled event {0}, {1}, {2}".format(event.subject, event.start, event.end))

    def _get_calendar(self, name=None):
        token_path = pathlib.Path() / 'mrd'
        token_filename = 'o365_token.txt'
        token_backend = FileSystemTokenBackend(token_path=token_path, token_filename=token_filename)

        account = Account(credentials=self._credentials, scopes=self._scopes, token_backend=token_backend)
        schedule = account.schedule()
        if name is not None:
            return schedule.get_calendar(calendar_name=name)

        return schedule.get_default_calendar()

    def _is_adhoc(self, event):
        if event is None:
            return False
        else:
            return event.organizer.address.lower() == self._room_id.lower() \
                and event.subject == self._ad_hoc_subject
