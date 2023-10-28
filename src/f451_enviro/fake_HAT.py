"""Mock version of Pimoroni Enviro+ library.

This mock version of the Pimoroni Enviro+ library can be 
used when running the demo on a device without access to
the Enviro+ HAT. It mimicks the Enviro+ sensors by generating
random values within the limits of the actual hardware.
"""

import random
from typing import Any


# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
BME280_TEMP_MIN = -40   # Unit: C
BME280_TEMP_MAX = 85    
BME280_PRESS_MIN = 300  # Unit: hPa
BME280_PRESS_MAX = 1100
BME280_HUMID_MIN = 0    # Unit: %
BME280_HUMID_MAX = 100

LTR559_LUX_MIN = 0.01
LTR559_LUX_MAX = 64000.0
LTR559_PROX = 1500

PMS5003_MIN = 0.3       # Unit: um
PMS5003_MAX = 10.1      # [>0.3, >0.5, >1.0, >2.5, >10]

ST7735_WIDTH = 160
ST7735_HEIGHT = 80


# =========================================================
#                H E L P E R   C L A S S E S
# =========================================================
class FakeSubST7735:
    def __init__(self, *args, **kwargs):
        self.width = ST7735_WIDTH
        self.height = ST7735_HEIGHT

    def begin(self):
        pass    


class FakeST7735:
    def __init__(self, *args, **kwargs):
        self.ST7735 = FakeSubST7735()


class FakeLTR559:
    def __init__(self, *args, **kwargs):
        self.active = True

    def get_proximity(self):
        return random.randint(LTR559_PROX, LTR559_PROX + 1)

    def get_lux(self):
        return random.randint(1, int(LTR559_LUX_MAX)*100) / 100


class FakeSMBus:
    def __init__(self, *args, **kwargs):
        self.active = True


class FakeBME280:
    def __init__(self, *args, **kwargs):
        self.active = True

    def get_temperature(self):
        return random.randint(BME280_TEMP_MIN * 10, BME280_TEMP_MAX * 10) / 10
    
    def get_pressure(self):
        return random.randint(BME280_PRESS_MIN * 10, BME280_PRESS_MAX * 10) / 10
    
    def get_humidity(self):
        return random.randint(BME280_HUMID_MIN * 10, BME280_HUMID_MAX * 10) / 10


class FakeGasData:
    def __init__(self):
        self.oxidising = random.randint(10000, 24000)   # TO DO: fix magic num
        self.reducing = random.randint(10000, 24000)    # TO DO: fix magic num
        self.nh3 = random.randint(10000, 24000)         # TO DO: fix magic num


class FakeEnviroPlus:
    def __init__(self, *args, **kwargs):
        self.active = True

    def read_all(self):
        return FakeGasData()


class FakePMS5003Data():
    def pm_ug_per_m3(self, *args):
        return random.randint(int(PMS5003_MIN * 10), int(PMS5003_MAX * 10)) / 10
    

class FakePMS5003:
    def __init__(self, *args, **kwargs):
        self.active = True

    def read(self):
        return FakePMS5003Data()
    
    
class FakeReadTimeoutError(Exception):
    pass


class FakeSerialTimeoutError(Exception):
    pass
