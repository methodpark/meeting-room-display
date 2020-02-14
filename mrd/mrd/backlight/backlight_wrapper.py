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
import time
import colorsys
from neopixel import *


class LEDPort(object):
    """Port description to distribute LED status throughout the application"""
    def __init__(self):
        super(LEDPort, self).__init__()

    def state_changed(self, state):
        logging.warn("Implement me")


class CompositeLEDPort(LEDPort):
    """Combine several adapters to the LEDPort into one."""
    def __init__(self, adapters=[]):
        super(CompositeLEDPort, self).__init__()
        self._adapters = adapters

    def add_adapter(self, adapter):
        self._adapters.append(adapter)

    def state_changed(self, state):
        for adapter in self._adapters:
            adapter.state_changed(state)


class LEDState(object):
    def __init__(self, name, rgb=None):
        logging.info("new LEDState {0}, {1}".format(name, rgb))
        self._name = name
        self._rgb = rgb

    @property
    def name(self):
        return self._name

    @property
    def rgb(self):
        return self._rgb


class BacklightWrapper(LEDPort):

    def __init__(self, package="neopixel"):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filemode='w')
        try:
            if package == "neopixel":
                self.backlight = NeoPixelLight()
                logging.info('{0} successfully imported'.format(package))
            else:
                raise ImportError()

        except:
            self.backlight = BacklightMock()
            logging.warn('ImportError: no module named {0}'.format(package))
            logging.info('run backlight with mock anyway')

    def state_changed(self, state):
        self.backlight.state_changed(state)


class NeoPixelLight(object):
    # LED strip configuration:
    LED_COUNT = 16  # Number of LED pixels.
    LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 100  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
    STRIP_TYPE = ws.WS2811_STRIP_GRB  # set strip type to match the used LED's

    def __init__(self):
        self.strip = self._configure_neopixel()
        self._set_color(255, 0, 0)
        time.sleep(0.5)
        self._set_color(0, 255, 0)
        time.sleep(0.5)
        self._set_color(0, 0, 255)

    def state_changed(self, state):
        name = state.name
        
        if name == 'rgb':
            r, g, b = state.rgb
            self._set_color(r, g, b)
        elif name == 'rainbow':
            self._set_rainbow()
        elif name == 'clear':
            self._clear()
        elif name == 'quit':
            self._shut_down()
        else:
            logging.warn("unknown state name: {0}".format(name))

    def _configure_neopixel(self):
        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
                                       self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS,
                                       self.LED_CHANNEL, self.STRIP_TYPE)
        # Intialize the library (must be called once before other functions).
        strip.begin()
        return strip

    def _set_color(self, r, g, b):
        for i in range(self.strip.numPixels()):
            if Color(r, g, b) != self.strip.getPixelColor(i):
                logging.info("set color to rgb ({0}, {1}, {2})".format(r, g, b))
                self.strip.setPixelColorRGB(i, r, g, b)

        self.strip.show()

    def _set_rainbow(self):
        logging.info("set color to rainbow")
        for i in range(self.strip.numPixels()):
            h = i*360.0/16/360
            (r,g,b) = colorsys.hsv_to_rgb(h,1,1)
            r = int(r*255)
            g = int(g*255)
            b = int(b*255)
            if Color(r, g, b) != self.strip.getPixelColor(i):
                self.strip.setPixelColorRGB(i, r, g, b)

        self.strip.show()

    def _clear(self):
        logging.info("clear neopixel")
        # turn color to white
        self._set_color(255, 255, 255)

    def _shut_down(self):
        logging.info("turn off neopixel")
        # turn color to black / off
        self._set_color(0, 0, 0)


class BacklightMock(object):
    def __init__(self):
        pass

    def state_changed(self, state):
        name = state.name
        if name == 'rgb':
            r, g, b = state.rgb
            logging.info("set_color to ({0}, {1}, {2})".format(r, g, b))
        elif name == 'rainbow':
            logging.info("set color to rainbow")
        elif name == 'clear':
            logging.info("clear backlight")
        elif name == 'quit':
            logging.info("turn off backlight")
        else:
            logging.warn("unknown state name: {0}".format(name))
