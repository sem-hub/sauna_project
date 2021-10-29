# Sauna project

The project was mad for control temperature in sauna's steam room and
temperature and humidity in rest room with NanoPI NEO2 board (but you can
use it on any SMC board without a modification).

## Sensors
It uses DS18B20 temperature sensor for steam room and AM2301(DH22)
temperature/humidity sensor for rest room.

It outputs parameters and time on TM1637 display.

I took TM1637 driver from https://github.com/WaltonSimons/TM1637 and 
modified it a little.

Drivers for DS18B20 and DH22 I wrote from scratch.

## WEB
You can control the parameters with a simple HTTPS server (www/). You need
to generate a self-signed sertificate (www/server.pem) for it.

## Requirements
The project require RPi.GPIO python module. But native RPi.GPIO wants only
Raspberry Pi. So, you need proprietary verion of the module. If you use
a custom Linux image (I use armbian for NanoPI NEO2) you have the module
preinstalled. For NanoPI see details [here](https://wiki.friendlyarm.com/wiki/index.php/RPi.GPIO_:_NanoPi_NEO/NEO2/Air_GPIO_Programming_with_Python)

Also the project uses rpyc python module for communication:
```
pip install rpyc
