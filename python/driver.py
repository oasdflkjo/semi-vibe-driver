"""
Python wrapper for the Semi-Vibe-Driver DLL.
This script provides a direct 1:1 interface to the driver DLL functions with zero logic.
"""

import ctypes
import os
from ctypes import c_bool, c_char_p, c_uint8, c_int, CFUNCTYPE, Structure, POINTER

# Define the callback function type
LOGCALLBACK = CFUNCTYPE(None, c_char_p)

# Door identifiers
DOOR_1 = 1
DOOR_2 = 2
DOOR_3 = 3
DOOR_4 = 4

# Door states
DOOR_CLOSED = 0
DOOR_OPEN = 1

# Component types
COMPONENT_TEMPERATURE = 0
COMPONENT_HUMIDITY = 1
COMPONENT_LED = 2
COMPONENT_FAN = 3
COMPONENT_HEATER = 4
COMPONENT_DOORS = 5


# Define the structures to match the C structures
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


class DriverDLL:
    """Direct 1:1 wrapper for the Semi-Vibe-Driver DLL with zero logic."""

    def __init__(self, dll_path=None):
        """Initialize the DLL wrapper.

        Args:
            dll_path: Optional path to the DLL file
        """
        if dll_path is None:
            dll_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "build",
                "bin",
                "Debug",
                "semi_vibe_driver.dll",
            )

        self.dll = ctypes.WinDLL(dll_path)
        self._callback = None  # Store the callback to prevent garbage collection

        # Define function prototypes
        self.dll.driver_init.argtypes = [LOGCALLBACK]
        self.dll.driver_init.restype = c_bool

        self.dll.driver_connect.argtypes = [c_char_p, c_int]
        self.dll.driver_connect.restype = c_bool

        self.dll.driver_disconnect.argtypes = []
        self.dll.driver_disconnect.restype = c_bool

        self.dll.driver_get_status.argtypes = [POINTER(DeviceStatus)]
        self.dll.driver_get_status.restype = c_bool

        self.dll.driver_get_humidity.argtypes = [POINTER(c_uint8)]
        self.dll.driver_get_humidity.restype = c_bool

        self.dll.driver_get_temperature.argtypes = [POINTER(c_uint8)]
        self.dll.driver_get_temperature.restype = c_bool

        self.dll.driver_set_led.argtypes = [c_uint8]
        self.dll.driver_set_led.restype = c_bool

        self.dll.driver_get_led.argtypes = [POINTER(c_uint8)]
        self.dll.driver_get_led.restype = c_bool

        self.dll.driver_set_fan.argtypes = [c_uint8]
        self.dll.driver_set_fan.restype = c_bool

        self.dll.driver_get_fan.argtypes = [POINTER(c_uint8)]
        self.dll.driver_get_fan.restype = c_bool

        self.dll.driver_set_heater.argtypes = [c_uint8]
        self.dll.driver_set_heater.restype = c_bool

        self.dll.driver_get_heater.argtypes = [POINTER(c_uint8)]
        self.dll.driver_get_heater.restype = c_bool

        self.dll.driver_set_door.argtypes = [c_int, c_int]
        self.dll.driver_set_door.restype = c_bool

        self.dll.driver_get_door_state.argtypes = [c_int, POINTER(c_int)]
        self.dll.driver_get_door_state.restype = c_bool

        self.dll.driver_power_sensors.argtypes = [c_bool, c_bool]
        self.dll.driver_power_sensors.restype = c_bool

        self.dll.driver_power_actuators.argtypes = [c_bool, c_bool, c_bool, c_bool]
        self.dll.driver_power_actuators.restype = c_bool

        self.dll.driver_reset_sensors.argtypes = [c_bool, c_bool]
        self.dll.driver_reset_sensors.restype = c_bool

        self.dll.driver_reset_actuators.argtypes = [c_bool, c_bool, c_bool, c_bool]
        self.dll.driver_reset_actuators.restype = c_bool

        self.dll.driver_get_power_state.argtypes = [c_int, POINTER(c_bool)]
        self.dll.driver_get_power_state.restype = c_bool

        self.dll.driver_get_error_state.argtypes = [c_int, POINTER(c_bool)]
        self.dll.driver_get_error_state.restype = c_bool

        self.dll.driver_set_power_state.argtypes = [c_int, c_bool]
        self.dll.driver_set_power_state.restype = c_bool

        self.dll.driver_reset_component.argtypes = [c_int]
        self.dll.driver_reset_component.restype = c_bool

        self.dll.driver_send_command.argtypes = [c_char_p, c_char_p]
        self.dll.driver_send_command.restype = c_bool

    def init(self, log_callback):
        """Initialize the driver.

        Args:
            log_callback: Callback function for logging

        Returns:
            bool: True if successful
        """
        self._callback = LOGCALLBACK(log_callback)
        return self.dll.driver_init(self._callback)

    def connect(self, host, port):
        """Connect to the device.

        Args:
            host: Hostname or IP address
            port: Port number

        Returns:
            bool: True if successful
        """
        host_bytes = host.encode("utf-8")
        return self.dll.driver_connect(host_bytes, port)

    def disconnect(self):
        """Disconnect from the device.

        Returns:
            bool: True if successful
        """
        return self.dll.driver_disconnect()

    def get_status(self, status):
        """Get device status.

        Args:
            status: DeviceStatus structure to fill

        Returns:
            bool: True if successful
        """
        return self.dll.driver_get_status(ctypes.byref(status))

    def get_humidity(self):
        """Get humidity value.

        Returns:
            int: Humidity value (0-100) or None if failed
        """
        value = c_uint8()
        if self.dll.driver_get_humidity(ctypes.byref(value)):
            return value.value
        return None

    def get_temperature(self):
        """Get temperature value.

        Returns:
            int: Temperature value (0-100) or None if failed
        """
        value = c_uint8()
        if self.dll.driver_get_temperature(ctypes.byref(value)):
            return value.value
        return None

    def set_led(self, value):
        """Set LED value.

        Args:
            value: Value to set (0-255)

        Returns:
            bool: True if successful
        """
        return self.dll.driver_set_led(value)

    def get_led(self):
        """Get LED value.

        Returns:
            int: LED value (0-255) or None if failed
        """
        value = c_uint8()
        if self.dll.driver_get_led(ctypes.byref(value)):
            return value.value
        return None

    def set_fan(self, value):
        """Set fan value.

        Args:
            value: Value to set (0-255)

        Returns:
            bool: True if successful
        """
        return self.dll.driver_set_fan(value)

    def get_fan(self):
        """Get fan value.

        Returns:
            int: Fan speed (0-255) or None if failed
        """
        value = c_uint8()
        if self.dll.driver_get_fan(ctypes.byref(value)):
            return value.value
        return None

    def set_heater(self, value):
        """Set heater value.

        Args:
            value: Value to set (0-15)

        Returns:
            bool: True if successful
        """
        return self.dll.driver_set_heater(value)

    def get_heater(self):
        """Get heater value.

        Returns:
            int: Heater value (0-15) or None if failed
        """
        value = c_uint8()
        if self.dll.driver_get_heater(ctypes.byref(value)):
            return value.value
        return None

    def set_door(self, door_id, state):
        """Set the state of a specific door.

        Args:
            door_id: Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)
            state: Door state (DOOR_OPEN or DOOR_CLOSED)

        Returns:
            bool: True if successful
        """
        return self.dll.driver_set_door(door_id, state)

    def get_door_state(self, door_id):
        """Get the state of a specific door.

        Args:
            door_id: Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)

        Returns:
            int: Door state (DOOR_OPEN or DOOR_CLOSED) or None if failed
        """
        state = c_int()
        if self.dll.driver_get_door_state(door_id, ctypes.byref(state)):
            return state.value
        return None

    def power_sensors(self, temperature_on, humidity_on):
        """Power sensors on/off.

        Args:
            temperature_on: Power state for temperature sensor
            humidity_on: Power state for humidity sensor

        Returns:
            bool: True if successful
        """
        return self.dll.driver_power_sensors(temperature_on, humidity_on)

    def power_actuators(self, led_on, fan_on, heater_on, doors_on):
        """Power actuators on/off.

        Args:
            led_on: Power state for LED
            fan_on: Power state for fan
            heater_on: Power state for heater
            doors_on: Power state for doors

        Returns:
            bool: True if successful
        """
        return self.dll.driver_power_actuators(led_on, fan_on, heater_on, doors_on)

    def reset_sensors(self, reset_temperature, reset_humidity):
        """Reset sensors.

        Args:
            reset_temperature: Reset temperature sensor
            reset_humidity: Reset humidity sensor

        Returns:
            bool: True if successful
        """
        return self.dll.driver_reset_sensors(reset_temperature, reset_humidity)

    def reset_actuators(self, reset_led, reset_fan, reset_heater, reset_doors):
        """Reset actuators.

        Args:
            reset_led: Reset LED
            reset_fan: Reset fan
            reset_heater: Reset heater
            reset_doors: Reset doors

        Returns:
            bool: True if successful
        """
        return self.dll.driver_reset_actuators(
            reset_led, reset_fan, reset_heater, reset_doors
        )

    def get_power_state(self, component_type):
        """Get power state of a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)

        Returns:
            bool: True if powered, False if not powered, None if failed
        """
        powered = c_bool()
        if self.dll.driver_get_power_state(component_type, ctypes.byref(powered)):
            return powered.value
        return None

    def get_error_state(self, component_type):
        """Get error state of a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)

        Returns:
            bool: True if error, False if no error, None if failed
        """
        has_error = c_bool()
        if self.dll.driver_get_error_state(component_type, ctypes.byref(has_error)):
            return has_error.value
        return None

    def set_power_state(self, component_type, powered):
        """Set power state of a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)
            powered: True if powered, False if not powered

        Returns:
            bool: True if successful
        """
        return self.dll.driver_set_power_state(component_type, powered)

    def reset_component(self, component_type):
        """Reset a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)

        Returns:
            bool: True if successful
        """
        return self.dll.driver_reset_component(component_type)

    def send_command(self, command, response_buffer):
        """Send a raw command to the device.

        Args:
            command: Command string (6 hex digits)
            response_buffer: Buffer to store the response

        Returns:
            bool: True if successful
        """
        command_bytes = command.encode("utf-8")
        return self.dll.driver_send_command(command_bytes, response_buffer)
