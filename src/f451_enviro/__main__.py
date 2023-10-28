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
    print("Beep boop!")


if __name__ == "__main__":
    main()