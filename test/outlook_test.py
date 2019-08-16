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

import mrd.time_util as datetime
import logging
import unittest
import time

import mrd.outlook as outlook
from mrd.mocks.event_mock import EventStates, set_auth_error_true


class OutlookRoomRepositoryTest(unittest.TestCase):
    #time_string = u'1971-01-01T00:00:00Z'
    id = "dummy_room@example.org"
    password = "secret"

    def setUp(self):
        use_mock = True
        self.backend = outlook.OutlookRoomRepository(self.id, self.password, use_mock)

    def test__call_fetch_calendar_twice__returns_same_object(self):
        self.backend.fetch_calendar()
        fst_calendar = self.backend.calendar

        self.backend.fetch_calendar()
        snd_calendar = self.backend.calendar

        self.assertEqual(fst_calendar, snd_calendar)

    def test__fetch_calendar__raises_error(self):
        set_auth_error_true()

        self.assertRaises(outlook.AuthenticationFailureError, self.backend.fetch_calendar())

    def test__fetch_calendar__returns_calendar(self):
        self.backend.fetch_calendar()

        self.assertIsNotNone(self.backend.calendar)

    def test__get_appointment__with_elapsed_event__returns_none(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.ELAPSED)

        now = time.time()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertIsNone(appointment)

    def test__get_appointment__returns_running_event(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.RUNNING)

        now = time.time()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertLess(appointment.date_from, now)
        self.assertGreater(appointment.date_until, now)
        self.assertIsNotNone(appointment.title)

    def test__get_appointment__returns_upcoming_event(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.UPCOMING)

        now = time.time()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertLessEqual(int(now) + 15*60, appointment.date_from)
        self.assertGreater(appointment.date_from, int(now))
        self.assertGreater(appointment.date_until, appointment.date_from)
        self.assertIsNotNone(appointment.title)

    def test__get_appointment__returns_future_event(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.FUTURE)

        now = time.time()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertGreater(appointment.date_until, appointment.date_from)
        self.assertGreater(appointment.date_from, now + 15*60)
        self.assertIsNotNone(appointment.title)

    def test__book_room__returns_30_minutes_ad_hoc_meeting(self):
        self.backend.fetch_calendar()

        time_from = time.time()
        time_to = time_from + 30*60
        appointment = self.backend.book_room(time_from, time_to)

        self.assertEqual(appointment.date_from, int(time_from))
        self.assertGreater(appointment.date_until, appointment.date_from)
        self.assertIsNotNone(appointment.title)
        self.assertTrue(appointment.is_adhoc)

    def test__cancel_running_adhoc_meeting__deletes_event(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.ADHOC)

        now = time.time()
        adhoc_meeting = self.backend.get_next_state_changing_appointment_up_to_midnight(now)
        self.backend.cancel_running_adhoc_meeting()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertTrue(adhoc_meeting.is_adhoc)
        self.assertIsNone(appointment)

    def test__cancel_running_adhoc_meeting__deletes_event_not(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.RUNNING)

        now = time.time()
        adhoc_meeting = self.backend.get_next_state_changing_appointment_up_to_midnight(now)
        self.backend.cancel_running_adhoc_meeting()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertFalse(adhoc_meeting.is_adhoc)
        self.assertIsNotNone(appointment)

    def test__cancel_running_adhoc_meeting__without_running_event(self):
        self.backend.fetch_calendar()
        self.backend.calendar._set_event_state(EventStates.FUTURE)

        now = time.time()
        self.backend.cancel_running_adhoc_meeting()
        appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(now)

        self.assertFalse(appointment.is_adhoc)
        self.assertIsNotNone(appointment)
