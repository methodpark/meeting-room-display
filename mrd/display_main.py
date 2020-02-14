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

import argparse
import configparser
import gettext
import locale
import logging
import os
import os.path

from .ui import ui as ui
from . import app
from . import rooms
from . import outlook

from .backlight.backlight import BackLight
from .mocks import room_mock

from . import network


def read_configuration():
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "configuration.ini")
    default_path = os.path.join(my_path, "configuration.default.ini")

    if os.path.exists(path):
        logging.info("Reading configuration from path %s", path)
        config = configparser.ConfigParser()
        config.read(default_path)
        config.read(path)
        return config
    else:
        logging.warning("No config file found at path %s", path)
        return None


def read_room_information(config):
    if config is None:
        logging.info("Found no configuration, starting in `Unconfigured` state")
        return None

    room_information = dict(config.items('RoomInformation'))

    return rooms.RoomInformation(room_information['id'],
                                 room_information['name'],
                                 room_information['password'],
                                 room_information['adhoc'],
                                 room_information['adhoc_ask_for_password'],
                                 room_information['capacity'],
                                 room_information['client_id'],
                                 room_information['client_secret'])


def determine_language(config):
    lang = 'de_DE'  # default language
    if config is None:
        logging.info("Found no configuration, setting language to default (%s)" % lang)
    else:
        lang = dict(config.items('RoomInformation'))['language']
        if lang == "de": # locale.setlocale() doesn't support "de"
            lang = "de_DE"
        logging.info("Setting language to %s" % lang)

    # Set internal locale for date/time formatting
    try:
        locale.setlocale(locale.LC_TIME, "{}.UTF-8".format(lang))
    except locale.Error:
        logging.warning('Unable to set locale to "{}"; falling back to default'.format(lang))

    # Set language for gettext translations
    translator = gettext.translation('mrd', 'locale', fallback=True, languages=[lang])
    return translator


def determine_network():
    if os.name == 'nt':
        logging.warning("Running on Windows, assuming network is connected for now.")
        return network.AlwaysConnected()
    else:
        return network.DefaultWifi()


def parse_command_line_args():
    parser = argparse.ArgumentParser(description="Run MRD")
    parser.add_argument("--nooutlook", help="Start with mock backend instead of outlook backend", default=False, required=False, action="store_true")
    return parser.parse_args()


if __name__ == '__main__':

    logging.info("Application starting")

    config = read_configuration()  # None if configuration.ini does not exist
    room_information = read_room_information(config)
    translator = determine_language(config)
    network = determine_network()

    args = parse_command_line_args()

    if config is not None and not args.nooutlook:
        logging.info("Starting with outlook repository, for room %s with id %s", room_information.name, room_information.id)
        logging.info("Allow booking adhoc meetings: %s", room_information.adhoc)
        logging.info("Adhoc meeting password required: %s", room_information.adhoc_ask_for_password)
        backend = outlook.OutlookRoomRepository(room_information.id, room_information.client_id, room_information.client_secret)
    else:
        logging.info("Starting with mock repository")
        backend = room_mock.AlternatingOccupation()

    event_port = rooms.CompositeEventPort()

    rooms_app = app.MeetingRoomApp(backend, room_information, event_port, network)
    rooms_app.setDaemon(True)

    ui = ui.KivyUI(rooms_app, translator)

    event_port.add_adapter(ui)
    event_port.add_adapter(BackLight())

    rooms_app.start()
    ui.start()
