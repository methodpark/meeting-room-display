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

import json

from configparser import ConfigParser
from O365 import Connection
from pathlib import Path

BASEDIR = Path(__file__).parents[1]

path = BASEDIR / 'mrd/configuration.ini'

if not path.exists():
    print("No valid configuration file at", path.absolute())
    print("Could not refresh token file")
    exit(0)

config = ConfigParser()
config.read(str(path))
items = dict(config.items('RoomInformation'))

CLIENT_ID = items['client_id']
CLIENT_SECRET = items['client_secret']

scopes = ['offline_access', 'https://graph.microsoft.com/Calendars.ReadWrite']
path = BASEDIR / 'mrd/o365_token.txt'
con = Connection(credentials=(CLIENT_ID, CLIENT_SECRET), scopes=scopes, token_file_name=path)

if not con.check_token_file():
    print("No valid token found at", path.absolute())
    print("Please run 'scripts/generate_token.py' first...")
else:
    con.get_session()
    con.refresh_token()
    token = json.load(path.absolute().open())
    print("Successfully updated token in", path.absolute())
    print("refresh_token=", token['refresh_token'])
