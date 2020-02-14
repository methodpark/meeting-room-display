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
from mrd.time_util import convert_secs_since_epoch_to_string
from O365 import Account
from pathlib import Path

BASEDIR = Path(__file__).parents[1]


def gen_token_file(con):
    print("Please visit the following url and paste the result url into the command line!")
    url = con.get_authorization_url()
    print(url)
    result_url = input("Paste the result url here: ")
    return con.request_token(result_url, store_token=True)


path = BASEDIR / 'mrd/configuration.ini'

if not path.exists():
    print("No valid configuration file at", path.absolute())
    print("Could not generate token file")
    exit(0)

config = ConfigParser()
config.read(str(path))
items = dict(config.items('RoomInformation'))

CLIENT_ID = items['client_id']
CLIENT_SECRET = items['client_secret']
MAIL_ID = items['id']

print("Generate token for id", CLIENT_ID, "with secret", CLIENT_SECRET)

scopes = ['offline_access', 'Calendars.ReadWrite']
path = BASEDIR / "mrd/o365_token.txt"

credentials = (CLIENT_ID, CLIENT_SECRET)
account = Account(credentials)
if account.authenticate(scopes=scopes):
    print('Authenticated')
#con = Connection(credentials=(CLIENT_ID, CLIENT_SECRET), scopes=scopes, token_file_name=path)

# if not con.check_token_file():
#     print("No valid token found. Starting authentication process for <%s> ..." % MAIL_ID)
#     if gen_token_file(con):
#         print("Successfully stored token file at", path.absolute())
#     else:
#         print("Failed to store token file")
# else:
#     token = json.load(path.absolute().open())
#     print("Valid token found at", path.absolute())
#     print("access_token=", token['access_token'])
#     print("expires_at=", convert_secs_since_epoch_to_string(token['expires_at']))
