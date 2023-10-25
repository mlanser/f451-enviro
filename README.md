# f451 Labs Uploader module

## Overview

The *f451 Labs Uploader* module encapsulates the *Adafruit IO* REST and MQTT clients, as well as the *Arduino Cloud* client within a single class. Most *f451 Labs* projects upload to and/or receive data from one or both of these services, and the `Uploader` class simplifies these tasks by standardizing send and receive methods, and so on.

## Install

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Convallis a cras semper auctor neque vitae.

### Dependencies

This module is dependent on the following libraries:

- [logging](https://docs.python.org/3/howto/logging.html)
- [pprint](https://docs.python.org/3/library/pprint.html)

### Installing from Github using `pip`

You can use `pip install` to install this module directly from Github as follows:

Using HTTPS:

```bash
$ pip install 'f451-uploader @ git+https://github.com/mlanser/f451-uploader.git'
```

Using SSH:

```bash
$ pip install 'f451-uploader @ git+ssh://git@github.com:mlanser/f451-uploader.git'
```

## How to use

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Convallis a cras semper auctor neque vitae.

```Python
# ??? ...
uploader = Uploader()

# ... ???
uploader = Uploader(....)
```
