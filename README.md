# f451 Labs Enviro+ module v1.2.2

## Overview

The *f451 Labs Enviro+* module encapsulates the drivers for the [Pimoroni Enviro+ HAT](https://shop.pimoroni.com/products/enviro?variant=31155658457171) within a single class. This module provides a standard set of methods to read sensor data and display content to the onboard 0.96" LCD (160x80).

## Install

This module is not (yet) available on PyPi. However, you can still use `pip` to install the module directly from GitHub (see below).

### Dependencies

This module is dependent on the following libraries:

- [enviroplus-python](https://github.com/pimoroni/enviroplus-python/)

NOTE: Only install `enviroplus-python` library on a device that also has the physical Enviro+ HAT installed.

NOTE: You can run this app in demo mode on (almost) any device even without the Enviro+ HAT. It will then create random numbers and can send output to the `logger` when log level is `DEBUG` or when `--debug` flag is used.

### Installing from GitHub using `pip`

You can use `pip install` to install this module directly from GitHub as follows:

```bash
$ pip install 'f451-enviro @ git+https://github.com/mlanser/f451-enviro.git'
```

## How to use

### Enviro+ Device

The `Enviro` object makes it easy to interact with the *Enviro+* device. The methods of this object help read sensor data, display data to the 0.96" LCD, etc., and using the module is straightforward. Simply `import` it into your code and instantiate an `Enviro` object which you can then use throughout your code.

```Python
# Import f451 Labs Enviro+
from f451_enviro.enviro import Enviro

# Initialize device instance which includes all sensors
# and LCD display on Enviro+
myEnviro = Enviro({
    "ROTATION": 90,
    "DISPLAY": 'sparkles',
    "PROGRESS": 0,
    "SLEEP": 600    
})
myEnviro.display_init()

print(f"TEMP:     {round(myEnviro.get_temperature(), 1)} C")
print(f"PRESSURE: {round(myEnviro.get_pressure(), 1)} hPa")
print(f"HUMIDITY: {round(myEnviro.get_humidity(), 1)} %")
```

### Enviro+ Data

The *f451 Labs Enviro+* module also includes an `EnviroData` object and a few other helper objects. These objects are designed to simplify storing and managing sensor data. The `EnviroData` object implements so-called [double-ended queues ('deque')](https://docs.python.org/3/library/collections.html#deque-objects) which makes it easy to add and retrieve data. To use these objects in your code, simply `import` them into your code and instantiate an `EnviroData` object.

```Python
# Import f451 Labs SenseHat Data
from f451_enviro.enviro import EnviroData

maxLen = 10     # Max length of queue
defVal = None   # Default value for initialization

myData = EnviroData(defVal, maxlen)

# Assuming we have instantiated the Enviro object as 'myEnviro' we
# can then read and store sensor data right into the data queues
myData.temperature.data.append(myEnviro.get_temperature())
myData.pressure.data.append(myEnviro.get_pressure())
myData.humidity.data.append(myEnviro.get_humidity())
```

### Enviro Module Demo

The **f451 Labs Enviro** module includes a (fairly) comprehensive demo which you can launch as follows:

```bash
$ python -m f451_sensehat.en_demo [<options>]

# If you have installed the 'f451 Labs Enviro' module 
# using the 'pip install'
$ en_demo [<options>]

# Use CLI arg '-h' to see available options
$ en_demo -h 
```

This demo does not display much in the console. Instead the focus is on displaying data on the Enviro+ 0.96" LCD. You can switch between different display modes by covering the light sensor for a fraction of a second.  

You can also also adjust the settings in the `sh_demo_settings.toml` file. For example, if you change the `PROGRESS` setting to 1, then the Enviro+ LCD will display a progress bar indicating when the next (simulated) upload will happen.

There is also a 'sleep mode' which turns off the display automatically after a certain amount of time. You can also turn on the LCD display back on by covering the light sensor again.

```toml
# File: sh_demo_settings.toml
...
PROGRESS = 1    # [0|1] - 1 = show upload progress bar on LCD
SLEEP = 600     # Delay in seconds until screen is blanked
...
```

Finally you can exit the application using the `ctrl-c` command. If you use the `--uploads N` commandline argument, then the application will stop after *N* (simulated) uploads.

```bash
# Stop after 10 uploads
$ en_demo --uploads 10

# Show 'progress bar' regardless of setting in 'toml' file
$ en_demo --progress

# Show specific display mode (e.g. 'rndpcnt') regardless 
# of setting in 'toml' file
$ en_demo --dmode rndpcnt
```

## How to test

The tests are written for [pytest](https://docs.pytest.org/en/7.1.x/contents.html) and we use markers to separate out tests that require the actual Sense HAT hardware. Some tests do not rely on the hardware to be present. However, those tests rely on the `pytest-mock` module to be present.

```bash

# Run all tests (except marked 'skip')
$ pytest

# Run tests with 'hardware' marker
$ pytest -m "hardware"

# Run tests without 'hardware' marker
$ pytest -m "not hardware"
```
