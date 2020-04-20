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
from O365 import Account, FileSystemTokenBackend
from pathlib import Path

BASEDIR = Path(__file__).parents[1]


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

scopes = ['offline_access', 'https://graph.microsoft.com/Calendars.ReadWrite.Shared']
token_path = BASEDIR / "mrd"
token_filename = "o365_token.txt"
path = token_path / token_filename
token_backend = FileSystemTokenBackend(token_path=token_path, token_filename=token_filename)

account = Account((CLIENT_ID, CLIENT_SECRET), token_backend=token_backend)

if not account.is_authenticated:
    print("No valid token found. Starting authentication process for <%s> ..." % MAIL_ID)
    if account.authenticate(redirect_uri='https://login.microsoftonline.com/common/oauth2/nativeclient', scopes=scopes):
        print("Successfully stored token file at", path.absolute())
    else:
        print("Failed to store token file")
else:
    token = json.load(path.absolute().open())
    print("Valid token found at", path.absolute())
    print("access_token=", token['access_token'])
    print("expires_at=", convert_secs_since_epoch_to_string(token['expires_at']))
