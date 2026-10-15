import time
import board
import busio
import adafruit_dht

from gpiozero import DigitalInputDevice, OutputDevice
from adafruit_ina219 import INA219


# =========================================================
# GPIO PIN CONFIGURATION
# =========================================================

DHT_PIN = board.D4       # GPIO4, physical pin 7
PIR_PIN = 25             # GPIO25, physical pin 22
LDR_PIN = 24             # GPIO24, physical pin 18

RELAY_LIGHT = 22         # GPIO22, physical pin 15
RELAY_FAN = 23           # GPIO23, physical pin 16


# =========================================================
# SENSOR INITIALIZATION
# =========================================================

# DHT11
dht = adafruit_dht.DHT11(
    DHT_PIN,
    use_pulseio=False
)

# PIR sensor
pir = DigitalInputDevice(
    PIR_PIN,
    pull_up=False
)

# LDR digital output
ldr = DigitalInputDevice(
    LDR_PIN,
    pull_up=False
)


# =========================================================
# RELAY INITIALIZATION
# =========================================================
# Most 5V relay modules are ACTIVE LOW.
#
# If your relay works opposite to this,
# change active_high=False to active_high=True.

light_relay = OutputDevice(
    RELAY_LIGHT,
    active_high=False,
    initial_value=False
)

fan_relay = OutputDevice(
    RELAY_FAN,
    active_high=False,
    initial_value=False
)


# =========================================================
# I2C BUS
# =========================================================

i2c = busio.I2C(
    board.SCL,
    board.SDA
)


# =========================================================
# INA219
# =========================================================

ina219 = INA219(i2c)


# =========================================================
# DHT11 READING FUNCTION
# =========================================================

def read_dht():

    try:

        temperature = dht.temperature
        humidity = dht.humidity

        return temperature, humidity

    except RuntimeError:

        # DHT11 occasionally gives temporary read errors
        return None, None

    except Exception as e:

        print("DHT11 error:", e)

        return None, None


# =========================================================
# INA219 READING FUNCTION
# =========================================================

def read_ina219():

    try:

        voltage = ina219.bus_voltage
        current = ina219.current
        power = ina219.power

        return voltage, current, power

    except Exception as e:

        print("INA219 error:", e)

        return None, None, None


# =========================================================
# START
# =========================================================

print()
print("================================")
print("     SMART CLASSROOM SYSTEM")
print("================================")
print()


# =========================================================
# MAIN LOOP
# =========================================================

try:

    while True:

        # ---------------------------------------------
        # PIR
        # ---------------------------------------------

        if pir.value:

            occupancy = True
            occupancy_text = "YES"

        else:

            occupancy = False
            occupancy_text = "NO"


        # ---------------------------------------------
        # LDR
        # ---------------------------------------------

        if ldr.value:

            light_text = "BRIGHT"

        else:

            light_text = "DARK"


        # ---------------------------------------------
        # DHT11
        # ---------------------------------------------

        temperature, humidity = read_dht()


        # ---------------------------------------------
        # INA219
        # ---------------------------------------------

        voltage, current, power = read_ina219()


        # =================================================
        # DISPLAY SENSOR DATA IN TERMINAL
        # =================================================

        print("--------------------------------")

        print("Occupancy :", occupancy_text)

        print("Light     :", light_text)

        if temperature is not None:

            print(
                "Temperature:",
                round(temperature, 1),
                "°C"
            )

            print(
                "Humidity   :",
                round(humidity, 1),
                "%"
            )

        else:

            print("Temperature: ERROR")
            print("Humidity   : ERROR")


        if voltage is not None:

            print(
                "Voltage    :",
                round(voltage, 3),
                "V"
            )

            print(
                "Current    :",
                round(current, 2),
                "mA"
            )

            print(
                "Power      :",
                round(power, 2),
                "mW"
            )

        else:

            print("INA219     : ERROR")


        # =================================================
        # SMART CLASSROOM CONTROL
        # =================================================

        # -------------------------------------------------
        # NO PERSON
        # -------------------------------------------------

        if not occupancy:

            light_relay.off()
            fan_relay.off()

            print("Light Relay: OFF")
            print("Fan Relay  : OFF")


        # -------------------------------------------------
        # PERSON DETECTED
        # -------------------------------------------------

        else:

            # ---------------------------------------------
            # LIGHT CONTROL USING LDR
            # ---------------------------------------------

            if light_text == "DARK":

                light_relay.on()

                print("Light Relay: ON")

            else:

                light_relay.off()

                print("Light Relay: OFF")


            # ---------------------------------------------
            # FAN CONTROL USING TEMPERATURE
            # ---------------------------------------------

            if temperature is not None:

                if temperature >= 28:

                    fan_relay.on()

                    print("Fan Relay  : ON")

                else:

                    fan_relay.off()

                    print("Fan Relay  : OFF")

            else:

                fan_relay.off()

                print("Fan Relay  : OFF")


        print("--------------------------------")

        # Wait before next measurement
        time.sleep(2)


# =========================================================
# STOP PROGRAM SAFELY
# =========================================================

except KeyboardInterrupt:

    print()
    print("Stopping Smart Classroom...")

    light_relay.off()
    fan_relay.off()

    dht.exit()

    print("All relays OFF.")
    print("System stopped.")
