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
import os
import subprocess
import threading
import time
from enum import Enum

from . import rooms
from . import time_util
from mrd.outlook import AuthenticationFailureError


CHECK_STATUS_TIMEOUT_IN_SECS = 10
ADMIN_GPIO_CHANNEL = 40

try:
    import RPi.GPIO as GPIO
except ImportError:
    from mrd.network import DummyGPIO
    GPIO = DummyGPIO()

class AppStates(Enum):
    UNCONFIGURED = 1
    CONFIGURED = 2

class Hotspot(object):
    def __init__(self, ssid='<SSID>', password='<PASSWORD>', url='<URL>'):
        self.ssid = ssid
        self.password = password
        self.url = url


def to_occupation(appointment):
    if appointment is None:
        return rooms.Occupation(None, None)

    if time_util.is_in_future(appointment.date_from):
        return rooms.Occupation(None, appointment)
    else:
        return rooms.Occupation(appointment, None)


class MeetingRoomApp(threading.Thread):
    NO_HOTSPOT_ERROR_MSG = "Not able to start hotspot mode,\n    please contact supervisor!"
    WELCOME_MSG = "Welcome to MP Meeting Room Display!"
    INCORRECT_CONFIG_MSG = "Incorrect username or password,\nplease update configuration file!"

    appointment = None

    def __init__(self, backend, room_information, event_port, network):
        super(MeetingRoomApp, self).__init__()
        self.backend = backend
        self.room_information = room_information
        self.event_port = event_port
        self.network = network
        self._state = AppStates.CONFIGURED if room_information is not None else AppStates.UNCONFIGURED

    def _fetch_appointment(self):
        self.appointment = self.backend.get_next_state_changing_appointment_up_to_midnight(time.time())
        logging.info("Got appointment %s", self.appointment)

    def _update_room_data_periodically(self):
        logging.info("Starting update loop")
        while self._is_running:
            try:
                if self.is_connected_to_network():
                    logging.info("Fetching room data")
                    self._update_room_data()
                else:
                    self.event_port.no_network_connection()

                time.sleep(CHECK_STATUS_TIMEOUT_IN_SECS)
            except Exception as e:
                logging.error("Exception in update loop %s", e)

    def _get_occupation(self):
        return to_occupation(self.appointment)

    def _update_room_data(self):
        self._fetch_appointment()
        self._is_occupied = self.appointment is not None
        self.event_port.occupation_changed(self._get_occupation())

    def _wait_for_network_connection(self):
        while self._is_running and not self.is_connected_to_network():
            self.event_port.no_network_connection()
            time.sleep(CHECK_STATUS_TIMEOUT_IN_SECS)

    def _admin_detected_on_startup(self, channel):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # check if channel is grounded
        val = GPIO.input(channel) == GPIO.LOW

        logging.info("Run admin mode: %s" % val)
        return val

    def run(self):
        self._is_running = True
        if not self.is_configured \
                or not self.is_connected_to_network() \
                or self._admin_detected_on_startup(ADMIN_GPIO_CHANNEL):
            logging.info("Not starting any polling")
            self.hotspot = self._start_hotspot()
            if self.hotspot is None:
                self.hotspot = Hotspot()  # mock object
                self.event_port.incorrect_configuration(self.NO_HOTSPOT_ERROR_MSG)
            else:
                self.event_port.incorrect_configuration(self.WELCOME_MSG)
        else:
            self._wait_for_network_connection()
            try:
                logging.info("Try to connect with exchange calendar")
                self.backend.fetch_calendar()
            except AuthenticationFailureError as e:
                # first try to fetch data failed, probably caused by wrong credentials
                logging.info("Exception while fetching calendar: %s", e.message)
                self._state = AppStates.UNCONFIGURED
                self.hotspot = self._start_hotspot()
                if self.hotspot is None:
                    self.hotspot = Hotspot()  # mock object
                    self.event_port.incorrect_configuration(self.NO_HOTSPOT_ERROR_MSG)
                else:
                    self.event_port.incorrect_configuration(self.INCORRECT_CONFIG_MSG)

                return

            logging.info("Starting normal operation")
            # everything initialized correctly, inform backend and start fetching events
            self.event_port.render_initial_state()
            self._update_room_data_periodically()

    def _start_hotspot(self):
        path = "/usr/bin/mrd_hotspot"
        if os.path.isfile(path):
            logging.info("Try to start hotspot")
            if subprocess.call(['sudo', path, 'start'], shell=False) != 0:
                # not able to start hotspot mode
                logging.error("Subprocess returned with error code")
            else:
                try:
                    hostname = self.network.get_hostname()
                    url = "{0}.local".format(hostname)
                    if hostname == "":
                        url = self.network.get_ip_address()
                except IOError:
                    logging.warning("Could not find ip address for given ifname")
                    url = "<URL>"

                logging.info("Hotspot running with local domain '%s'", url)
                ssid, pw = self._read_hostapd_conf()
                return Hotspot(ssid, pw, url)
        else:
            logging.warning("Could not start hotspot, no such file '%s'", path)

        # either an error occurred or hotspot not installed properly
        return None

    def _stop_hotspot(self):
        path = "/usr/bin/mrd_hotspot"
        if os.path.isfile(path):
            logging.info("Stop Hotspot mode")
            subprocess.call(['sudo', path, 'stop'], shell=False)
        else:
            logging.warning("could not stop hotspot, no such file '%s'", path)

        self.hotspot = None

    def _read_hostapd_conf(self):
        path = "/etc/hostapd/hostapd.conf"
        ssid = "<NO SSID DETECTED>"
        pw = "<NO PW DETECTED>"

        if os.path.isfile(path):
            file = open(path, "r").read()
            for line in file.splitlines():
                if line.startswith("ssid="):
                    ssid = line.split('=', 1)[1]
                elif line.startswith("wpa_passphrase="):
                    pw = line.split('=', 1)[1]
        else:
            logging.warning("file %s does not exist", path)

        return ssid, pw

    def get_room_id(self):
        return self.room_information.id

    def get_capacity(self):
        return self.room_information.capacity

    def on_exit(self):
        logging.info("App received closing signal. Exiting thread, notifying backlight.")
        self.event_port.shut_down()
        self._is_running = False

    def get_room_name(self):
        return self.room_information.name

    def get_room_password(self):
        return self.room_information.password

    def book_room(self, time_from, time_to):
        appointment = self.backend.book_room(time_from, time_to)
        self._update_room_data()
        return appointment

    def cancel_appointment(self):
        self.backend.cancel_running_adhoc_meeting()
        self._update_room_data()

    def is_occupied(self):
        if self.appointment is None:
            return False
        else:
            return time_util.is_date_in_span(self.appointment.date_from, self.appointment.date_until, time.time())

    def is_connected_to_network(self):
        return self.network.is_connected()

    def is_adhoc_booking_allowed(self):
        return self.room_information.adhoc

    def ask_for_adhoc_password(self):
        return self.room_information.adhoc_ask_for_password

    @property
    def state(self):
        return self._state

    @property
    def is_configured(self):
        return self.state == AppStates.CONFIGURED
