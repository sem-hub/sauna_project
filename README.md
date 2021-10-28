# Sauna project

The project was mad for control temperature in sauna's steam room and
temperature and humidity in rest room with NanoPI NEO2 board.

# Sensors
It uses DS18B20 temperature sensor for steam room and AM2301(DH22)
temperature/humidity sensor for rest room.

It outputs parameters and time on TM1637 display.

I took TM1637 driver from https://github.com/WaltonSimons/TM1637 and 
modified it a little.

Drivers for DS18B20 and DH22 I wrote from scratch.

# WEB
You can control the parameters with a simple HTTPS server (www/). You need
to generate a self-signed sertificate (www/server.pem) for it.

# Requirements
It uses rpyc python module for communication:
pip install rpyc
