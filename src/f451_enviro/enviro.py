"""f451 Labs Enviro+ Device Class.

The Enviro+ Device class includes support for sensosr and 
LCD display included on the Pimoroni Enviro+ HAT.

The class wraps -- and extends as needed -- the methods 
and functions supported by underlying libraries, and also
keeps track of core counters, flags, etc.

Dependencies:
 - fonts: https://pypi.org/project/fonts/
 - font-roboto: https://pypi.org/project/font-roboto/
 - Pillow: https://pypi.org/project/Pillow/
 - Pimoroni Enviro+ library: https://github.com/pimoroni/enviroplus-python/  
"""

import time
import colorsys

from random import randint

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium

from subprocess import PIPE, Popen

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
    from .fake_HAT import FakePMS5003 as PMS5003, FakeReadTimeoutError as pmsReadTimeoutError, FakeSerialTimeoutError as SerialTimeoutError

# Support Enviro+ gas sensor
try:
    from enviroplus import gas
except ImportError:
    from .fake_HAT import FakeEnviroPlus as gas

__all__ = [
    "Enviro",
    "EnviroError",
    "KWD_ROTATION",
    "KWD_DISPLAY",
    "KWD_PROGRESS",
    "KWD_SLEEP",
    "KWD_DISPL_TOP_X",
    "KWD_DISPL_TOP_Y",
    "KWD_DISPL_TOP_BAR",
]


# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
DEF_ROTATION = 0        # Default display rotation
DEF_DISPL_MODE = 0      # Default display mode
DEF_SLEEP = 600         # Default time to sleep (in seconds)
DEF_LCD_OFFSET_X = 1    # Default horizontal offset for LCD
DEF_LCD_OFFSET_Y = 1    # Default vertical offseet for LCD 

STATUS_ON = True
STATUS_OFF = False

DISPL_TOP_X = 2         # X/Y ccordinate of top-left corner for LCD content
DISPL_TOP_Y = 2
DISPL_TOP_BAR = 21      # Height (in px) of top bar

PROX_DEBOUNCE = 0.5     # Delay to debounce proximity sensor on 'tap'
PROX_LIMIT = 1500       # Threshold for proximity sensor to detect 'tap'

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

# RGB colors and palette for values on combo/text screen
COLOR_PALETTE = [
    RGB_BLUE,           # Dangerously Low
    RGB_CYAN,           # Low
    RGB_GREEN,          # Normal
    RGB_YELLOW,         # High
    RGB_RED             # Dangerously High
]         

COLOR_BG = RGB_BLACK    # Default background
COLOR_TXT = RGB_CHROME  # Default text on background
COLOR_PBAR = RGB_CYAN   # Default progress bar 

FONT_SIZE_SM = 10       # Small font size
FONT_SIZE_MD = 16       # Medium font size
FONT_SIZE_LG = 20       # Large font size

ROTATE_90 = 90          # Rotate 90 degrees    


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_ROTATION = "ROTATION"
KWD_DISPLAY = "DISPLAY"
KWD_PROGRESS = "PROGRESS"
KWD_SLEEP = "SLEEP"
KWD_DISPL_TOP_X = "TOP_X"
KWD_DISPL_TOP_Y = "TOP_Y"
KWD_DISPL_TOP_BAR = "TOP_BAR"


