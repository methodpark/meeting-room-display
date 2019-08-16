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

import unittest
import time
from mock import MagicMock


import mrd.app
from mrd.rooms import RoomInformation, EventPort, Occupation, Appointment
import mrd.mocks.room_mock as rooms
import mrd.mocks.outlook_mock as outlook

import mrd.network as network

class EventPortMock(object):
    pass



class MeetingRoomAppTests(unittest.TestCase):
    id = "dummy@example.org"
    password = "secret"

    def setUp(self):
        self.event_port = EventPortMock()
        self.network = network.AlwaysConnected()
        self.room_information = RoomInformation(self.id, "Room 1", self.password, "True")
        backend = outlook.OutlookRoomRepositoryMock(self.id, self.password)
        self.app = mrd.app.MeetingRoomApp(backend, self.room_information, self.event_port, self.network)

    def test__init_when_called_with_no_room_information__starts_in_unconfigured_state(self):
        app = mrd.app.MeetingRoomApp(None, None, self.event_port, self.network)

        self.assertEqual(app.state, mrd.app.AppStates.UNCONFIGURED)

    def test__init_when_called_with_room_information__starts_in_configured_state(self):
        self.assertEqual(self.app.state, mrd.app.AppStates.CONFIGURED)

    def test__get_room_id__returns_the_rooms_id(self):
        id = self.app.get_room_id()
        self.assertEqual(self.id, id)

    def test__get_room_name__returns_the_rooms_name(self):
        name = self.app.get_room_name()
        self.assertEqual("Room 1", name)

    def test__get_room_password__returns_the_rooms_password(self):
        password = self.app.get_room_password()
        self.assertEqual(self.password, password)

    def test__update_room_data__notifies_event_port__when_occupation_changes(self):
        self.event_port.occupation_changed = MagicMock()

        app = mrd.app.MeetingRoomApp(rooms.AlternatingOccupation(), self.room_information, self.event_port, self.network)
        app._update_room_data()

        self.event_port.occupation_changed.assert_called_once()

    def test___fetch_appointment__fetches_current_running_appointment_from_backend(self):
        self.app._fetch_appointment()
        appointment = self.app.appointment

        self.assertTrue(appointment is not None)
        self.assertTrue(appointment.date_from < time.time())
        self.assertTrue(appointment.date_until > time.time())

    def test___fetch_appointment__fetches_upcoming_appointment_from_backend(self):
        self.app.backend._begin_for_state_changing_appointment = 1
        self.app._fetch_appointment()
        appointment = self.app.appointment

        self.assertTrue(appointment is not None)
        self.assertTrue(appointment.date_from > time.time())
        self.assertTrue(appointment.date_until > appointment.date_from)

    def test___fetch_appointment__fetches_elapsed_appointment_from_backend(self):
        self.app.backend._begin_for_state_changing_appointment = -1
        self.app._fetch_appointment()
        appointment = self.app.appointment

        self.assertTrue(appointment is None)

    def test__to_occupation__current_appointment__returns_true(self):
        time_from = time.time() - (5 * 60)
        time_until = time_from + (10 * 60)
        title = 'test__to_occupation__title'

        appointment = Appointment(time_from, time_until, title)
        occupation = mrd.app.to_occupation(appointment)

        self.assertTrue(occupation.is_occupied)
        self.assertTrue(occupation.current_event is not None)
        self.assertTrue(occupation.upcoming_event_today is None)

    def test__to_occupation__upcoming_appointment__returns_true(self):
        time_from = time.time() + (5 * 60)
        time_until = time_from + (10 * 60)
        title = 'test__to_occupation__title'

        appointment = Appointment(time_from, time_until, title)
        occupation = mrd.app.to_occupation(appointment)

        self.assertFalse(occupation.is_occupied)
        self.assertIsNone(occupation.current_event)
        self.assertIsNotNone(occupation.upcoming_event_today)
