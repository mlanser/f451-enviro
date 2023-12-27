"""Custom class for demo data.

This class defines a data structure that can be used 
to manage misc. demo data. This object follows overall 
design of Enviro+ Data object, but is customized for
random demo data collected in the demo application.

Dependencies:
    TBD
"""

from collections import deque
import f451_enviro.enviro_data as f451EnviroData


# =========================================================
#                     M A I N   C L A S S
# =========================================================
class DemoData:
    """Data structure for holding and managing demo data.

    This class follows same principles and design as used
    with the 'SystemData' and 'SenseData' classes.

    Attributes:
        number1: random number
        number2: random number

    Methods:
        as_list: returns a 'list' with data from each attribute as 'dict'
    """

    def __init__(self, defVal, maxLen):
        """Initialize data structurte.

        Args:
            defVal: default value to use when filling up the queues
            maxLen: max length of each queue

        Returns:
            'dict' - holds entiure data structure
        """
        self.rndnum = f451EnviroData.EnviroObject(
            deque([defVal] * maxLen, maxlen=maxLen),
            (1, 200),  # min/max range for valid data
            'km/h',
            [None, None, None, None],
            'Demo Speed',
        )
        self.rndpcnt = f451EnviroData.EnviroObject(
            deque([defVal] * maxLen, maxlen=maxLen),
            (0, 100),  # min/max range for valid data
            '%',
            [10, 30, 70, 90],
            'Demo Pcnt',
        )

    def as_list(self):
        return [
            self.rndnum.as_dict(),
            self.rndpcnt.as_dict(),
        ]

    def as_dict(self):
        return {
            'number1': self.rndnum.as_dict(),
            'number2': self.rndpcnt.as_dict(),
        }
