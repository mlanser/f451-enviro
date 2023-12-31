"""Global constants for f451 Labs Enviro+ Demo application

This module holds all global constants used within the components of the 
f451 Labs SenseHat Demo applications Some of the constants are used as 
keyword equivalents for attributes listed in the `settings.toml` file.
"""

# fmt: off
# =========================================================
#              M I S C .   C O N S T A N T S
# =========================================================
DEF_FREQ = 600              # Default delay between uploads in seconds
DEF_DELAY = 300             # Default delay before first upload in seconds
DEF_WAIT = 1                # Default delay between sensor reads
DEF_THROTTLE = 120          # Default additional delay on 'ThrottlingError'
DEF_ROUNDING = 2            # Default 'rounding' precision for uploaded data
# fmt: on


# =========================================================
#    K E Y W O R D S   F O R   C O N F I G   F I L E S
# =========================================================
KWD_FREQ = 'FREQ'
KWD_DELAY = 'DELAY'
KWD_WAIT = 'WAIT'
KWD_THROTTLE = 'THROTTLE'
KWD_ROUNDING = 'ROUNDING'

# fmt: off
# =========================================================
#   C O N S T A N T S   F O R   D I S P L A Y   M O D E S
# =========================================================
DISPL_RNDNUM = 'rndnum'     # Display random number
DISPL_RNDPCNT = 'rndpcnt'   # Display random percentage
# fmt: on
