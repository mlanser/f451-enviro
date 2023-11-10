# f451 Labs Enviro+ module v0.0.1

## Overview

The *f451 Labs Enviro+* module encapsulates the drivers for the [*Pimoroni Enviro+* HAT](https://shop.pimoroni.com/products/enviro?variant=31155658457171) within a single class. This module provides a standard set of methods to read sensor data and display content to the onboard 0.96" LCD (160x80).

## Install

This module is not (yet) available on PyPi. however, you can still use `pip` to install the module directly from Github (see below).

### Dependencies

This module is dependent on the following libraries:

- [enviroplus-python](https://github.com/pimoroni/enviroplus-python/)

### Installing from Github using `pip`

You can use `pip install` to install this module directly from Github as follows:

Using HTTPS:

```bash
$ pip install 'f451-enviro @ git+https://github.com/mlanser/f451-enviro.git'
```

Using SSH:

```bash
$ pip install 'f451-enviro @ git+ssh://git@github.com:mlanser/f451-enviro.git'
```

## How to use

Using the module is straightforward. Simply `import` it into your code and instantiate an `Enviro` object which you can then use throughout your code.

```Python
# Import f451 Labs Enviro+
from f451_enviro.enviro import Enviro

# Initialize device instance which includes all sensors
# and LCD display on Enviro+
myEnviro = Enviro({
    "ROTATION": 90,
    "DISPLAY": 0,
    "PROGRESS": 0,
    "SLEEP": 600    
})
myEnviro.display_init()

print(f"TEMP:     {round(myEnviro.get_temperature(), 1)} C")
print(f"PRESSURE: {round(myEnviro.get_pressure(), 1)} hPa")
print(f"HUMIDITY: {round(myEnviro.get_humidity(), 1)} %")
```
