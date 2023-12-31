"""f451 Labs Enviro+ Device Class.

The Enviro+ Device class includes support for sensosr and 
LCD display included on the Pimoroni Enviro+ HAT.

The class wraps -- and extends as needed -- the methods 
and functions supported by underlying libraries, and also
keeps track of core counters, flags, etc.

TODO: there are a few things that will be adeded as needed including:
 - method to display shapes
 - method to display scrolling text
 - method to display images
 - more/better tests

Dependencies:
 - fonts: https://pypi.org/project/fonts/
 - font-roboto: https://pypi.org/project/font-roboto/
 - Pillow: https://pypi.org/project/Pillow/
 - Pimoroni Enviro+ library: https://github.com/pimoroni/enviroplus-python/  
"""

import time
import colorsys

from random import randint
from subprocess import PIPE, Popen


from . import enviro_data as f451EnviroData

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium  # type: ignore

# Support for ST7735 LCD
try:
    import ST7735
except ImportError:
    from .fake_HAT import FakeST7735 as ST7735

# Support for proximity sensor
try:
    try:
        # Transitional fix for breaking change in LTR559
        from ltr559 import LTR559

        ltr559 = LTR559()
    except ImportError:
        import ltr559
except ImportError:
    from .fake_HAT import FakeLTR559 as ltr559

# Support SMBus
try:
    try:
        from smbus2 import SMBus
    except ImportError:
        from smbus import SMBus
except ImportError:
    from .fake_HAT import FakeSMBus as SMBus

# Support temperature/pressure/humidity sensor
try:
    from bme280 import BME280
except ImportError:
    from .fake_HAT import FakeBME280 as BME280

# Support air quality sensor
try:
    from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError, SerialTimeoutError
except ImportError:
    from .fake_HAT import (
        FakePMS5003 as PMS5003,
        FakeReadTimeoutError as pmsReadTimeoutError,
        FakeSerialTimeoutError as SerialTimeoutError,
    )

# Support Enviro+ gas sensor
try:
    from enviroplus import gas
except ImportError:
    from .fake_HAT import FakeEnviroPlus as gas

__all__ = [
    'Enviro',
    'EnviroError',
    'prep_data',
    'DISPL_SPARKLE',
    'KWD_ROTATION',
    'KWD_DISPLAY',
    'KWD_PROGRESS',
    'KWD_SLEEP',
    'KWD_DISPLAY_TOP_X',
    'KWD_DISPLAY_TOP_Y',
    'KWD_DISPLAY_TOP_BAR',
]


# fmt: off
# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
DEF_ROTATION = 0                # Default display rotation
DEF_SLEEP = 600                 # Default time to sleep (in seconds)
DEF_LCD_OFFSET_X = 1            # Default horizontal offset for LCD
DEF_LCD_OFFSET_Y = 1            # Default vertical offseet for LCD

STATUS_ON = True
STATUS_OFF = False

DISPL_TOP_X = 2                 # X/Y ccordinate of top-left corner for LCD content
DISPL_TOP_Y = 2
DISPL_TOP_BAR = 21              # Height (in px) of top bar
DISPL_LBL_LEN = 4               # Num chars of label to display in top bar

PBAR_HEIGHT = 2                 # Prgress bar height in pixels

PROX_DEBOUNCE = 0.2             # Delay to debounce proximity sensor on 'tap'
PROX_LIMIT = 1500               # Threshold for proximity sensor to detect 'tap'

DISPL_SPARKLE = 'sparkles'      # Name of 'sparkles' view :-)
MAX_SPARKLE_PCNT = 0.05         # 5% sparkles

RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255, 255, 255)

RGB_BLUE = (0, 0, 255)
RGB_CYAN = (0, 255, 255)
RGB_GREEN = (0, 255, 0)
RGB_YELLOW = (255, 255, 0)
RGB_RED = (255, 0, 0)

RGB_CHROME = (219, 226, 233)    # Chrome (lt grey)
RGB_GREY = (67, 70, 75)         # Dark Steel Grey
RGB_GREY2 = (57, 61, 71)        # Anthracite
RGB_PURPLE = (127, 0, 255)
RGB_GREY_BLUE = (33, 46, 82)

