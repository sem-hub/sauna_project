import re
import RPi.GPIO as GPIO

class DS18B20:
    __w1_file = ''

    def __init__(self, pin: int, file: str):
        self.__w1_file = file
        self.__valid = False
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN)
    def read(self) -> float:
        temperature = 0.0
        try:
            with open(self.__w1_file) as handler:
                for line in handler:
                    match = re.search('t=(\d+)', line)
                    if match != None:
                        temperature = float(match.group(1))/1000
                        self.__valid = True
        except:
            self.__valid = False
            print("w1 file error")
        return temperature
    def is_valid(self):
        return self.__valid
