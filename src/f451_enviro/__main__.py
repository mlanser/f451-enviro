"""Demo for using f451 Labs Enviro+ Module."""

import time
import sys
import asyncio
from pathlib import Path
from random import randint

from f451_enviro.enviro import Enviro

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# =========================================================
#          G L O B A L S   A N D   H E L P E R S
# =========================================================


# =========================================================
#                    D E M O   A P P
# =========================================================
def main():
    # Get app dir
    appDir = Path(__file__).parent

    # Initialize TOML parser and load 'settings.toml' file
    try:
        with open(appDir.joinpath("settings.toml"), mode="rb") as fp:
            config = tomllib.load(fp)
    except tomllib.TOMLDecodeError:
        sys.exit("Invalid 'settings.toml' file")      

    # Initialize device instance which includes all sensors
    # an d LCD display on Enviro+
    enviro = Enviro(config)
    enviro.display_init()

    tempRaw = enviro.get_temperature()
    pressRaw = enviro.get_pressure()
    humidRaw = enviro.get_humidity()

    print("\n===== [Demo of f451 Labs Enviro+ Module] ======")
    print(f"TEMP:     {tempRaw} C")
    print(f"PRESSURE: {pressRaw} hPa")
    print(f"HUMIDITY: {humidRaw} %")
    # print("Beep boop!")
    print("=============== [End of Demo] =================\n")


if __name__ == "__main__":
    main()