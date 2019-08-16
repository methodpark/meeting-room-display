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

import mrd.rooms as rooms


class EventPortMock(rooms.EventPort):
    def __init__(self):
        super(EventPortMock, self).__init__()
        self.count = 0

    def occupation_changed(self, occupation):
        self.count = self.count + 1

    def incorrect_configuration(self):
        pass

    def no_network_connection(self):
        pass


class CompositeEventPortTest(unittest.TestCase):
    def test__occupation_changed__distributes_event_so_adapters(self):
        adapter1 = EventPortMock()
        adapter2 = EventPortMock()
        composite_event_port = rooms.CompositeEventPort([adapter1, adapter2])

        composite_event_port.occupation_changed(None)

        call_counts = [a.count for a in [adapter1, adapter2]]
        self.assertEqual(sum(call_counts, 0), 2, "Each event port adapter should have been called")
