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
from datetime import datetime
import time

OUTLOOK_TIME_STRING = '%Y-%m-%dT%H:%M:%SZ'


def minutes(secs):
    return secs * 60


def seconds(mins):
    return int(mins / 60)


def is_date_in_span(start_in_sec_since_epoch, end_in_sec_since_epoch, date_in_sec_since_epoch):
    return start_in_sec_since_epoch <= date_in_sec_since_epoch <= end_in_sec_since_epoch


def is_in_future(timestamp):
    return time.time() < timestamp


def convert_string_to_secs_since_epoch(time_string):
    return calendar.timegm(time.strptime(time_string, OUTLOOK_TIME_STRING))


def convert_struct_time_to_secs_since_epoch(time_struct):
    return calendar.timegm(time_struct)


def convert_secs_since_epoch_to_string(time_in_sec_since_epoch):
    return time.strftime(OUTLOOK_TIME_STRING, time.gmtime(time_in_sec_since_epoch))


def convert_struct_time_to_string(time_struct):
    return time.strftime(OUTLOOK_TIME_STRING, time_struct)

def convert_secs_since_epoch_to_struct_time(time_in_sec_since_epoch):
    return time.gmtime(time_in_sec_since_epoch)

def convert_datetime_to_secs_since_epoch(datetime):
    return time.mktime(datetime.timetuple())

def convert_secs_since_epoch_to_datetime(time_in_sec_since_epoch):
    return datetime.fromtimestamp(time_in_sec_since_epoch)
