"""Test cases for f451 Labs SenseHat Data module.

These test cases only use fake/random data to test these 
data structures and associated methods.
"""

import pytest
from src.f451_enviro.enviro_data import EnviroData, TEMP_UNIT_F, TEMP_UNIT_K


# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
DEF_VAL = 0
MAX_LEN = 100


# =========================================================
#          F I X T U R E S   A N D   H E L P E R S
# =========================================================
@pytest.fixture
def valid_str():
    return 'Hello world'


@pytest.fixture
def valid_struct():
    return EnviroData(DEF_VAL, MAX_LEN)


# =========================================================
#                    T E S T   C A S E S
# =========================================================
def test_dummy(valid_str):
    """Dummy test case.

    This is only a placeholder test case.
    """
    assert valid_str == 'Hello world'


def test_append_data(valid_struct):
    testData = valid_struct

    testData.temperature.data.append(100)
    testData.pressure.data.append(200)
    testData.humidity.data.append(300)

    # These deque's have fixed lengths
    assert len(testData.temperature.data) == MAX_LEN
    assert len(testData.pressure.data) == MAX_LEN
    assert len(testData.humidity.data) == MAX_LEN

    # We append data at the end of the deque
    assert testData.temperature.data[-1] == 100
    assert testData.pressure.data[-1] == 200
    assert testData.humidity.data[-1] == 300

    # But we do not change start of the deque
    assert testData.temperature.data[0] == DEF_VAL
    assert testData.pressure.data[0] == DEF_VAL
    assert testData.humidity.data[0] == DEF_VAL


def test_convert_data(valid_struct):
    testData = valid_struct

    testData.temperature.data.append(100)

    tempC = testData.temperature.as_dict()
    tempF = testData.temperature.as_dict(TEMP_UNIT_F)
    tempK = testData.temperature.as_dict(TEMP_UNIT_K)

    assert tempC['data'][-1] == 100
    assert float(tempF['data'][-1]) == 212.0
    assert float(tempK['data'][-1]) == 373.15
