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
KWD_TST_VAL = "TST_VAL"

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
def config():
    settings = "src/f451_enviro/settings.toml"
    try:
        with open(Path(__file__).parent.parent.joinpath(settings), mode="rb") as fp:
            config = tomllib.load(fp)
    except tomllib.TOMLDecodeError:
        pytest.fail("Invalid 'settings.toml' file")      
    except FileNotFoundError:
        pytest.fail("Missing 'settings.toml' file")      

    return config


@pytest.fixture(scope="session")
def device_default():
    device = Enviro()
    return device


@pytest.fixture(scope="session")
def device_config(config):
    device = Enviro()
    return device


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_dummy(valid_str):
    """Dummy test case.
    
    This is only a placeholder test case.
    """
    assert valid_str == "Hello world"


def test_get_CPU_temp_mock(device_default, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_CPU_temp", return_value=BME280_TEMP_MIN)
    cpuTemp = device_default.get_CPU_temp()
    assert cpuTemp == BME280_TEMP_MIN


@pytest.mark.hardware
def test_get_CPU_temp(device_default):
    try:
        cpuTemp = device_default.get_CPU_temp()
    except FileNotFoundError:
        pass
    else:        
        assert cpuTemp >= float(BME280_TEMP_MIN)


def test_get_proximity_mock(device_default, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_proximity", return_value=1500)
    proximity = device_default.get_proximity()
    assert proximity == 1500


@pytest.mark.hardware
def test_get_proximity(device_default):
    proximity = device_default.get_proximity()
    assert proximity >= float(LTR559_LUX_MIN)


def test_get_lux_mock(device_default, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_lux", return_value=LTR559_LUX_MIN)
    lux = device_default.get_lux()
    assert lux == LTR559_LUX_MIN


@pytest.mark.hardware
def test_get_lux(device_default):
    lux = device_default.get_lux()
    assert lux >= float(LTR559_LUX_MIN)


def test_get_pressure_mock(device_default, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_pressure", return_value=BME280_PRESS_MIN)
    pressure = device_default.get_pressure()
    assert pressure == BME280_PRESS_MIN


@pytest.mark.hardware
def test_get_pressure(device_default):
    pressure = device_default.get_pressure()
    assert pressure >= float(BME280_PRESS_MIN)


def test_get_humidity_mock(device_default, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_humidity", return_value=BME280_HUMID_MIN)
    humidity = device_default.get_humidity()
    assert humidity == BME280_HUMID_MIN


@pytest.mark.hardware
def test_get_humidity(device_default):
    humidity = device_default.get_humidity()
    assert humidity >= float(BME280_HUMID_MIN)


def test_get_temperature_mock(device_default, mocker):
    mocker.patch("src.f451_enviro.enviro.Enviro.get_temperature", return_value=BME280_TEMP_MIN)
    temperature = device_default.get_temperature()
    assert temperature == BME280_TEMP_MIN


@pytest.mark.hardware
def test_get_temperature(device_default):
    temperature = device_default.get_temperature()
    assert temperature >= float(BME280_TEMP_MIN)


def test_get_gas_data_mock(device_default, mocker):
    class FakeGasData:
        def __init__(self):
            self.oxidising = 24000
            self.reducing = 24000
            self.nh3 = 24000

    mocker.patch("src.f451_enviro.enviro.Enviro.get_gas_data", return_value=FakeGasData())
    data = device_default.get_gas_data()
    assert data.oxidising == 24000


@pytest.mark.hardware
def test_get_gas_data(device_default):
    data = device_default.get_gas_data()
    assert float(data.oxidising) >= 0.0


def test_get_particles_mock(device_default, mocker):
    class FakeParticleData:
        def __init__(self):
            self.data = float(PMS5003_MIN)

    mocker.patch("src.f451_enviro.enviro.Enviro.get_particles", return_value=FakeParticleData())
    particles = device_default.get_particles()
    assert particles.data == float(PMS5003_MIN)


@pytest.mark.hardware
def test_get_particles(device_default):
    particles = device_default.get_particles()
    assert particles.data >= float(PMS5003_MIN)


def test_display_init_mock(device_config, mocker):
    testDev = device_config
    mocker.patch("src.f451_enviro.enviro.Enviro.display_init")
    testDev.display_init()
    testDev.display_init.assert_called_once()


@pytest.mark.hardware
def test_display_init(device_config):
    testDev = device_config
    assert testDev._img is None
    assert testDev._draw is None
    assert testDev._fontLG is None
    assert testDev._fontSM is None

    testDev.display_init()
    assert testDev._img is not None
    assert testDev._draw is not None
    assert testDev._fontLG is not None
    assert testDev._fontSM is not None


@pytest.mark.skip(reason="Is it worth testing?")
def test_display_on_mock(device_config, mocker):
    testDev = device_config
    mocker.patch("src.f451_enviro.enviro.Enviro.display_on")
    testDev.display_on()
    testDev.display_on.assert_called_once()


@pytest.mark.skip(reason="Is it worth testing?")
def test_display_off_mock(device_config, mocker):
    testDev = device_config
    mocker.patch("src.f451_enviro.enviro.Enviro.display_off")
    testDev.display_off()
    testDev.display_off.assert_called_once()


@pytest.mark.skip(reason="Is it worth testing?")
def test_display_blank_mock(device_config, mocker):
    testDev = device_config
    mocker.patch("src.f451_enviro.enviro.Enviro.display_blank")
    testDev.display_blank()
    testDev.display_blank.assert_called_once()


@pytest.mark.skip(reason="Is it worth testing?")
def test_display_reset_mock(device_config, mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_sparkle_mock(device_config, mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_as_graph_mock(device_config, mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_as_text_mock(device_config, mocker):
    pass


@pytest.mark.skip(reason="TO DO")
def test_display_progress_mock(device_config, mocker):
    pass