# RGB colors and palette for values on combo/text screen
COLOR_PALETTE = [
    RGB_BLUE,                   # Dangerously Low
    RGB_CYAN,                   # Low
    RGB_GREEN,                  # Normal
    RGB_YELLOW,                 # High
    RGB_RED,                    # Dangerously High
]

COLOR_BG = RGB_BLACK            # Default background
COLOR_TXT = RGB_CHROME          # Default text on background
COLOR_PBAR = RGB_CYAN           # Default progress bar
COLOR_PBAR_BG = RGB_GREY_BLUE   # Default prog bar background

FONT_SIZE_SM = 10               # Small font size
FONT_SIZE_MD = 16               # Medium font size
FONT_SIZE_LG = 20               # Large font size
LINE_SPACING = 4                # Line spacing (in pixels) for ImageDraw multiline text

ROTATE_90 = 90                  # Rotate 90 degrees
ROTATE_180 = 180                # Rotate 180 degrees


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_ROTATION = 'ROTATION'
KWD_DISPLAY = 'DISPLAY'
KWD_PROGRESS = 'PROGRESS'
KWD_SLEEP = 'SLEEP'

KWD_DISPLAY_TOP_X = 'TOP_X'
KWD_DISPLAY_TOP_Y = 'TOP_Y'
KWD_DISPLAY_TOP_BAR = 'TOP_BAR'
# fmt: on


# =========================================================
#                        H E L P E R S
# =========================================================
class EnviroError(Exception):
    """Custom exception class"""

    def __init__(self, errMsg='Unknown Enviro+ error'):
        super().__init__(errMsg)


def prep_data(inData, lenSlice=0):
    """Prep data for Enviro+

    This function will filter data to ensure we don't have incorrect
    outliers (e.g. from faulty sensors, etc.). The final data set will
    have only valid values. Any invalid values will be replaced with
    0's so that we can display the set on the Enviro+ LCD.

    This will technically affect the min/max values for the set. However,
    we're displaying this data on an 0.96" LCD. So visual 'accuracy' is
    already less than ideal ;-)

    Args:
        inData: 'DataUnit' named tuple with 'raw' data from sensors
        lenSlice: (optional) length of data slice

    Returns:
        'DataUnit' named tuple with the following fields:
            data   = [list of values],
            valid  = <tuple with min/max>,
            unit   = <unit string>,
            label  = <label string>,
            limits = [list of limits]
    """

    def _is_valid(val, valid, allowNone=True):
        """Verify value 'valid'

        This method allows us to verify that a given
        value falls within the 'valid' ranges are for 
        a given data set. Any value outside the range 
        is considered an error and is replaced by a 
        default value.

        NOTE: This local function is similar to the 'is_valid()' 
              function in f451 Labs Common library. We have a copy
              here so that the f451 Labs SenseHat library does not 
              have another dependency

        Args:
            val: value to check
            valid: 'tuple' with min/max values for valid range
            allowNone: if 'True', then skip compare if 'valid' is 'None

        Returns:
            'True' if value is valid, else 'False'
        """
        if valid is None or not all(valid):
            return allowNone

        if val is not None and any(valid):
            isValid = True
            if valid[0] is not None:
                isValid &= float(val) >= float(valid[0])
            if valid[1] is not None:
                isValid &= float(val) <= float(valid[1])

            return isValid

        return False

    # Size of data slice we want to send to Sense HAT. The 'f451 Labs SenseHat'
    # library will ulimately only display the last 8 values anyway.
    dataSlice = list(inData.data)[-lenSlice:]

    # Return filtered data
    dataClean = [i if _is_valid(i, inData.valid) else 0 for i in dataSlice]

    return f451EnviroData.DataUnit(
        data=dataClean,
        valid=inData.valid,
        unit=inData.unit,
        label=inData.label,
        limits=inData.limits,
    )


