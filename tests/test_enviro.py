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


@pytest.mark.skip(reason="TO DO")
def test_get_CPU_temp(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_proximity(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_lux(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_pressure(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_humidity(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_temperature(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_gas_data(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_get_particles(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_init(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_on(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_off(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_blank(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_reset(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_sparkle(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_as_graph(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_as_text(mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_progress(mocker):
    pass
