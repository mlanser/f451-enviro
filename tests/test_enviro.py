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
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return "Hello world"


@pytest.fixture(scope="session")
def default_device():
    device = Enviro()
    return device


# =========================================================
#                    T E S T   C A S E S
# =========================================================
# def test_person_class_with_mock(mocker):
#     """
#     Function to test Person class with mock
#     :param mocker: pytest-mock fixture
#     :return: None
#     """
#     fake_response = {"name": "FAKE_NAME", "age": "FAKE_AGE", "address": "FAKE_ADDRESS"}
#     # Mock the 'Person' class to return a mock object.
#     mocker.patch(
#         "mock_examples.core.Person.get_person_json", return_value=fake_response
#     )

#     # Initalize the Person class with fresh data.
#     person = Person(name="Eric", age=25, address="123 Farmville Rd")
#     actual = person.get_person_json()
#     assert actual == fake_response

def test_dummy(valid_str):
    """Dummy test case.
    
    This is only a placeholder test case.
    """
    assert valid_str == "Hello world"


def test_get_CPU_temp_mock(default_device, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_CPU_temp", return_value=BME280_TEMP_MIN)
    cpuTemp = default_device.get_CPU_temp()
    assert cpuTemp == BME280_TEMP_MIN


@pytest.mark.hardware
def test_get_CPU_temp(default_device):
    try:
        cpuTemp = default_device.get_CPU_temp()
    except FileNotFoundError:
        pass
    else:        
        assert cpuTemp >= float(BME280_TEMP_MIN)


def test_get_proximity_mock(default_device, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_proximity", return_value=1500)
    proximity = default_device.get_proximity()
    assert proximity == 1500


@pytest.mark.hardware
def test_get_proximity(default_device):
    proximity = default_device.get_proximity()
    assert proximity >= float(LTR559_LUX_MIN)


def test_get_lux_mock(default_device, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_lux", return_value=LTR559_LUX_MIN)
    lux = default_device.get_lux()
    assert lux == LTR559_LUX_MIN


@pytest.mark.hardware
def test_get_lux(default_device):
    lux = default_device.get_lux()
    assert lux >= float(LTR559_LUX_MIN)


def test_get_pressure_mock(default_device, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_pressure", return_value=BME280_PRESS_MIN)
    pressure = default_device.get_pressure()
    assert pressure == BME280_PRESS_MIN


@pytest.mark.hardware
def test_get_pressure(default_device):
    pressure = default_device.get_pressure()
    assert pressure >= float(BME280_PRESS_MIN)


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
