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
import gettext
import logging
import os
import qrcode
import sys
import threading
import time

import mrd.time_util as datetime

formatter = logging.Formatter("[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s", "%H:%M:%S")
console = logging.StreamHandler()
console.setFormatter(formatter)
sys._kivy_logging_handler = console

import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.clock import Clock, mainthread

from kivy.properties import ObjectProperty, StringProperty, NumericProperty

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.write()

kivy.require('1.8.0')

# dictionary for translation of labels
_ = None

def fallback(msgstr):
    return msgstr


HELL = "hells_kitchen@example.org"

def is_hells_kitchen(room_id):
    cur_local_time_in_sec_since_epoch = calendar.timegm(time.localtime(time.time()))
    weekday = int(time.strftime("%w", time.gmtime(cur_local_time_in_sec_since_epoch)))
    hour = int(time.strftime("%H", time.gmtime(cur_local_time_in_sec_since_epoch)))
    # show flames every Thursday after 5 pm
    return weekday == 4 and hour >= 17 and room_id == HELL

class ScreenManagement(ScreenManager):

    def __init__(self, app, *args, **kwargs):
        super(ScreenManagement, self).__init__(*args, **kwargs)
        self._app = app
        self._free_until = 0

    def switch_to(self, screen):
        if self.has_screen(screen):
            logging.info("Switching to '%s'", screen)
            self.current = screen
        else:
            logging.warning("ScreenManager has no screen '%s'", screen)

    def book_room_async(self, time_from, time_to):
        logging.info("Book room for {0} minutes".format(datetime.seconds(time_to - time_from)))
        thread = threading.Thread(target=self._app.book_room, args=(time_from, time_to))
        thread.start()
        return thread

    def cancel_appointment_async(self):
        logging.info("Cancel current ad hoc meeting")
        thread = threading.Thread(target=self._app.cancel_appointment)
        thread.start()
        self.set_password(None)
        return thread

    def set_free_until(self, time_in_sec=3600):
        self._free_until = time_in_sec

    def set_password(self, pw):
        self.get_screen('numpad_screen')._set_password(pw)

    @property
    def free_until(self):
        return self._free_until

    @property
    def is_occupied(self):
        return self._app.is_occupied()

    @property
    def is_adhoc(self):
        appointment = self._app._get_occupation().current_event
        if appointment is not None:
            return appointment.is_adhoc
        else:
            return False

    @property
    def is_connected_to_network(self):
        return self._app.is_connected_to_network()

    @property
    def is_adhoc_booking_allowed(self):
        return self._app.is_adhoc_booking_allowed()

    @property
    def ask_for_adhoc_password(self):
        return self._app.ask_for_adhoc_password()


class BookingScreen(Screen):
    TIMEOUT_INTERVAL = 30
    time_button_left = ObjectProperty()
    time_button_right = ObjectProperty()
    confirm_booking_button = ObjectProperty
    cancel_booking_button = ObjectProperty
    booking_label = ObjectProperty()

    def __init__(self, manager, *args, **kwargs):
        super(BookingScreen, self).__init__(*args, **kwargs)
        self._manager = manager
        self.booking_label.text = _("Book room:")
        self.confirm_booking_button.text = _("confirm")
        self.cancel_booking_button.text = _("cancel")

    def render_screen(self, _):
        pass

    def on_pre_enter(self):
        self._set_toggle_button_state('down', 'normal')
        self._set_toggle_button_text(self._manager.free_until)

    def _set_toggle_button_text(self, free_until):
        if free_until >= datetime.minutes(60):
            self.time_button_left.text = "30 Min."
            self.time_button_right.text = "60 Min."
        else:
            minutes = datetime.seconds(free_until)
            date_diff = minutes - (minutes % 15)
            if date_diff < 15:
                self._manager.switch_to("main_screen")
            elif date_diff > 30:
                self.time_button_left.text = "30 Min."
                self.time_button_right.text = str(date_diff) + " Min."
            else:
                self.time_button_left.text = str(date_diff) + " Min."
                self.time_button_right.text = ""
                self.time_button_right.background_color = (0, 0, 0, 1)
                self.time_button_right.disabled = True

    def _set_toggle_button_state(self, left, right):
        self.time_button_left.state = left
        self.time_button_right.state = right

    def on_enter(self):
        Clock.schedule_interval(self._exit, self.TIMEOUT_INTERVAL)

    def on_leave(self):
        Clock.unschedule(self._exit)
        self.time_button_left.background_color = (1, 1, 1, 1)
        self.time_button_right.background_color = (1, 1, 1, 1)
        self.time_button_right.disabled = False
        self.time_button_left.disabled = False

    def _exit(self, *args):
        logging.info("BookingScreen reached timeout, returning to main_screen")
        # previously determined password needs to be reset
        self._manager.set_password(None)
        self._manager.switch_to("main_screen")

    def book_room(self):
        if self.time_button_left.state == 'down':
            duration = int(self.time_button_left.text[:2])
        elif self.time_button_right.state == 'down':
            duration = int(self.time_button_right.text[:2])
        else:
            self._manager.switch_to(self.name)
            return

        time_from = time.time()
        time_to = time_from + datetime.minutes(duration)

        # handle information to app
        self._manager.book_room_async(time_from, time_to).join()
        self._manager.switch_to('main_screen')

    def show_flames(self):
        pass

    def hide_flames(self):
        pass


