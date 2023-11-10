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
#                    D E M O   A P P
# =========================================================
def main():
    # Get app dir
    appDir = Path(__file__).parent

    # Initialize TOML parser and load 'settings.toml' file
    try:
        with open(appDir.joinpath("settings.toml"), mode="rb") as fp:
            config = tomllib.load(fp)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        sys.exit("ERROR: Missing or invalid 'settings.toml' file")      

    # Initialize device instance which includes all sensors
    # an d LCD display on Enviro+
    enviro = Enviro(config)
    enviro.display_init()

    # Display text on LCD
    enviro.display_message("Hello world!")

    tempRaw = round(enviro.get_temperature(), 1)
    pressRaw = round(enviro.get_pressure(), 1)
    humidRaw = round(enviro.get_humidity(), 1)

    print("\n===== [Demo of f451 Labs Enviro+ Module] ======")
    print(f"TEMP:     {tempRaw} C")
    print(f"PRESSURE: {pressRaw} hPa")
    print(f"HUMIDITY: {humidRaw} %")
    print("=============== [End of Demo] =================\n")


if __name__ == "__main__":
    main()