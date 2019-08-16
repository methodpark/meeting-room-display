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

from subprocess import call

def enableDisplay():
    backlight = open('/sys/class/backlight/rpi_backlight/bl_power', 'w')
    backlight.write('0')
    backlight.close()

def startServices():
    call(['systemctl', 'restart', 'mrd'], shell=False)
    call(['systemctl', 'restart', 'backlight'], shell=False)
    call(['systemctl', 'restart', 'backlight_status.timer'], shell=False)

enableDisplay()
startServices()

