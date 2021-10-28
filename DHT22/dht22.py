import RPi.GPIO
import time

def conv_delay_to_bin(count):
    if count > 10:
        return '1'
    else:
        return '0'

def check_checksum(bytes_array) -> bool:
    return ((int(bytes_array[0], 2) + int(bytes_array[1], 2) + int(bytes_array[2], 2) + int(bytes_array[3], 2)) & 255) == int(bytes_array[4], 2)
    
class DHT22:
    def __init__(self, pin: int):
        self.__pin = pin
        self.__valid = True
    def __collect_data(self):
        # data is an array of high edge delays
        data = []
        last = 1
        # Read 40 bits. It's 80 edge changes + 3 first edges of data ready
        #  signal (we ignore them).
        i = 0
        while i < 83:
            counter = 0
            current = RPi.GPIO.input(self.__pin)
            while current == last:
                counter += 1
                if counter == 255:
                    break
                current = RPi.GPIO.input(self.__pin)

            if counter == 255:
                break
            last = current
            if i >= 3 and last == 0:
                data.append(counter)
            i += 1

        bytes_array = []
        bit_count = 0
        byte = ''
        for n in data:
            byte += conv_delay_to_bin(n)
            bit_count += 1
            if bit_count == 8:
                bit_count = 0
                bytes_array.append(byte)
                byte = ''
        return bytes_array

    def read(self) -> (int, int):
        RPi.GPIO.setup(self.__pin, RPi.GPIO.OUT)
        # Set bus low to signal we are ready to read data
        RPi.GPIO.output(self.__pin, RPi.GPIO.LOW)
        time.sleep(0.005)
        # Setup pin to input
        RPi.GPIO.setup(self.__pin, RPi.GPIO.IN, RPi.GPIO.PUD_UP)
        bytes_array = self.__collect_data()
        if len(bytes_array) != 5:
            self.__valid=False
            print('Wrong bytes count')
            return (0.0, 0.0)
        if not check_checksum(bytes_array):
            self.__valid = False
            print('Checksum error')
            return (0.0, 0.0)
        humid = int(bytes_array[0]+bytes_array[1], 2)/10
        temp = 0.0
        # Check for bellow zero
        if bytes_array[2][0] == '1':
            temp = -(int(bytes_array[2][1:len(bytes_array[2])]+bytes_array[3], 2)/10)
        else:
            temp = int(bytes_array[2]+bytes_array[3], 2)/10

        self.__valid = True
        return (humid, temp)

    def is_valid(self):
        return self.__valid
