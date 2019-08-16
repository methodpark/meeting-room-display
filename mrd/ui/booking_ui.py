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

import time
import kivy

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import ObjectProperty


class ScreenManagement(ScreenManager):
    def switch_to(self, screen):
        self.current = screen


class MainScreen(Screen):
    clock_label = ObjectProperty()
    room_free_label = ObjectProperty()
    appointment_name_label = ObjectProperty()
    date_label = ObjectProperty()
    room_name_label = ObjectProperty()

    def __init__(self, manager, *args, **kwargs):
        super(Screen, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.update_clock, 1)
        self.room_name_label.text = 'MedDev Meeting Room Test'
        self.room_free_label.text = 'frei'
        self.appointment_name_label.text = 'bis 12:00 Uhr'
        self._manager = manager

    def update_clock(self, *args):
        self.date_label.text = time.strftime('%Y-%m-%d')
        self.clock_label.text = time.strftime('%H:%M:%S')

    def on_touch_down(self, screen):
        self._manager.switch_to('booking_screen')


class BookingScreen(Screen):
    def __init__(self, manager, *args, **kwargs):
        super(BookingScreen, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self._exit, 30)
        self._manager = manager

    def _exit(self, *args):
        self._manager.switch_to('main_screen')


class KivyUI(App):
    def __init__(self):
        super(KivyUI, self).__init__()

    def build(self):
        manager = ScreenManagement()
        manager.add_widget(MainScreen(manager))
        manager.add_widget(BookingScreen(manager))
        return manager

    def start(self):
        self.run()


if __name__ == '__main__':
    app = KivyUI()
    app.start()
