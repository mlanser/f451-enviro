"""Demo for using f451 Labs Enviro+ Module."""

from f451_enviro.enviro import Enviro


# =========================================================
#                    D E M O   A P P
# =========================================================
def main():
    # Initialize device instance which includes all sensors
    # an d LCD display on Enviro+
    enviro = Enviro({
        "ROTATION": 90,
        "DISPLAY": 0,
        "PROGRESS": 0,
        "SLEEP": 600    
    })
    enviro.display_init()

    # Display text on LCD
    enviro.display_message("Hello world!")

    tempRaw = round(enviro.get_temperature(), 1)
    pressRaw = round(enviro.get_pressure(), 1)
    humidRaw = round(enviro.get_humidity(), 1)

    print("\n===== [Demo of f451 Labs Enviro+ Module] ======")
    print(f"TEMP:     {tempRaw} C")
    print(f"PRESSURE: {pressRaw} hPa")
    print(f"HUMIDITY: {humidRaw} %")
    print("=============== [End of Demo] =================\n")


if __name__ == "__main__":
    main()