class CancellationScreen(Screen):
    TIMEOUT_INTERVAL = 30
    cancellation_label = ObjectProperty()
    confirm_cancellation_button = ObjectProperty()
    cancel_cancellation_button = ObjectProperty()

    def __init__(self, manager, *args, **kwargs):
        super(CancellationScreen, self).__init__(*args, **kwargs)
        self._manager = manager
        self.cancellation_label.text = _("Terminate:")
        self.cancel_cancellation_button.text = _("cancel")

    def on_enter(self):
        Clock.schedule_interval(self._exit, self.TIMEOUT_INTERVAL)

    def on_leave(self):
        Clock.unschedule(self._exit)

    def _exit(self, *args):
        logging.info("cancellation screen: reached timeout, returning to main screen")
        self._manager.switch_to("main_screen")

    def cancel_appointment(self):
        self._manager.cancel_appointment_async().join()
        self._manager.switch_to('main_screen')

    def render_screen(self, _):
        pass

    def show_flames(self):
        pass

    def hide_flames(self):
        pass


class MainScreen(Screen):
    clock_label = ObjectProperty()
    room_free_label = ObjectProperty()
    main_layout = ObjectProperty()
    date_label = ObjectProperty()
    room_name_label = ObjectProperty()
    touch_image = ObjectProperty()
    capacity_label = ObjectProperty()
    capacity_image = ObjectProperty()
    red = NumericProperty(0)
    green = NumericProperty(0)
    blue = NumericProperty(1)
    logo_image = ObjectProperty()

    def __init__(self, manager, *args, **kwargs):
        super(MainScreen, self).__init__(*args, **kwargs)
        self._manager = manager

    def _schedule_clock_interval(self):
        Clock.schedule_interval(self.update_clock, 1)

    def _unschedule_clock_interval(self):
        Clock.unschedule(self.update_clock)

    def on_enter(self):
        self._schedule_clock_interval()
        self.update_clock()

    def on_leave(self):
        self._unschedule_clock_interval()

    def update_clock(self, *args):
        self.date_label.text = time.strftime(_("%a, %Y/%m/%d"))
        self.clock_label.text = time.strftime('%H:%M:%S')

    def display_room_as_free(self, occupation):
        self.room_free_label.text = _("available")
        self.appointment_name_label.text = ""
        self.show_icons()
        self.set_frame_color(0, 1, 0)
        self.display_touch_availability(True)
        if occupation.upcoming_event_today is None:
            date_until = _("no events today")
            title = ""
            self._manager.set_free_until()
        else:
            date_until = _("until") + " " + time.strftime("%H:%M", time.localtime(occupation.upcoming_event_today.date_from)) + " Uhr"
            title = occupation.upcoming_event_today.title
            date_diff = int(occupation.upcoming_event_today.date_from - time.time())
            self._manager.set_free_until(date_diff - datetime.minutes(1))  # leave one minute as buffer
            if date_diff <= 15 * 60:
                self.set_frame_color(1, 1, 0)

        self.appointment_time_label.text = date_until
        self.upcoming_appointment_label.text = title

    def display_room_as_occupied(self, occupation):
        self.room_free_label.text = _("occupied")
        self.show_icons()
        capacity = self._manager._app.get_capacity()
        if not occupation.current_event.is_adhoc and capacity != "":
            self.capacity_label.text = "{}/{}".format(occupation.current_event.num_attendees, capacity)

        self.appointment_name_label.text = occupation.current_event.title
        self.upcoming_appointment_label.text = ""
        time_from = time.strftime("%H:%M", time.localtime(occupation.current_event.date_from))
        time_to = time.strftime("%H:%M", time.localtime(occupation.current_event.date_until))
        if time_from == time_to:
            self.appointment_time_label.text = _("all-day")
        else:
            self.appointment_time_label.text = time_from + " - " + time_to
        self.set_frame_color(1, 0, 0)
        if not self._manager.is_adhoc:
            self._manager.switch_to(self.name)  # when occupation changes during BookingScreen
            self.display_touch_availability(False)

    def display_touch_availability(self, roomFreeOrClearable):
        if self._manager.is_adhoc_booking_allowed == "True" and roomFreeOrClearable:
            self.touch_image.source = "mrd/ui/img/touch.png"
        else:
            self.touch_image.source = "mrd/ui/img/no-touch.png"

    def display_room_as_unconnected(self):
        self.hide_icons()
        self.no_connection_image.opacity = 1
        self.room_free_label.text = _("Error")
        self.appointment_name_label.text = _("no connection to wifi")
        self.upcoming_appointment_label.text = ""
        self.appointment_time_label.text = ""
        self.set_frame_color(0, 0, 1)

    def render_screen(self, occupation):
        self.no_connection_image.opacity = 0

        if occupation is None:
            self.display_room_as_unconnected()
        elif occupation.is_occupied:
            self.display_room_as_occupied(occupation)
        else:
            self.display_room_as_free(occupation)

    def on_touch_down(self, screen):
        if not self._manager.is_occupied and self._manager.is_connected_to_network:
            logging.info("MainScreen received touch down, booking adhoc allowed: %s", self._manager.is_adhoc_booking_allowed)
            if self._manager.is_adhoc_booking_allowed == "True":
                if self._manager.ask_for_adhoc_password == "True":
                    self._manager.switch_to('numpad_screen')
                else:
                    self._manager.switch_to('booking_screen')
        elif self._manager.is_adhoc:
            if self._manager.get_screen('numpad_screen')._password is None:
                self._manager.switch_to('cancellation_screen')
            else:
                self._manager.switch_to('numpad_screen')

        return super(Screen, self).on_touch_down(screen)

    def set_frame_color(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b

    def show_flames(self):
        self.flames_image_left.opacity = 0.8
        self.flames_image_right.opacity = 0.8

    def hide_flames(self):
        self.flames_image_left.opacity = 0
        self.flames_image_right.opacity = 0

    def show_icons(self):
        self.touch_image.opacity = 0.8
        self.logo_image.opacity = 1
        capacity = self._manager._app.get_capacity()
        self.capacity_image.opacity = 0.8 if capacity != "" else 0
        self.capacity_label.text = capacity

    def hide_icons(self):
        self.touch_image.opacity = 0
        self.capacity_image.opacity = 0
        self.capacity_label.text = ""


class NumPadScreen(Screen):
    TIMEOUT_INTERVAL = 30
    password_label = ObjectProperty()

    def __init__(self, manager, *args, **kwargs):
        super(NumPadScreen, self).__init__(*args, **kwargs)
        self._manager = manager
        self._password = None
        self.cancel_button.text = _("cancel")

    def on_pre_enter(self):
        minutes = datetime.seconds(self._manager.free_until)
        date_diff = minutes - (minutes % 15)
        if date_diff < 15:
            self._manager.switch_to("main_screen")

        if self._password is None:
            self.room_name_label.text = _("Set password for canceling:")
        else:
            self.room_name_label.text = _("Insert determined password:")

    def on_enter(self):
        Clock.schedule_interval(self._exit, self.TIMEOUT_INTERVAL)

    def on_leave(self):
        Clock.unschedule(self._exit)
        self.password_label.text = ""

    def add_digit(self, val):
        if "<" in self.password_label.text or ">" in self.password_label.text:
            self.password_label.text = ""

        self.password_label.text += val

    def remove_digit(self):
        if "<" in self.password_label.text or ">" in self.password_label.text:
            self.password_label.text = ""
        else:
            self.password_label.text = self.password_label.text[:-1]

    def handle_password(self, pw):
        if self._password is None:
            self._set_password(pw)
            self._manager.switch_to('booking_screen')
        elif self._password == pw:
            self._manager.switch_to('cancellation_screen')
        else:
            logging.warning("given password is incorrect: '%s'" % pw)
            self.password_label.text = "<" + _("Error") + ">"

    def _set_password(self, pw):
        self._password = pw if pw != "" else None
        logging.info("setting password to '%s'" % self._password)

    def _exit(self, *args):
        logging.info("NumPadScreen reached timeout, returning to main_screen")
        self._manager.switch_to("main_screen")

    def render_screen(self, _):
        pass

    def show_flames(self):
        pass

    def hide_flames(self):
        pass


class PendingScreen(Screen):
    TIMEOUT_INTERVAL = 10
    pending_label = ObjectProperty()
    room_name_label = ObjectProperty()

    def __init__(self, manager, *args, **kwargs):
        super(PendingScreen, self).__init__(*args, **kwargs)
        self._manager = manager
        self.pending_label.text = _("pending ...")
        self.room_name_label.text = ""

    def on_enter(self):
        Clock.schedule_interval(self._exit, self.TIMEOUT_INTERVAL)

    def on_leave(self):
        Clock.unschedule(self._exit)

    def _exit(self, *args):
        logging.info("PendingScreen reached timeout, returning to main screen")
        self._manager.switch_to("main_screen")

    def render_screen(self, _):
        pass

    def show_flames(self):
        pass

    def hide_flames(self):
        pass


class UnconfiguredScreen(Screen):
    ssid = StringProperty()
    url = StringProperty()
    password = StringProperty()
    hostname_image = ObjectProperty()
    configure_label = ObjectProperty()
    open_label = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(UnconfiguredScreen, self).__init__(*args, **kwargs)
        self.ssid = kwargs['ssid']
        self.password = kwargs['password']

        self.url = "http://{}/".format(kwargs['url'])
        self.hostname_image.source = self.create_qr_code(self.url)

        self.configure_label.text = "[i]" + _("To configure your device connect to:") + "[/i]"
        self.open_label.text = "[i]" + _("and open") + "[/i]\n[b]{}[/b]".format(self.url)

    def create_qr_code(self, url):
        img = qrcode.make(url)
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, "img/hostname_qr.png")

        with open(path, 'wb') as out_file:
            img.save(out_file, 'PNG')
            out_file.flush()
            os.fsync(out_file)
            out_file.close()

        return path

    def render_screen(self, _):
        pass


