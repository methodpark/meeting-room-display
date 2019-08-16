test:
	python -m unittest discover -p "*_test.py"

deps:
	pip install -r requirements.txt

mqtt-broker:
	apt-get install mosquitto

# https://github.com/jgarff/rpi_ws281x
# https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
scons:
	sudo apt-get install gcc make build-essential python-dev git scons swig

ws281x:
	echo "tbd"

run:
	python3 -m mrd.display_main

run-backlight:
	sudo python -m mrd.backlight.mqtt_service & sudo echo $$! > .mqtt-service.pid

stop-backlight:
	if [ -e .mqtt-service.pid ]; then \
		( sudo kill -SIGTERM $$(cat .mqtt-service.pid) & sudo rm .mqtt-service.pid ) || true; \
	fi;
	sudo python -m mrd.backlight.turn_off_backlight

restart-backlight-service:
	systemctl restart backlight

restart-mrd-service:
	systemctl restart mrd

restart-services: restart-backlight-service restart-mrd-service

.PHONY: test
