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

from abc import ABCMeta, abstractmethod
import logging


class Appointment(object):
    def __init__(self, date_from, date_until, title, num_attendees, is_adhoc=False):
        self.date_from = date_from
        self.date_until = date_until
        self.title = title
        self.is_adhoc = is_adhoc
        self.num_attendees = num_attendees


class RoomInformation(object):
    def __init__(self, id, name, password, adhoc, adhoc_ask_for_password, capacity, client_id, client_secret):
        self._id = id
        self._name = name
        self._password = password
        self._adhoc = adhoc
        self._adhoc_ask_for_password = adhoc_ask_for_password
        self._capacity = capacity
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def password(self):
        return self._password

    @property
    def adhoc(self):
        return self._adhoc

    @property
    def adhoc_ask_for_password(self):
        return self._adhoc_ask_for_password

    @property
    def capacity(self):
        return self._capacity

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

class Occupation(object):
    def __init__(self, current_event, upcoming_event):
        self._current_event = current_event
        self._is_occupied = current_event is not None
        self._upcoming_event = upcoming_event

    @property
    def is_occupied(self):
        return self._is_occupied

    @property
    def upcoming_event_today(self):
        return self._upcoming_event

    @property
    def current_event(self):
        return self._current_event


class RoomRepositoryPort(object, metaclass=ABCMeta):
    """Port for accessing and storing data"""

    @abstractmethod
    def get_next_state_changing_appointment_up_to_midnight(self, time_in_sec_since_epoch):
        """Return the next appointment from the given time up until midnight of today.

        :param time_in_sec_since_epoch: the current time.
        :returns: a instance of `Appointment` or None"""
        pass

    @abstractmethod
    def book_room(self, time_from, time_to):
        """
        :param time_from: seconds since epoch.
        :param time_to: seconds since epoch.
        :returns: a instance of `Appointment` for the newly created appointment or None"""
        pass


class EventPort(object, metaclass=ABCMeta):
    """Port description to distribute events throughout the application"""

    def __init__(self):
        super(EventPort, self).__init__()

    @abstractmethod
    def occupation_changed(self, current_occupation):
        pass

    @abstractmethod
    def no_network_connection(self):
        pass

    @abstractmethod
    def incorrect_configuration(self, msg=""):
        pass

    @abstractmethod
    def render_initial_state(self):
        pass

    @abstractmethod
    def shut_down(self):
        pass


class CompositeEventPort(EventPort):
    """Combine several adapters to the EventPort into one."""
    def __init__(self, adapters=[]):
        super(CompositeEventPort, self).__init__()
        self._adapters = adapters

    def add_adapter(self, adapter):
        self._adapters.append(adapter)

    def occupation_changed(self, current_occupation):
        for adapter in self._adapters:
            adapter.occupation_changed(current_occupation)

    def no_network_connection(self):
        for adapter in self._adapters:
            adapter.no_network_connection()

    def incorrect_configuration(self, msg=""):
        for adapter in self._adapters:
            adapter.incorrect_configuration(msg)

    def render_initial_state(self):
        # should be called only once
        for adapter in self._adapters:
            adapter.render_initial_state()

    def shut_down(self):
        for adapter in self._adapters:
            adapter.shut_down()