class KivyUI(App):
    def __init__(self, rooms_app, dictionary=None):
        super(KivyUI, self).__init__()
        self.rooms_app = rooms_app
        self.logger = logging.getLogger("kivy")

        # set up message catalog access
        global _
        _ = fallback if dictionary is None else dictionary.gettext

    def on_stop(self, *_):
        if self.manager.has_screen('unconfigured_screen'):
            path = self.manager.get_screen('unconfigured_screen').hostname_image.source
            logging.info("remove hostname qr code image: '%s'" % path)
            os.remove(path)

        self.logger.info("Application is being stopped, notifying app")
        self.rooms_app.on_exit()

    @mainthread
    def occupation_changed(self, occupation):
        self.logger.info("Received occupation_changed from application")
        if self.rooms_app.is_occupied() and is_hells_kitchen(self.rooms_app.get_room_id()):
            self._set_screen_labels("Hell's Kitchen")
            self._show_flames()
        else:
            self._hide_flames()
            self._set_screen_labels(self.rooms_app.get_room_name())
        self.screen.render_screen(occupation)

    @mainthread
    def no_network_connection(self):
        self.logger.warning("Received no_network_connection from application")
        name = "main_screen"
        self.screen = self.manager.get_screen(name)
        self.manager.switch_to(name)
        self.screen.render_screen(None)

    @mainthread
    def incorrect_configuration(self, msg=""):
        logging.warning("Received incorrect configuration state")
        screen_name = "unconfigured_screen"
        if not self.manager.has_screen(screen_name):
            self.screen = UnconfiguredScreen(ssid=self.rooms_app.hotspot.ssid,
                                             password=self.rooms_app.hotspot.password,
                                             url=self.rooms_app.hotspot.url)

            self.manager.add_widget(self.screen)
        else:
            self.screen = self.manager.get_screen(screen_name)

        self.screen.display_heading.text = '[b]{}[/b]'.format(_(msg))
        self.manager.switch_to(screen_name)

    @mainthread
    def render_initial_state(self):
        screen_name = "main_screen"
        self.screen = self.manager.get_screen(screen_name)
        self.manager.switch_to(screen_name)

    @mainthread
    def shut_down(self):
        logging.info("Shut down KivyUI App")
        self.stop()

    def build(self):
        self.manager = ScreenManagement(self.rooms_app, transition=NoTransition())
        self.screen = PendingScreen(self.manager)

        self.manager.add_widget(self.screen)  # pending screen on default
        self.manager.add_widget(MainScreen(self.manager))

        if self.rooms_app.is_configured:
            self.manager.add_widget(BookingScreen(self.manager))
            self.manager.add_widget(NumPadScreen(self.manager))
            self.manager.add_widget(CancellationScreen(self.manager))
            self._set_screen_labels(self.rooms_app.get_room_name())

        return self.manager

    def _set_screen_labels(self, label):
        for screen in self.manager.screens:
            if screen.name != 'numpad_screen':
                screen.room_name_label.text = label

    def _show_flames(self):
        for screen in self.manager.screens:
            screen.show_flames()

    def _hide_flames(self):
        for screen in self.manager.screens:
            screen.hide_flames()

    def start(self):
        self.run()