# =========================================================
#                        H E L P E R S
# =========================================================
class EnviroError(Exception):
    """Custom exception class"""
    pass


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
        DISPLAY:    Default display mode [0...]
        PROGRESS:   Show progress bar - [0 = no, 1 = yes]
        SLEEP:      Number of seconds until LCD goes to screen saver mode
        TOP_X:      X coordinate for top-left corner on LCD
        TOP_Y:      Y coordinate for top-left corner on LCD
        TOP_BAR:    Height (in px) of top bar

    Methods:
        get_CPU_temp:       Get CPU temp which we then can use to compensate temp reads
        get_proximity:      Get proximity value from sensor
        get_lux:            Get illumination value from sensor
        get_pressure:       Get barometric pressure from sensor
        get_humidity:       Get humidity from sensor
        get_temperature:    Get temperature from sensor
        get_gas_data:       Get gas data from sensor
        get_particles:      Get particle data from sensor
        display_init:       Initialize display so we can draw on it
        display_on:         Turn 'on' LCD
        display_off:        Turn 'off' LCD
        display_blank:      Erase LCD
        display_reset:      Erase LCD
        display_sparkle:    Show random sparkles on LCD
        display_as_graph:   Display data as (sparkline) graph
        display_as_text:    Display data as text (in columns)
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
        settings = {**args[0], **kwargs} if args and type(args[0]) is dict else kwargs

        bus = SMBus(1)
        self._BME280 = BME280(i2c_dev=bus)                  # BME280 temperature, pressure, humidity sensor

        self._PMS5003 = PMS5003()                           # PMS5003 particulate sensor
        self._LTR559 = ltr559                               # Proximity sensor
        self._GAS = gas                                     # Enviro+

        # Initialize LCD and canvas
        self._LCD = self._init_LCD(**settings)              # ST7735 0.96" 160x80 LCD

        self.displRotation = settings.get(KWD_ROTATION, DEF_ROTATION)
        self.displMode = settings.get(KWD_DISPLAY, DEF_DISPL_MODE)
        self.displProgress = bool(settings.get(KWD_PROGRESS, STATUS_ON))

        self.displSleepTime = settings.get(KWD_SLEEP, DEF_SLEEP)
        self.displSleepMode = False
        
        self.displTopX = settings.get(KWD_DISPL_TOP_X, DISPL_TOP_X)
        self.displTopY = settings.get(KWD_DISPL_TOP_Y, DISPL_TOP_Y)
        self.displTopBar = settings.get(KWD_DISPL_TOP_BAR, DISPL_TOP_BAR)

        self._img = None
        self._draw = None
        self._fontLG = None
        self._fontSM = None

    @property
    def widthLCD(self):
        return self._LCD.width
    
    @property
    def heightLCD(self):
        return self._LCD.height

    def _init_LCD(self, **kwargs):
        """Initialize LCD on Enviro+"""
        st7735 = ST7735.ST7735(
            port = 0,
            cs = 1,
            dc = 9,
            backlight = 12,
            rotation = kwargs.get(KWD_ROTATION, DEF_ROTATION),
            spi_speed_hz = 10000000
        )
        st7735.begin()

        return st7735

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
            return float(output[output.index('=') + 1:output.rindex("'")])
        
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
            raise EnviroError(f"PMS5003 Error: {e}")

        return data

    def update_sleep_mode(self, *args):
        """Enable or disable LCD sleep mode

        We're turning on/off teh LCD sleep mode flag based on whether
        one or more args are 'True'

        Args:
            args: list of one or more flags
        """
        sleep = any(args)

        # Do we need to turn off LCD?
        if sleep and not self.displSleepMode:
            self.display_off()

        # Do we need to turn on LCD?
        elif not sleep and self.displSleepMode:
            self.display_on()

    def display_init(self):
        """Initialize LCD drawing area
        
        This only initializes the drawing area without actually 
        drawing or displying anything on the LCD. So we can/should 
        do this regardless of sleep mode.
        """
        self._img = Image.new(
            'RGB', 
            (self._LCD.width, self._LCD.height), 
            color = RGB_BLACK
        )
        self._draw = ImageDraw.Draw(self._img)
        self._fontLG = ImageFont.truetype(RobotoMedium, FONT_SIZE_LG)
        self._fontMD = ImageFont.truetype(RobotoMedium, FONT_SIZE_MD)
        self._fontSM = ImageFont.truetype(RobotoMedium, FONT_SIZE_SM)

    def display_on(self):
        """Turn 'on' LCD display"""
        self.displSleepMode = False     # Reset 'sleep mode' flag
        self._LCD.display_on()
        self.display_blank()

    def display_off(self):
        """Turn 'off' LCD display"""
        self.display_blank()
        self._LCD.display_off()
        self.displSleepMode = True      # Set 'sleep mode' flag
        
    def display_blank(self):
        """Show clear/blank LCD"""
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode:
            return
        
        img = Image.new(
            'RGB', 
            (self._LCD.width, self._LCD.height), 
            color = RGB_BLACK
        )
        self._LCD.display(img)

    def display_reset(self):
        """Reset and clear LCD"""
        self.display_init()

    def display_as_graph(self, data):
        """Display graph and data point as text label
        
        This method will redraw the entire LCD

        Args:
            data:
                'dict' as follows:
                    {
                        "data": [list of values],
                        "unit" <unit string>,
                        "label": <label string>,
                        "limit": [list of limits]
                    }    
        """
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode:
            return

        # Scale values in data set between 0 and 1
        vmin = min(data["data"])
        vmax = max(data["data"])
        colors = [(v - vmin + 1) / (vmax - vmin + 1) for v in data["data"]]

        # Reserve space for progress bar?
        yMin = 2 if (self.displProgress) else 0
        self._draw.rectangle((0, yMin, self._LCD.width, self._LCD.height), RGB_BLACK)
        
        for i in range(len(colors)):
            # Convert the values to colors from red to blue
            color = (1.0 - colors[i]) * 0.6
            r, g, b = [int(x * 255.0)
                    for x in colorsys.hsv_to_rgb(color, 1.0, 1.0)]
        
            # Draw a 1-pixel wide rectangle of given color
            self._draw.rectangle((i, self.displTopBar, i + 1, self._LCD.height), (r, g, b))
        
            # Draw and overlay a line graph in black
            line_y = self._LCD.height - (self.displTopBar + (colors[i] * (self._LCD.height - self.displTopBar))) + self.displTopBar
            self._draw.rectangle((i, line_y, i + 1, line_y + 1), RGB_BLACK)
        
        # Write the text at the top in black
        message = "{}: {:.1f} {}".format(data["label"][:4], data["data"][-1], data["unit"])
        self._draw.text((0, 0), message, font=self._fontMD, fill=COLOR_TXT)

        self._LCD.display(self._img)

    def display_as_text(self, data):
        """Display graph and data point as text label
        
        This method will redraw the entire LCD

        Args:
            data:
                'list' of data rows where each row is a 'dict' as follows:
                    {
                        "data": [list of values],
                        "unit" <unit string>,
                        "label": <label string>,
                        "limit": [list of limits]
                    }    
        """
        # Skip this if we're in 'sleep' mode
        if self.displSleepMode:
            return

        # Reserve space for progress bar?
        yMin = 2 if (self.displProgress) else 0
        self._draw.rectangle((0, yMin, self._LCD.width, self._LCD.height), RGB_BLACK)

        cols = 2
        rows = (len(data) / cols)

        for idx, item in enumerate(data):
            x = DEF_LCD_OFFSET_X + ((self._LCD.width // cols) * (idx // rows))
            y = DEF_LCD_OFFSET_Y + ((self._LCD.height / rows) * (idx % rows))
            
            message = "{}: {:.1f} {}".format(item["label"][:4], item["data"][-1], item["unit"])
            
            lim = item["limits"]
            rgb = COLOR_PALETTE[0]

            for j in range(len(lim)):
                if item["data"][-1] > lim[j]:
                    rgb = COLOR_PALETTE[j + 1]

            self._draw.text((x, y), message, font=self._fontSM, fill=rgb)

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

        # Calculate X value. We ensure that we do not go over max width
        # of LCD by limiting any input value to a range of 0.0 - 1.0
        x = int(max(min(float(inFrctn), 1.0), 0.0) * self._LCD.width)

        self._draw.rectangle((0, 0, self._LCD.width, 0), COLOR_BG)
        self._draw.rectangle((0, 0, x, 0), COLOR_PBAR)

        self._LCD.display(self._img)

    def display_sparkle(self):
        """Show random sparkles on LCD"""
        pass
        # x = randint(0, 7)
        # y = randint(0, 7)
        # r = randint(0, 255)
        # g = randint(0, 255)
        # b = randint(0, 255)

        # toggle = randint(0, 3)

        # if toggle != 0:
        #     self.enviro.set_pixel(x, y, r, g, b)
        # else:    
        #     self.enviro.clear()
