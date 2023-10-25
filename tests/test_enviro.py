"""Test cases for f451 Labs Enviro+ module.

Some of these test cases will collect sample data from the 
sensors on and/or will display info on the
0.96" LCD on the Enviro+ HAT.

However, many tests can be run without the attached hardware
using the mock unit.
"""

import pytest
import sys
import logging
from pathlib import Path

from src.f451_enviro.enviro import Enviro

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# =========================================================
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return "Hello world"


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_dummy(valid_str):
    """Dummy test case.
    
    This is only a placeholder test case.
    """
    assert valid_str == "Hello world"