# =========================================================
#                     M A I N   C L A S S
# =========================================================
class Enviro:
    """Main Enviro+ class for managing the Pimoroni Enviro+ HAT.

    This class encapsulates all methods required to interact with
    the sensors and the LCD on the Pimoroni Enviro+ HAT.

    NOTE: attributes follow same naming convention as used
    in the 'settings.toml' file. This makes it possible to pass
    in the 'config' object (or any other dict) as is.

    NOTE: we let users provide an entire 'dict' object with settings as
    key-value pairs, or as individual settings. User can combine both and,
    for example, provide a standard 'config' object as well as individual
    settings which could override the values in the 'config' object.

    Example:
        myEnviro = Enviro(config)           # Use values from 'config'
        myEnviro = Enviro(key=val)          # Use val
        myEnviro = Enviro(config, key=val)  # Use values from 'config' and also use 'val'

    Attributes:
        ROTATION:   Default rotation for LCD display - [0, 90, 180, 270]
        DISPLAY:    Default display mode
        PROGRESS:   Show progress bar - [0 = no, 1 = yes]
        SLEEP:      Number of seconds until LCD goes to screen saver mode
        TOP_X:      X coordinate for top-left corner on LCD
        TOP_Y:      Y coordinate for top-left corner on LCD
        TOP_BAR:    Height (in px) of top bar

    Methods & Properties:
        displayWidth:       Width (pixels) of 0.96" LCD display
        displayHeight:      Height (pixels) of 0.96" LCD display
        isFake:             'False' if physical Enviro+
        get_CPU_temp:       Get CPU temp which we then can use to compensate temp reads
        get_proximity:      Get proximity value from sensor
        get_lux:            Get illumination value from sensor
        get_pressure:       Get barometric pressure from sensor
        get_humidity:       Get humidity from sensor
        get_temperature:    Get temperature from sensor
        get_gas_data:       Get gas data from sensor
        get_particles:      Get particle data from sensor
        add_display_modes:  Add one or more display modes to the list
        set_display_mode:   Switch display mode
        update_sleep_mode:  Switch to/from sleep mode
        display_init:       Initialize display so we can draw on it
        display_rotate:     Rotate display +/- 90 degrees
        display_on:         Turn 'on' LCD
        display_off:        Turn 'off' LCD
        display_blank:      Erase LCD
        display_reset:      Erase LCD
        display_sparkle:    Show random sparkles on LCD
        display_as_graph:   Display data as (sparkline) graph
        display_as_text:    Display data as text (in columns)
        display_message:    Display text message
        display_progress:   Display progress bar
    """

    def __init__(self, *args, **kwargs):
        """Initialize Enviro+ hardware

        Args:
            args:
                User can provide single 'dict' with settings
            kwargs:
                User can provide individual settings as key-value pairs
        """
        # We combine 'args' and 'kwargs' to allow users to provide the entire
        # 'config' object and/or individual settings (which could override
        # values in 'config').
        settings = {**args[0], **kwargs} if args and isinstance(args[0], dict) else kwargs

        bus = SMBus(1)
        self._BME280 = BME280(i2c_dev=bus)  # BME280 temperature, pressure, humidity sensor

        self._PMS5003 = PMS5003()  # PMS5003 particulate sensor
        self._LTR559 = ltr559  # Proximity sensor
        self._GAS = gas  # Enviro+

        # Initialize LCD and canvas
        self._LCD = self._init_LCD(**settings)  # ST7735 0.96" 160x80 LCD

        self.displRotation = settings.get(KWD_ROTATION, DEF_ROTATION)
        self.displProgress = bool(settings.get(KWD_PROGRESS, STATUS_ON))

        self.displayModes = [DISPL_SPARKLE]
        self.displMode = DISPL_SPARKLE

        self.displSleepTime = settings.get(KWD_SLEEP, DEF_SLEEP)
        self.displSleepMode = False

        self.displTopX = settings.get(KWD_DISPLAY_TOP_X, DISPL_TOP_X)
        self.displTopY = settings.get(KWD_DISPLAY_TOP_Y, DISPL_TOP_Y)
        self.displTopBar = settings.get(KWD_DISPLAY_TOP_BAR, DISPL_TOP_BAR)

        self._img = None
        self._draw = None
        self._fontLG = None
        self._fontSM = None

    @property
    def displayWidth(self):
        return self._LCD.width

    @property
    def displayHeight(self):
        return self._LCD.height

    @property
    def isFake(self):
        """Is this 'real' or 'fake' Enviro+?
        
        Returns 'True' if we use 'fake' Enviro+ libraries
        """
        return getattr(self._LCD, 'fake', False)

    def _init_LCD(self, **kwargs):
        """Initialize LCD on Enviro+"""
        st7735 = ST7735.ST7735(
            port=0,
            cs=1,
            dc=9,
            backlight=12,
            rotation=kwargs.get(KWD_ROTATION, DEF_ROTATION),
            spi_speed_hz=10000000,
        )
        st7735.begin()

        return st7735

    @staticmethod
    def _scrub(data, default=0):
        """Scrub 'None' values from data"""
        return [default if i is None else i for i in data]

    @staticmethod
    def _clamp(val, minVal=0, maxVal=1):
        """Clamp values to min/max range"""
        return min(max(float(minVal), float(val)), float(maxVal))

    @staticmethod
    def _scale(val, minMax, height):
        """Scale value to fit on Enviro+ LCD

        This is similar to 'num_to_range()' in f451 Labs Common module,
        but simplified for fitting values to Enviro+ LCD display dimensions.
        """
        if minMax is None or minMax[1] == minMax[0]:
            return 0

        return float(val - minMax[0]) / float(minMax[1] - minMax[0]) * height

    @staticmethod
    def _get_rgb(val):
        """Get a color value using 'colorsys' library
        
        We use this method if there is no color map and/or 
        no limits are defined for a give data set.
        """
        # Convert the values to colors from red to blue
        color = (1.0 - val) * 0.6
        return tuple(int(x * 255.0) for x in colorsys.hsv_to_rgb(color, 1.0, 1.0))

    @staticmethod
    def _get_rgb_from_map(val, limits, colorMap):
        """Get a color from color map based on limits
        
        This function maps a value against a color map. Note that 
        we need to map an original value (as opposed to scaled value)
        against the color map, as the color map limits use actual 
        (full-scale) values.

        Args:
            val: value to map
            limits: 'list' with limits
            colorMap: named 'tuple' with color map

        Returns:
            'tuple' with RGB as '(R, G, B)'
        """
        if val > round(limits[2], 1):
            return colorMap.high
        elif val <= round(limits[1], 1):
            return colorMap.low
        else:
            return colorMap.normal

    def get_CPU_temp(self, strict=True):
        """Get CPU temp

        We use this for compensating temperature reads from BME280 sensor.

        Based on code from Enviro+ example 'luftdaten_combined.py'

        Args:
            strict:
                If 'True', then we raise an exception, else we simply
                return 'regular' temperature (from BME280) if the
                exceptions is 'FileNotFoundError'
        Raises:
            Same exceptions as 'Popen'
        """
        try:
            process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
            output, _error = process.communicate()
            return float(output[output.index('=') + 1 : output.rindex("'")])

        except FileNotFoundError:
            if not strict:
                return self._BME280.get_temperature()
            else:
                raise

    def get_proximity(self):
        """Get proximity from LTR559 sensor"""
        return self._LTR559.get_proximity()

    def get_lux(self):
        """Get illumination from LTR559 sensor"""
        return self._LTR559.get_lux()

    def get_pressure(self):
        """Get air pressure data from BME280 sensor"""
        return self._BME280.get_pressure()

    def get_humidity(self):
        """Get humidity data from BME280 sensor"""
        return self._BME280.get_humidity()

    def get_temperature(self):
        """Get temperature data from BME280"""
        return self._BME280.get_temperature()

    def get_gas_data(self):
        return self._GAS.read_all()

    def get_particles(self):
        """Get particle data from PMS5003"""
        try:
            data = self._PMS5003.read()

        except pmsReadTimeoutError:
            time.sleep(1)
            self._PMS5003.reset()
            data = self._PMS5003.read()

        except SerialTimeoutError as e:
            raise EnviroError(f'PMS5003 Error: {e}') from e

        return data

    def add_displ_modes(self, modes):
        """Add list of display modes to existing list
        
        We combine the lists, convert them to a set to ensure that
        there are no duplicates, and then convert back to a list.

        Args:
            modes: list of one or more view names
        """
        # If it's a single string, then we'll assume it's the name
        # of a new view and we'll convert it to alist with 1 item.
        if isinstance(modes, str):
            modes = [modes]
        
        self.displayModes = list(set(self.displayModes + modes))

    def set_display_mode(self, mode):
        """Change LED display mode

        Change the LED display mode and also wake
        up the display if needed.

        Args:
            mode: if pos/neg int, then move to next/prev view/mode
                  if string, then move to specific view/mode

        """
        newMode = DISPL_SPARKLE

        # Did we get a string? Check if it's a valid view.
        if isinstance(mode, str) and mode in self.displayModes:
            newMode = mode

        # Or did we get 'direction' ? Then loop to prev/next view.
        elif isinstance(mode, int):
            displMax = max(0, len(self.displayModes) - 1)
            
            newModeIndx = self.displayModes.index(self.displMode)
            newModeIndx += (-1 if int(mode) < 0 else 1)

            if newModeIndx > displMax:
                newModeIndx = 0
            elif newModeIndx < 0:
                newModeIndx = displMax

            newMode = self.displayModes[newModeIndx]

        self.displMode = newMode

        # Wake up display?
        if self.displSleepMode:
            self.display_on()

        # Clear the display
        self.display_blank()

    def update_sleep_mode(self, *args):
        """Enable or disable LCD sleep mode

        We're turning on/off teh LCD sleep mode flag based on whether
        one or more args are 'True'

        Args:
            args: list of one or more flags
        """
        if any(args) and not self.displSleepMode:
            self.display_off()
        elif not any(args) and self.displSleepMode:
            self.display_on()

    def display_init(self, **kwargs):
        """Initialize LCD drawing area

        This only initializes the drawing area without actually
        drawing or displying anything on the LCD. So we can/should
        do this regardless of sleep mode.

        Args:
            kwargs: reserved for future extension
        """
        self._img = Image.new('RGB', (self._LCD.width, self._LCD.height), color=RGB_BLACK)
        self._draw = ImageDraw.Draw(self._img)
        self._fontLG = ImageFont.truetype(RobotoMedium, FONT_SIZE_LG)
        self._fontMD = ImageFont.truetype(RobotoMedium, FONT_SIZE_MD)
        self._fontSM = ImageFont.truetype(RobotoMedium, FONT_SIZE_SM)

    def display_rotate(self, direction, step180=False):
        """Rotate LED display

        Since 0.96" LCD is rectangular (160x80), rotating only 90 degrees 
        obvioulsy affects aspect ratio. However, it's the responsibility 
        of the main app to ensure proper rotation, and in most cases
        that probably means rotating 180 degrees at a time.

        Args:
            direction: pos/neg integer
            step180: if 'True' then we rotate full 180 degress each time
        """
        if self.isFake:
            return

        if step180:
            self.displRotation = 0 if self.displRotation >= 180 else 180

        elif int(direction) < 0:
            self.displRotation = 270 if self.displRotation <= 0 else self.displRotation - ROTATE_90

        else:
            self.displRotation = 0 if self.displRotation >= 270 else self.displRotation + ROTATE_90

        # fmt: off
        # Rotate as needed
        self._LCD = self._init_LCD(ROTATION=self.displRotation) # Re-init LCD to change rotation
        self.display_init()                                     # Also need to re-init display as 
                                                                # this changes aspect ratio, etc.
        #fmt: on
        # Wake up display?
        if self.displSleepMode:
            self.display_on()

    # fmt: off
    def display_on(self):
        """Turn 'on' LCD display"""
        if not self.isFake:
            self._LCD.display_on()
        self.displSleepMode = False     # Reset 'sleep mode' flag
        # self.display_blank()          # Clear LCD

    def display_off(self):
        """Turn 'off' LCD display"""
        if not self.isFake:
            self.display_blank()        # Clear LCD
            self._LCD.display_off()
        self.displSleepMode = True      # Set 'sleep mode' flag

    def display_blank(self):
        """Show clear/blank LCD"""
        # Skip this if we're in 'sleep' mode
        if not (self.isFake or self.displSleepMode):
            self._img = Image.new('RGB', (self._LCD.width, self._LCD.height), color=RGB_BLACK)
            self._draw = ImageDraw.Draw(self._img)

    def display_reset(self):
        """Reset and clear LCD"""
        if not self.isFake:
            self.display_init()
    # fmt: on

    def display_as_graph(self, data, minMax=None, colorMap=None, lblLen=DISPL_LBL_LEN, default=0):
        """Display graph and data point as text label

        This method will redraw the entire LCD

        Args:
            data:
                'DataUnit' named tuple with the following fields:
                    data   = [list of values],
                    valid  = <tuple with min/max>,
                    unit   = <unit string>,
                    label  = <label string>,
                    limits = [list of limits]
            minMax:
                'tuple' with min/max values. If 'None' then calculate locally.
            colorMap:
                'tuple' (optional) custom color map to use if data has defined 'limits'
            lblLen:
                'int' (optional) number of chars of label to display on top row
            default:
                'float' (optional) default value to use when replacing 'None' values
        """
        # Skip this if we're in 'sleep' mode
        if self.isFake or self.displSleepMode:
            return

        # Create a list with 'displayWidth' num values. We add 0 (zero) to
        # the beginning of the list if whole set has less than 'displayWidth'
        # num values. This allows us to simulate 'scrolling' right to left. We
        # grab last 'n' values that can fit LED and scrub any 'None' values. If
        # there are not enough values to to fill display, we add 0's
        displWidth = self.displayWidth
        displHeight = self.displayHeight
        subSet = self._scrub(data.data[-displWidth:], default)
        lenSet = min(displWidth, len(subSet))

        # Extend 'value' list as needed
        values = (
            subSet
            if lenSet == displWidth
            else [default for _ in range(displWidth - lenSet)] + subSet
        )

        # Reserve space for progress bar? Then clear rest of display by 
        # 'painting' it black.
        yProg = (PBAR_HEIGHT if (self.displProgress) else 0)
        yMin = DISPL_TOP_BAR
        yMax = displHeight - yMin - yProg
        if minMax is None or minMax[1] == minMax[0]:
            vMin = min(values) if minMax is None else minMax[0]
            vMax = max(values) if minMax is None else minMax[1]
        else:
            vMin, vMax = minMax

        fitted = [int(self._clamp(self._scale(v, (vMin, vMax), yMax), yMin, yMax)) for v in values]
        self._draw.rectangle((0, 0, displWidth, displHeight - 1 - yProg), RGB_BLACK)

        # Get colors based on limits and color map? Or generate based on
        # value itself compared to defined limits?
        if all(data.limits):
            colors = [self._get_rgb_from_map(v, data.limits, colorMap) for v in values]
        else:
            # Scale incoming values to be between 0 and 1. We may need to clamp 
            # values when values are outside min/max for current sub-set. This 
            # can happen when original data set has more values than the chunk 
            # that we display on the Enviro+ LCD.
            scaled = [self._clamp((v - vMin + 1) / (vMax - vMin + 1)) for v in values]
            colors = [self._get_rgb(v) for v in scaled]

        for i in range(len(fitted)):
            self._draw.rectangle((i, (displHeight - fitted[i]), i + 1, displHeight - 1 - yProg), colors[i]) # type: ignore

        # Write the text at the top in black
        message = f'{data.label[:lblLen]}: {values[-1]:.1f} {data.unit}'
        self._draw.text((0, 0), message, font=self._fontMD, fill=COLOR_TXT)

        self._LCD.display(self._img)

    def display_as_text(self, data, lblLen=DISPL_LBL_LEN):
        """Display data points as text in columns

        This method will redraw the entire LCD

        Args:
            data:
                'list' of 'dict' objects with following fields:
                    dataPt   = [list of values],
                    label  = <label string>,
                    unit   = <unit string>,
                    limits =  to use if data has defined 'limits'
                    colorMap = 'tuple' (optional) custom color map
            lblLen:
                'int' (optional) number of chars of label to display on top row
        """
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode:
            return

        # Reserve space for progress bar?
        displWidth = self.displayWidth
        displHeight = self.displayHeight
        yProg = (PBAR_HEIGHT if (self.displProgress) else 0)
        self._draw.rectangle((0, 0, displWidth, displHeight - 1 - yProg), RGB_BLACK)

        cols = 2
        rows = len(data) / cols

        for idx, item in enumerate(data):
            x = DEF_LCD_OFFSET_X + ((displWidth // cols) * (idx // rows))
            y = DEF_LCD_OFFSET_Y + ((displHeight / rows) * (idx % rows))

            if all(item['limits']):
                rgb = self._get_rgb_from_map(item['dataPt'], item['limits'], item['colorMap'])
            else:
                rgb = COLOR_TXT

            message = f"{item['label'][:lblLen]}: {item['dataPt']:.1f} {item['unit']}"
            self._draw.text((x, y), message, font=self._fontSM, fill=rgb)

        # Display results
        self._LCD.display(self._img)

    def display_message(self, msg, fgCol=None, bgCol=None):
        """Display text message

        This method will redraw the entire LCD

        Args:
            msg: 'str' with text to display
            fgCol: 'tuple' with (R, G, B) for text color
            bgCol: 'tuple' with (R, G, B) for background color
        """
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode:
            return

        # Reserve space for progress bar?
        displWidth = self.displayWidth
        displHeight = self.displayHeight
        
        bgCol = bgCol or RGB_BLACK
        fgCol = fgCol or RGB_WHITE

        yProg = (PBAR_HEIGHT if (self.displProgress) else 0)
        self._draw.rectangle((0, 0, displWidth, displHeight - 1 - yProg), bgCol)

        # How long is text?
        txtLen = self._draw.textlength(str(msg), font=self._fontLG)

        # Draw message
        x = DEF_LCD_OFFSET_X
        if txtLen >= displWidth:
            y = DEF_LCD_OFFSET_Y + int((displHeight - FONT_SIZE_LG * 2 - LINE_SPACING) / 2)    # ImageDraw default line spacing is 4px
            splitMsg = '-\n'.join(str(msg).rsplit('-', 1))  # TODO: need better/smarter way to split text
            self._draw.multiline_text((x, y), splitMsg, font=self._fontLG, fill=fgCol)
        else:
            y = DEF_LCD_OFFSET_Y + int((displHeight - FONT_SIZE_LG) / 2)
            self._draw.text((x, y), str(msg), font=self._fontLG, fill=fgCol)

        # Display results
        self._LCD.display(self._img)

    def display_progress(self, inFrctn=0.0):
        """Update progressbar on LCD

        This method marks 'fraction complete' (0.0 - 1.0)
        on 1px tall progress bar on top row of LCD

        Args:
            inFrctn: 'float' representing fraction complete
        """
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode or not self.displProgress:
            return

        displWidth = self.displayWidth
        displHeight = self.displayHeight
        yProg = self.displayHeight - PBAR_HEIGHT

        # Calculate X value. We ensure that we do not go over max width
        # of LCD by limiting any input value to a range of 0.0 - 1.0
        x = int(max(min(float(inFrctn), 1.0), 0.0) * displWidth)

        self._draw.rectangle((0, yProg, displWidth, displHeight - 1), COLOR_BG)
        self._draw.rectangle((0, yProg + 1, x, displHeight - 1), COLOR_PBAR)

        # Display results
        self._LCD.display(self._img)

    def display_sparkle(self):
        """Show random sparkles on LCD"""
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode:
            return

        # Reserve space for progress bar?
        displWidth = self.displayWidth
        displHeight = self.displayHeight
        yProg = (PBAR_HEIGHT if (self.displProgress) else 0)

        # Create sparkles
        x = randint(0, displWidth - 1)
        y = randint(0, displHeight - 1 - yProg)
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)

        # Do we want to clear the screen? Or add more sparkles?
        maxSparkle = int(displWidth * displHeight * MAX_SPARKLE_PCNT)
        if randint(0, maxSparkle):
            self._draw.point((x, y), (r, g, b))
        else:
            self._draw.rectangle((0, 0, displWidth, displHeight - 1 - yProg), RGB_BLACK)

        self._LCD.display(self._img)
