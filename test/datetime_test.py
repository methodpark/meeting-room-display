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

import mrd.time_util as datetime


class DateTimeTest(unittest.TestCase):
    def test__is_date_in_span__is_in_span__returns_true(self):
        now = time.time()
        before_now = now - 100
        after_now = now + 100

        result = datetime.is_date_in_span(before_now, after_now, now)

        self.assertTrue(result)

    def test__is_date_in_span__is_not_in_span__returns_true(self):
        now = time.time()
        before_now = now - 100
        way_before_now = now - 200

        result = datetime.is_date_in_span(way_before_now, before_now, now)

        self.assertFalse(result)

    def test__convert_string_to_secs__epoch_time__returns_true(self):
        time_string = '1970-01-01T00:00:00Z'
        secs = datetime.convert_string_to_secs_since_epoch(time_string)

        result = (secs == 0)

        self.assertTrue(result)

    def test__convert_secs_to_string__epoch_time__returns_true(self):
        secs = 0
        time_string = datetime.convert_secs_since_epoch_to_string(secs)

        result = (time_string == '1970-01-01T00:00:00Z')

        self.assertTrue(result)

    def test__convert_string_to_secs__one_year__returns_true(self):
        time_string = '1971-01-01T00:00:00Z'
        secs = datetime.convert_string_to_secs_since_epoch(time_string)

        secs_per_year = 365 * 24 * 60 * 60
        result = (secs == secs_per_year)

        self.assertTrue(result)

    def test__convert_secs_to_string__one_year__returns_true(self):
        secs = 365 * 24 * 60 * 60
        time_string = datetime.convert_secs_since_epoch_to_string(secs)

        result = (time_string == '1971-01-01T00:00:00Z')

        self.assertTrue(result)

    def test__convert_string_to_secs__valid_input__returns_true(self):
        time_as_outlook_string = '2018-04-25T13:14:15Z'
        expected_epoch_time = 1524662055

        actual_epoch_time = datetime.convert_string_to_secs_since_epoch(time_as_outlook_string)

        self.assertEqual(actual_epoch_time, expected_epoch_time)

    def test__convert_secs_to_string__valid_input__returns_true(self):
        time_as_outlook_string = '2018-04-25T13:14:15Z'
        expected_epoch_time = 1524662055

        actual_time_string = datetime.convert_secs_since_epoch_to_string(expected_epoch_time)

        self.assertEqual(actual_time_string, time_as_outlook_string)
