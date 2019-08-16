#!/bin/sh
# https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/

if [ "$#" -ne 1 ] || ! [ -d "$1" ]; then
  echo "Usage: $0 <DIRECTORY>" >&2
  exit 1
fi

# required packages for the WS2812 LED library
sudo apt-get install -y gcc make build-essential python-dev git scons swig

if [ ! -d "$1/../rpi_ws281x" ]; then
  # download the library
  git clone https://github.com/jgarff/rpi_ws281x $1/../rpi_ws281x
fi

cd "$1/../rpi_ws281x"

# In this directory are on the one hand some C files included, which can be easily compiled.
# In order to use them in Python, we need to compile them:
scons

# Here we carry out the installation:
cd python
python3 setup.py build
sudo python3 setup.py install