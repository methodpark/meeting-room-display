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

from mrd.backlight.backlight_wrapper import BacklightMock, LEDState, CompositeLEDPort


class UnicornMockTests(unittest.TestCase):

    def test__set_free(self):
        backlight = BacklightMock()
        self.assertEqual(backlight.state, None)

        state = LEDState('rgb', (0, 255, 0))
        backlight.state_changed(state)
        self.assertEqual(backlight.state.name, state.name)
        self.assertEqual(backlight.state.rgb, state.rgb)

    def test__set_occupied(self):
        backlight = BacklightMock()
        self.assertEqual(backlight.state, None)

        state = LEDState('rgb', (255, 0, 0))
        backlight.state_changed(state)
        self.assertEqual(backlight.state.name, state.name)
        self.assertEqual(backlight.state.rgb, state.rgb)

    def test__turn_off(self):
        backlight = BacklightMock()
        self.assertEqual(backlight.state, None)

        state = LEDState('clear')
        backlight.state_changed(state)
        self.assertEqual(backlight.state.name, state.name)
        self.assertEqual(backlight.state.rgb, state.rgb)

    def test__shut_down(self):
        backlight = BacklightMock()
        self.assertEqual(backlight.state, None)

        state = LEDState('quit')
        backlight.state_changed(state)
        self.assertEqual(backlight.state.name, state.name)
        self.assertEqual(backlight.state.rgb, state.rgb)


class LEDPortTests(unittest.TestCase):

    def setUp(self):
        self.adapter = BacklightMock()
        self.port = CompositeLEDPort()
        self.port.add_adapter(self.adapter)

    def test__set_free(self):
        state = LEDState('rgb', (255, 0, 0))
        self.port.state_changed(state)
        self.assertEqual(self.adapter.state.name, state.name)
        self.assertEqual(self.adapter.state.rgb, state.rgb)

    def test__set_occupied(self):
        state = LEDState('rgb', (0, 255, 0))
        self.port.state_changed(state)
        self.assertEqual(self.adapter.state.name, state.name)
        self.assertEqual(self.adapter.state.rgb, state.rgb)

    def test__turn_off(self):
        state = LEDState('clear')
        self.port.state_changed(state)
        self.assertEqual(self.adapter.state.name, state.name)
        self.assertEqual(self.adapter.state.rgb, state.rgb)

    def test__shut_down(self):
        state = LEDState('quit')
        self.port.state_changed(state)
        self.assertEqual(self.adapter.state.name, state.name)
        self.assertEqual(self.adapter.state.rgb, state.rgb)
