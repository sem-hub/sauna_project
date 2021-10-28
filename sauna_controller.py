#!/bin/env python3

import configparser
from datetime import timedelta, datetime
import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
import threading
import signal
import time

import DHT22
import DS18B20
import TM1637
from periodic_job import Periodic_job


class RPyCService(rpyc.Service):
    def __init__(self, stor):
        super().__init__()
        self.__stor = stor

    # space separated data
    def exposed_get_data(self):
        data = ''
        if self.__stor.is_steam_valid():
            data += str(my_round(self.__stor.get_steam_temp()*10)/10)+'°'
        else:
            data += 'Error'
        data += ' '
        if self.__stor.is_rest_valid():
            data += str(my_round(self.__stor.get_rest_temp()*10)/10)+'°'
        else:
            data += 'Error'
        data += ' '
        if self.__stor.is_rest_valid():
            data += str(my_round(self.__stor.get_rest_humid()))+'%'
        else:
            data += 'Error'

        return data

class TM1637ex(TM1637.TM1637):
    def __init__(self, cpin, dpin):
        super().__init__(cpin, dpin)

    def clear(self):
        self.set_values([' ', ' ', ' ', ' '])

class Storage:
    def __init__(self):
        self.__rest_room_temp = 0.0
        self.__rest_room_humid = 0.0
        self.__rest_valid = False
        self.__rest_failures = 0
        self.__steam_room_temp = 0.0
        self.__steam_valid = False
        self.__steam_failures = 0

    def get_rest_temp(self) -> str:
        return self.__rest_room_temp

    def get_rest_humid(self) -> str:
        return self.__rest_room_humid

    def get_steam_temp(self) -> str:
        return self.__steam_room_temp

    def set_steam_temp(self, temp: float, valid: bool) -> None:
        if not valid:
            self.__steam_failures += 1
            if self.__steam_failures > 2:
                self.__steam_valid = False
        else:
            self.__steam_room_temp = temp
            self.__steam_failures = 0
            self.__steam_valid = True

    def is_steam_valid(self) -> bool:
        return self.__steam_valid

    def set_rest_params(self, temp: float, humid: float, valid: bool) -> None:
        if not valid:
            self.__rest_failures += 1
            if self.__rest_failures > 2:
                self.__rest_valid = False
        else:
            self.__rest_room_temp = temp
            self.__rest_room_humid = humid
            self.__rest_failures = 0
            self.__rest_valid = True

    def is_rest_valid(self) -> bool:
        return self.__rest_valid

class ProgramStopped(Exception):
    pass

def signal_handler(signum, frame):
    raise ProgramStopped

def read_temp(stor, rest, steam):
    stor.set_steam_temp(steam.read(), steam.is_valid())
    humid, temp = rest.read()
    stor.set_rest_params(temp, humid, rest.is_valid())

class Blink_colon(threading.Thread):
    def __init__(self, display):
        super().__init__()
        self.__disp = display
        self.__stop = False

    def run(self):
        while not self.__stop:
            self.__disp.set_doublepoint(True)
            time.sleep(0.5)
            self.__disp.set_doublepoint(False)
            time.sleep(0.5)
    def stop(self):
        self.__stop = True

def show_time(disp) -> None:
    disp.clear()
    dt = datetime.now()
    str = '{:02}{:02}'.format(dt.hour, dt.minute)
    disp.set_values([c for c in str])

def my_round(n: float) -> int:
    if n-int(n) > 0.5:
        return int(n) + 1
    return int(n)

def show_error(disp) -> None:
    disp.set_values(['E', 'r', 'r', ' '])

def show_value(disp, val: float, kind: str) -> None:
    disp.clear()
    s = str(my_round(val))
    out = []
    if kind == 'T1':
        out.append(' ')
    elif kind == 'T2':
        out.append('A')
    else:
        out.append(' ')

    if val < 10:
        out.append(' ')
    out += [c for c in s]
    if kind == 'H':
        out.append('H')
    else:
        out.append('GR')
    disp.set_values(out)

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    rest_room = DHT22.DHT22(int(config['DHT22']['data_pin']))
    steam_room = DS18B20.DS18B20(int(config['DS18B20']['data_pin']), config['DS18B20']['w1_file'])
    display = TM1637ex(int(config['TM1637']['clock_pin']), int(config['TM1637']['data_pin']))

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    stor = Storage()
    read_temp(stor=stor, rest=rest_room, steam=steam_room)

    rpyc_service = classpartial(RPyCService, stor)
    rpyc_server = ThreadedServer(rpyc_service, port=18888)
    rpyc_thr = threading.Thread(target = rpyc_server.start)
    rpyc_thr.daemon = True
    rpyc_thr.start()

    read_params_job = Periodic_job(interval=timedelta(seconds=3), execute=read_temp, stor=stor, rest=rest_room, steam=steam_room)
    read_params_job.start()

    while True:
        try:
            #print(stor.get_steam_temp(), stor.get_rest_temp(), stor.get_rest_humid())
            blink = Blink_colon(display)
            blink.daemon = True
            blink.start()
            show_time(display)
            time.sleep(4)
            blink.stop()

            if stor.is_steam_valid():
                show_value(display, stor.get_steam_temp(), 'T1')
            else:
                show_error(display)
            time.sleep(3)

            if stor.is_rest_valid():
                show_value(display, stor.get_rest_temp(), 'T2')
                time.sleep(3)

                show_value(display, stor.get_rest_humid(), 'H')
            else:
                show_error(display)
            time.sleep(3)
        except ProgramStopped:
            print('Killed')
            read_params_job.stop()
            display.clear()
            break;

if __name__ == '__main__':
    main()
