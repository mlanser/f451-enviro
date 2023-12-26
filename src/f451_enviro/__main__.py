"""Demo for using f451 Labs Enviro+ Module."""

import time
from f451_enviro.enviro import Enviro


# =========================================================
#                    D E M O   A P P
# =========================================================
def main():
    # Initialize device instance which includes all sensors
    # and LCD display on Enviro+
    enviro = Enviro({'ROTATION': 90, 'DISPLAY': 0, 'PROGRESS': 0, 'SLEEP': 600})

    # Skip display demos if we're using fake HAT
    if not enviro.is_fake():
        enviro.display_init()

        # Display text on LCD
        enviro.display_message("Hello world!")

        for _ in range(50):
            enviro.display_sparkle()
            time.sleep(0.2)

        enviro.display_blank()
        enviro.display_off()

    else:
        print("\nSkipping LCD demo since we don't have a real Enviro+ HAT")

    # Get enviro data, even if it's fake
    tempRaw = round(enviro.get_temperature(), 1)
    pressRaw = round(enviro.get_pressure(), 1)
    humidRaw = round(enviro.get_humidity(), 1)

    print("\n===== [Demo of f451 Labs Enviro+ Module] ======")
    print(f"TEMP:     {tempRaw} C")
    print(f"PRESSURE: {pressRaw} hPa")
    print(f"HUMIDITY: {humidRaw} %")
    print("=============== [End of Demo] =================\n")


if __name__ == '__main__':
    main()
