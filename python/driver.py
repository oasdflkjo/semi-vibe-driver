"""
Driver script for the Semi-Vibe-Driver.
This script loads the DLL and provides functions to interact with the driver.
"""

import ctypes
import os
import sys
from ctypes import c_bool, c_char_p, c_uint8, c_int, CFUNCTYPE, Structure

# Define the callback function type
LogCallbackType = CFUNCTYPE(None, c_char_p)


# Define structures
class SensorData(Structure):
    _fields_ = [
        ("temperature_id", c_uint8),
        ("temperature_value", c_uint8),
        ("humidity_id", c_uint8),
        ("humidity_value", c_uint8),
    ]


class ActuatorData(Structure):
    _fields_ = [
        ("led_value", c_uint8),
        ("fan_value", c_uint8),
        ("heater_value", c_uint8),
        ("doors_value", c_uint8),
    ]


class DeviceStatus(Structure):
    _fields_ = [
        ("connected", c_bool),
        ("sensors_powered", c_bool),
        ("actuators_powered", c_bool),
        ("has_errors", c_bool),
    ]


class Driver:
    """Semi-Vibe-Driver wrapper class."""

    def __init__(self):
        """Initialize the driver."""
        self.driver_lib = None
        self.callback_func = None
        self.initialized = False
        self.connected = False

    def log_callback(self, message):
        """Callback function for driver logging."""
        print(f"[DRIVER] {message.decode('utf-8')}")

    def load_dll(self):
        """Load the driver DLL."""
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the build directory
        build_dir = os.path.abspath(os.path.join(script_dir, ".."))

        # Try Debug folder first (Visual Studio default)
        dll_path = os.path.join(
            build_dir, "build", "bin", "Debug", "semi_vibe_driver.dll"
        )
        if not os.path.exists(dll_path):
            # Fall back to regular bin folder
            dll_path = os.path.join(build_dir, "build", "bin", "semi_vibe_driver.dll")

        if not os.path.exists(dll_path):
            print("Error: Driver DLL not found. Make sure you have built the project.")
            return False

        try:
            self.driver_lib = ctypes.CDLL(dll_path)
        except OSError as e:
            print(f"Error: Failed to load driver DLL: {e}")
            print("Make sure you have built the DLL using CMake.")
            return False

        # Define function prototypes
        self.driver_lib.driver_init.argtypes = [LogCallbackType]
        self.driver_lib.driver_init.restype = c_bool

        self.driver_lib.driver_connect.argtypes = [c_char_p, c_int]
        self.driver_lib.driver_connect.restype = c_bool

        self.driver_lib.driver_disconnect.argtypes = []
        self.driver_lib.driver_disconnect.restype = c_bool

        self.driver_lib.driver_get_status.argtypes = [ctypes.POINTER(DeviceStatus)]
        self.driver_lib.driver_get_status.restype = c_bool

        self.driver_lib.driver_get_sensors.argtypes = [ctypes.POINTER(SensorData)]
        self.driver_lib.driver_get_sensors.restype = c_bool

        self.driver_lib.driver_get_actuators.argtypes = [ctypes.POINTER(ActuatorData)]
        self.driver_lib.driver_get_actuators.restype = c_bool

        self.driver_lib.driver_set_led.argtypes = [c_uint8]
        self.driver_lib.driver_set_led.restype = c_bool

        self.driver_lib.driver_set_fan.argtypes = [c_uint8]
        self.driver_lib.driver_set_fan.restype = c_bool

        self.driver_lib.driver_set_heater.argtypes = [c_uint8]
        self.driver_lib.driver_set_heater.restype = c_bool

        self.driver_lib.driver_set_doors.argtypes = [c_uint8]
        self.driver_lib.driver_set_doors.restype = c_bool

        self.driver_lib.driver_power_sensors.argtypes = [c_bool, c_bool]
        self.driver_lib.driver_power_sensors.restype = c_bool

        self.driver_lib.driver_power_actuators.argtypes = [
            c_bool,
            c_bool,
            c_bool,
            c_bool,
        ]
        self.driver_lib.driver_power_actuators.restype = c_bool

        self.driver_lib.driver_reset_sensors.argtypes = [c_bool, c_bool]
        self.driver_lib.driver_reset_sensors.restype = c_bool

        self.driver_lib.driver_reset_actuators.argtypes = [
            c_bool,
            c_bool,
            c_bool,
            c_bool,
        ]
        self.driver_lib.driver_reset_actuators.restype = c_bool

        self.driver_lib.driver_send_command.argtypes = [c_char_p, c_char_p]
        self.driver_lib.driver_send_command.restype = c_bool

        return True

    def init(self):
        """Initialize the driver."""
        if not self.driver_lib and not self.load_dll():
            return False

        # Create callback function
        self.callback_func = LogCallbackType(self.log_callback)

        # Initialize driver
        if not self.driver_lib.driver_init(self.callback_func):
            print("Failed to initialize driver")
            return False

        self.initialized = True
        return True

    def connect(self, host="localhost", port=8989):
        """Connect to the device."""
        if not self.initialized and not self.init():
            return False

        if self.connected:
            return True

        # Connect to device
        if not self.driver_lib.driver_connect(host.encode("utf-8"), port):
            print("Failed to connect to device")
            return False

        self.connected = True
        return True

    def disconnect(self):
        """Disconnect from the device."""
        if not self.connected:
            return True

        # Disconnect from device
        if not self.driver_lib.driver_disconnect():
            print("Failed to disconnect from device")
            return False

        self.connected = False
        return True

    def get_status(self):
        """Get device status."""
        if not self.connected:
            print("Not connected to device")
            return None

        status = DeviceStatus()
        if not self.driver_lib.driver_get_status(ctypes.byref(status)):
            print("Failed to get device status")
            return None

        return {
            "connected": status.connected,
            "sensors_powered": status.sensors_powered,
            "actuators_powered": status.actuators_powered,
            "has_errors": status.has_errors,
        }

    def get_sensors(self):
        """Get sensor data."""
        if not self.connected:
            print("Not connected to device")
            return None

        data = SensorData()
        if not self.driver_lib.driver_get_sensors(ctypes.byref(data)):
            print("Failed to get sensor data")
            return None

        return {
            "temperature_id": data.temperature_id,
            "temperature_value": data.temperature_value,
            "humidity_id": data.humidity_id,
            "humidity_value": data.humidity_value,
        }

    def get_actuators(self):
        """Get actuator data."""
        if not self.connected:
            print("Not connected to device")
            return None

        data = ActuatorData()
        if not self.driver_lib.driver_get_actuators(ctypes.byref(data)):
            print("Failed to get actuator data")
            return None

        return {
            "led_value": data.led_value,
            "fan_value": data.fan_value,
            "heater_value": data.heater_value,
            "doors_value": data.doors_value,
        }

    def set_led(self, value):
        """Set LED value."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_set_led(value)

    def set_fan(self, value):
        """Set fan value."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_set_fan(value)

    def set_heater(self, value):
        """Set heater value."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_set_heater(value)

    def set_doors(self, value):
        """Set doors value."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_set_doors(value)

    def power_sensors(self, temperature_on=True, humidity_on=True):
        """Power on/off sensors."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_power_sensors(temperature_on, humidity_on)

    def power_actuators(self, led_on=True, fan_on=True, heater_on=True, doors_on=True):
        """Power on/off actuators."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_power_actuators(
            led_on, fan_on, heater_on, doors_on
        )

    def reset_sensors(self, reset_temperature=True, reset_humidity=True):
        """Reset sensors."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_reset_sensors(reset_temperature, reset_humidity)

    def reset_actuators(
        self, reset_led=True, reset_fan=True, reset_heater=True, reset_doors=True
    ):
        """Reset actuators."""
        if not self.connected:
            print("Not connected to device")
            return False

        return self.driver_lib.driver_reset_actuators(
            reset_led, reset_fan, reset_heater, reset_doors
        )

    def send_command(self, command):
        """Send a raw command to the device."""
        if not self.connected:
            print("Not connected to device")
            return None

        response = ctypes.create_string_buffer(256)
        if not self.driver_lib.driver_send_command(command.encode("utf-8"), response):
            print("Failed to send command")
            return None

        return response.value.decode("utf-8")


def main():
    """Main function for testing the driver."""
    print("Semi-Vibe-Driver Python Test")
    print("--------------------------")

    driver = Driver()
    if not driver.init():
        return 1

    if not driver.connect():
        return 1

    # Get device status
    status = driver.get_status()
    if status:
        print("\nDevice status:")
        print(f"  Connected: {status['connected']}")
        print(f"  Sensors powered: {status['sensors_powered']}")
        print(f"  Actuators powered: {status['actuators_powered']}")
        print(f"  Has errors: {status['has_errors']}")

    # Get sensor data
    sensors = driver.get_sensors()
    if sensors:
        print("\nSensor data:")
        print(f"  Temperature ID: 0x{sensors['temperature_id']:02X}")
        print(f"  Temperature value: {sensors['temperature_value']}")
        print(f"  Humidity ID: 0x{sensors['humidity_id']:02X}")
        print(f"  Humidity value: {sensors['humidity_value']}")

    # Get actuator data
    actuators = driver.get_actuators()
    if actuators:
        print("\nActuator data:")
        print(f"  LED value: {actuators['led_value']}")
        print(f"  Fan value: {actuators['fan_value']}")
        print(f"  Heater value: {actuators['heater_value']}")
        print(f"  Doors value: 0x{actuators['doors_value']:02X}")

    # Test setting actuator values
    print("\nSetting LED to 128...")
    driver.set_led(128)

    print("Setting fan to 200...")
    driver.set_fan(200)

    print("Setting heater to 10...")
    driver.set_heater(10)

    print("Setting doors to 0x55...")
    driver.set_doors(0x55)

    # Get updated actuator data
    actuators = driver.get_actuators()
    if actuators:
        print("\nUpdated actuator data:")
        print(f"  LED value: {actuators['led_value']}")
        print(f"  Fan value: {actuators['fan_value']}")
        print(f"  Heater value: {actuators['heater_value']}")
        print(f"  Doors value: 0x{actuators['doors_value']:02X}")

    # Disconnect from device
    print("\nDisconnecting from device...")
    driver.disconnect()

    print("\nTest completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
