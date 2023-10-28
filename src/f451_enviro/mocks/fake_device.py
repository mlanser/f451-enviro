"""Mock version of Pimoroni Enviro+ library.

This mock version of the Pimoroni Enviro+ library can be 
used during testing, etc. It mimicks the Enviro+ sensors 
by generating random values within the limits of the 
actual hardware.
"""

import random
from typing import Any


# =========================================================
#                H E L P E R   C L A S S E S
# =========================================================
class FakeSubST7735:
    def __init__(self, *args, **kwargs):
        self.width = 160
        self.height = 80

    def begin(self):
        pass    


class FakeST7735:
    def __init__(self, *args, **kwargs):
        self.ST7735 = FakeSubST7735()


class FakeLTR559:
    def __init__(self, *args, **kwargs):
        self.active = True

    def get_proximity(self):
        return random.randint(1500, 1501)

    def get_lux(self):
        return random.randint(0, 1500)


class FakeSMBus:
    def __init__(self, *args, **kwargs):
        self.active = True


class FakeBME280:
    def __init__(self, *args, **kwargs):
        self.active = True

    def get_temperature(self):
        return random.randint(const.MIN_TEMP * 10, const.MAX_TEMP * 10) / 10
    
    def get_pressure(self):
        return random.randint(const.MIN_PRESS * 10, const.MAX_PRESS * 10) / 10
    
    def get_humidity(self):
        return random.randint(const.MIN_HUMID * 10, const.MAX_HUMID * 10) / 10


class FakeGasData:
    def __init__(self):
        self.oxidising = random.randint(10000, 24000)
        self.reducing = random.randint(10000, 24000)
        self.nh3 = random.randint(10000, 24000)


class FakeEnviroPlus:
    def __init__(self, *args, **kwargs):
        self.active = True

    def read_all(self):
        return FakeGasData()


class FakePMS5003Data():
    def pm_ug_per_m3(self, *args):
        return random.randint(1, 12) / 10
    

class FakePMS5003:
    def __init__(self, *args, **kwargs):
        self.active = True

    def read(self):
        return FakePMS5003Data()
    
    
class FakeReadTimeoutError(Exception):
    pass


class FakeSerialTimeoutError(Exception):
    pass
