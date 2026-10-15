# IoT-Based Smart Classroom: Occupancy and Energy Optimization System

A Raspberry Pi 5 prototype that saves energy in classrooms. It detects whether anyone is in the room, checks the daylight level and temperature, and automatically switches the **light** and the **fan** through a relay module. An INA219 sensor measures voltage, current and power so energy use can be monitored.

## Features

- **Occupancy detection** with a PIR motion sensor
- **Automatic lighting:** the light turns ON only when the room is occupied **and** dark
- **Automatic fan control:** the fan turns ON only when the room is occupied **and** the temperature is 28 °C or above
- **Power monitoring:** bus voltage (V), current (mA) and power (mW) from an INA219 over I2C
- **Fail-safe behaviour:** both relays turn OFF when the room is empty, when the program stops (Ctrl+C), and the fan stays OFF if the DHT11 cannot be read
- Live readings printed to the terminal every 2 seconds

## Hardware

| Component | Purpose | Raspberry Pi 5 pin (BCM) | Physical pin |
|-----------|---------|--------------------------|--------------|
| PIR sensor | Occupancy detection | GPIO 25 | 22 |
| LDR module (digital out) | Bright / dark detection | GPIO 24 | 18 |
| DHT11 | Temperature and humidity | GPIO 4 | 7 |
| INA219 | Voltage, current and power | SDA = GPIO 2, SCL = GPIO 3 (I2C) | 3, 5 |
| 2-channel 5 V relay, IN1 | Light | GPIO 22 | 15 |
| 2-channel 5 V relay, IN2 | Fan | GPIO 23 | 16 |

Other parts: Raspberry Pi 5 with a 5 V / 5 A USB-C supply, jumper wires, and the light and fan loads.

**Notes**

- The relay board is assumed to be **active-LOW**. If your relays work the opposite way, change `active_high` in `smart_classroom.py`.
- The LDR module's bright / dark threshold is set with its on-board potentiometer.
- The INA219 measures **DC only** (bus voltage up to 26 V). In this prototype it monitors a DC load supply, not mains power.
- Keep any mains wiring insulated and enclosed. Do not touch the relay's AC side while it is powered.
- Signals into the Pi's GPIO pins must never exceed 3.3 V.

## Control logic

| Person (PIR) | Light (LDR) | Temperature | Light relay | Fan relay |
|--------------|-------------|-------------|-------------|-----------|
| No | any | any | OFF | OFF |
| Yes | Dark | below 28 °C | ON | OFF |
| Yes | Dark | 28 °C or above | ON | ON |
| Yes | Bright | below 28 °C | OFF | OFF |
| Yes | Bright | 28 °C or above | OFF | ON |
| Yes | any | read error | by LDR | OFF |

## Software setup

1. Enable I2C: run `sudo raspi-config`, then go to **Interface Options → I2C → Enable**, and reboot.
2. Install system packages and create a virtual environment:

   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv libgpiod2
   python3 -m venv ~/smart-classroom-env
   source ~/smart-classroom-env/bin/activate
   ```

3. Install the Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

   `gpiozero` with `lgpio` is used because the older `RPi.GPIO` library does not work on the Raspberry Pi 5.

4. (Optional) Check that the INA219 is detected on the I2C bus (it is usually at address `0x40`):

   ```bash
   sudo apt install -y i2c-tools
   i2cdetect -y 1
   ```

## Run

```bash
python3 smart_classroom.py
```

Press **Ctrl+C** to stop. Both relays are switched OFF before the program exits.

### Sample output

```
================================
     SMART CLASSROOM SYSTEM
================================

--------------------------------
Occupancy : YES
Light     : DARK
Temperature: 29.0 °C
Humidity   : 58.0 %
Voltage    : 5.02 V
Current    : 160.0 mA
Power      : 800.0 mW
Light Relay: ON
Fan Relay  : ON
--------------------------------
```

## Configuration

All settings are at the top of `smart_classroom.py`, except the temperature limit, which is in the fan-control section.

| Setting | Where | Default |
|---------|-------|---------|
| Sensor and relay pins | `GPIO PIN CONFIGURATION` block | see the hardware table |
| Relay polarity | `active_high` in the relay initialization | `False` (active-LOW) |
| Fan temperature limit | `if temperature >= 28:` | 28 °C |
| Reading interval | `time.sleep(2)` | 2 s |

## Project structure

```
smart-classroom/
├── smart_classroom.py   # main program
├── requirements.txt     # Python dependencies
└── README.md
```

## Troubleshooting

- **DHT11 shows ERROR:** occasional read errors are normal. The code skips them and tries again after 2 s. If it fails constantly, check wiring and the pull-up resistor (many DHT11 modules include one).
- **INA219 shows ERROR:** confirm I2C is enabled and that `i2cdetect -y 1` lists the sensor.
- **Relays behave backwards:** toggle `active_high` for both relays.
- **Light never turns on:** adjust the LDR module's potentiometer, and check that its output is wired to GPIO 24.

## Future scope

- Publish readings over **MQTT** and add a web dashboard (for example Flask and a live chart)
- Log power and energy history to a database
- Add a delay timer before switching appliances off, to avoid flicker when someone sits still
- Multi-room deployment, camera-based people counting, and a mobile app

## Team

- Swara Joshi
- Nishu Anand
- Himani Malavia

**Guide:** Prof. Pooja Gundewar

## License

Add a license of your choice (for example MIT) before publishing.
