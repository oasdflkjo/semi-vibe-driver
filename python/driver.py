"""
Python wrapper for the Semi-Vibe-Driver DLL.
This script provides a direct 1:1 interface to the driver DLL functions with zero logic.
"""

import ctypes
import os
from ctypes import (
    c_bool,
    c_char_p,
    c_uint8,
    c_int,
    CFUNCTYPE,
    Structure,
    POINTER,
    c_void_p,
)

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

# Error codes
DRIVER_ERROR_NONE = 0
DRIVER_ERROR_INVALID_PARAMETER = 1
DRIVER_ERROR_NOT_INITIALIZED = 2
DRIVER_ERROR_ALREADY_INITIALIZED = 3
DRIVER_ERROR_NOT_CONNECTED = 4
DRIVER_ERROR_ALREADY_CONNECTED = 5
DRIVER_ERROR_CONNECTION_FAILED = 6
DRIVER_ERROR_COMMUNICATION_FAILED = 7
DRIVER_ERROR_PROTOCOL_ERROR = 8
DRIVER_ERROR_DEVICE_ERROR = 9
DRIVER_ERROR_INTERNAL = 10
DRIVER_ERROR_RESOURCE_UNAVAILABLE = 11


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
        self._handle = None  # Store the driver handle
        self._error_code = c_int(0)  # Store the error code

        # Define function prototypes for the new handle-based API
        self.dll.driver_create.argtypes = [
            POINTER(c_void_p),
            LOGCALLBACK,
            POINTER(c_int),
        ]
        self.dll.driver_create.restype = c_bool

        self.dll.driver_destroy.argtypes = [c_void_p, POINTER(c_int)]
        self.dll.driver_destroy.restype = c_bool

        self.dll.driver_get_last_error_message.argtypes = [c_void_p, c_char_p, c_int]
        self.dll.driver_get_last_error_message.restype = c_bool

        self.dll.driver_set_timeout.argtypes = [c_void_p, c_uint8, POINTER(c_int)]
        self.dll.driver_set_timeout.restype = c_bool

        self.dll.driver_connect.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_int)]
        self.dll.driver_connect.restype = c_bool

        self.dll.driver_disconnect.argtypes = [c_void_p, POINTER(c_int)]
        self.dll.driver_disconnect.restype = c_bool

        self.dll.driver_get_status.argtypes = [
            c_void_p,
            POINTER(DeviceStatus),
            POINTER(c_int),
        ]
        self.dll.driver_get_status.restype = c_bool

        self.dll.driver_get_humidity.argtypes = [
            c_void_p,
            POINTER(c_uint8),
            POINTER(c_int),
        ]
        self.dll.driver_get_humidity.restype = c_bool

        self.dll.driver_get_temperature.argtypes = [
            c_void_p,
            POINTER(c_uint8),
            POINTER(c_int),
        ]
        self.dll.driver_get_temperature.restype = c_bool

        self.dll.driver_set_led.argtypes = [c_void_p, c_uint8, POINTER(c_int)]
        self.dll.driver_set_led.restype = c_bool

        self.dll.driver_get_led.argtypes = [c_void_p, POINTER(c_uint8), POINTER(c_int)]
        self.dll.driver_get_led.restype = c_bool

        self.dll.driver_set_fan.argtypes = [c_void_p, c_uint8, POINTER(c_int)]
        self.dll.driver_set_fan.restype = c_bool

        self.dll.driver_get_fan.argtypes = [c_void_p, POINTER(c_uint8), POINTER(c_int)]
        self.dll.driver_get_fan.restype = c_bool

        self.dll.driver_set_heater.argtypes = [c_void_p, c_uint8, POINTER(c_int)]
        self.dll.driver_set_heater.restype = c_bool

        self.dll.driver_get_heater.argtypes = [
            c_void_p,
            POINTER(c_uint8),
            POINTER(c_int),
        ]
        self.dll.driver_get_heater.restype = c_bool

        self.dll.driver_set_door.argtypes = [c_void_p, c_int, c_int, POINTER(c_int)]
        self.dll.driver_set_door.restype = c_bool

        self.dll.driver_get_door_state.argtypes = [
            c_void_p,
            c_int,
            POINTER(c_int),
            POINTER(c_int),
        ]
        self.dll.driver_get_door_state.restype = c_bool

        self.dll.driver_get_power_state.argtypes = [
            c_void_p,
            c_int,
            POINTER(c_bool),
            POINTER(c_int),
        ]
        self.dll.driver_get_power_state.restype = c_bool

        self.dll.driver_get_error_state.argtypes = [
            c_void_p,
            c_int,
            POINTER(c_bool),
            POINTER(c_int),
        ]
        self.dll.driver_get_error_state.restype = c_bool

        self.dll.driver_set_power_state.argtypes = [
            c_void_p,
            c_int,
            c_bool,
            POINTER(c_int),
        ]
        self.dll.driver_set_power_state.restype = c_bool

        self.dll.driver_reset_component.argtypes = [c_void_p, c_int, POINTER(c_int)]
        self.dll.driver_reset_component.restype = c_bool

        self.dll.driver_send_command.argtypes = [
            c_void_p,
            c_char_p,
            c_char_p,
            POINTER(c_int),
        ]
        self.dll.driver_send_command.restype = c_bool

    def set_log_callback(self, log_callback):
        """Set the log callback function.

        This is used by the test utilities to set the callback before initialization.

        Args:
            log_callback: Callback function for logging

        Returns:
            bool: True if successful
        """
        self._callback = LOGCALLBACK(log_callback)
        return True

    def initialize(self):
        """Initialize the driver using the previously set callback.

        This is used by the test utilities for consistency.

        Returns:
            bool: True if successful
        """
        if self._callback is None:
            return False
        return self.init(self._callback)

    def init(self, log_callback):
        """Initialize the driver.

        Args:
            log_callback: Callback function for logging

        Returns:
            bool: True if successful
        """
        self._callback = LOGCALLBACK(log_callback)
        handle_ptr = c_void_p()
        result = self.dll.driver_create(
            ctypes.byref(handle_ptr), self._callback, ctypes.byref(self._error_code)
        )
        if result:
            self._handle = handle_ptr
        return result

    def connect(self, host, port):
        """Connect to the device.

        Args:
            host: Hostname or IP address
            port: Port number

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        host_bytes = host.encode("utf-8")
        return self.dll.driver_connect(
            self._handle, host_bytes, port, ctypes.byref(self._error_code)
        )

    def disconnect(self):
        """Disconnect from the device.

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        return self.dll.driver_disconnect(self._handle, ctypes.byref(self._error_code))

    def get_status(self, status):
        """Get device status.

        Args:
            status: DeviceStatus structure to fill

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        return self.dll.driver_get_status(
            self._handle, ctypes.byref(status), ctypes.byref(self._error_code)
        )

    def get_humidity(self):
        """Get humidity value.

        Returns:
            int: Humidity value (0-100) or None if failed
        """
        if self._handle is None:
            return None
        value = c_uint8()
        if self.dll.driver_get_humidity(
            self._handle, ctypes.byref(value), ctypes.byref(self._error_code)
        ):
            return value.value
        return None

    def get_temperature(self):
        """Get temperature value.

        Returns:
            int: Temperature value (0-100) or None if failed
        """
        if self._handle is None:
            return None
        value = c_uint8()
        if self.dll.driver_get_temperature(
            self._handle, ctypes.byref(value), ctypes.byref(self._error_code)
        ):
            return value.value
        return None

    def set_led(self, value):
        """Set LED value.

        Args:
            value: Value to set (0-255)

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        return self.dll.driver_set_led(
            self._handle, value, ctypes.byref(self._error_code)
        )

    def get_led(self):
        """Get LED value.

        Returns:
            int: LED value (0-255) or None if failed
        """
        if self._handle is None:
            return None
        value = c_uint8()
        if self.dll.driver_get_led(
            self._handle, ctypes.byref(value), ctypes.byref(self._error_code)
        ):
            return value.value
        return None

    def set_fan(self, value):
        """Set fan value.

        Args:
            value: Value to set (0-255)

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        return self.dll.driver_set_fan(
            self._handle, value, ctypes.byref(self._error_code)
        )

    def get_fan(self):
        """Get fan value.

        Returns:
            int: Fan speed (0-255) or None if failed
        """
        if self._handle is None:
            return None
        value = c_uint8()
        if self.dll.driver_get_fan(
            self._handle, ctypes.byref(value), ctypes.byref(self._error_code)
        ):
            return value.value
        return None

    def set_heater(self, value):
        """Set heater value.

        Args:
            value: Value to set (0-15)

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        return self.dll.driver_set_heater(
            self._handle, value, ctypes.byref(self._error_code)
        )

    def get_heater(self):
        """Get heater value.

        Returns:
            int: Heater value (0-15) or None if failed
        """
        if self._handle is None:
            return None
        value = c_uint8()
        if self.dll.driver_get_heater(
            self._handle, ctypes.byref(value), ctypes.byref(self._error_code)
        ):
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
        if self._handle is None:
            return False
        return self.dll.driver_set_door(
            self._handle, door_id, state, ctypes.byref(self._error_code)
        )

    def get_door_state(self, door_id):
        """Get the state of a specific door.

        Args:
            door_id: Door identifier (DOOR_1, DOOR_2, DOOR_3, or DOOR_4)

        Returns:
            int: Door state (DOOR_OPEN or DOOR_CLOSED) or None if failed
        """
        if self._handle is None:
            return None
        state = c_int()
        if self.dll.driver_get_door_state(
            self._handle, door_id, ctypes.byref(state), ctypes.byref(self._error_code)
        ):
            return state.value
        return None

    def get_power_state(self, component_type):
        """Get power state of a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)

        Returns:
            bool: True if powered, False if not powered, None if failed
        """
        if self._handle is None:
            return None
        powered = c_bool()
        if self.dll.driver_get_power_state(
            self._handle,
            component_type,
            ctypes.byref(powered),
            ctypes.byref(self._error_code),
        ):
            return powered.value
        return None

    def get_error_state(self, component_type):
        """Get error state of a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)

        Returns:
            bool: True if error, False if no error, None if failed
        """
        if self._handle is None:
            return None
        has_error = c_bool()
        if self.dll.driver_get_error_state(
            self._handle,
            component_type,
            ctypes.byref(has_error),
            ctypes.byref(self._error_code),
        ):
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
        if self._handle is None:
            return False
        return self.dll.driver_set_power_state(
            self._handle, component_type, powered, ctypes.byref(self._error_code)
        )

    def reset_component(self, component_type):
        """Reset a specific component.

        Args:
            component_type: Component type (COMPONENT_TEMPERATURE, COMPONENT_HUMIDITY, etc.)

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        return self.dll.driver_reset_component(
            self._handle, component_type, ctypes.byref(self._error_code)
        )

    def send_command(self, command, response_buffer):
        """Send a raw command to the device.

        Args:
            command: Command string (6 hex digits)
            response_buffer: Buffer to store the response

        Returns:
            bool: True if successful
        """
        if self._handle is None:
            return False
        command_bytes = command.encode("utf-8")
        return self.dll.driver_send_command(
            self._handle, command_bytes, response_buffer, ctypes.byref(self._error_code)
        )

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, "_handle") and self._handle is not None:
            self.dll.driver_destroy(self._handle, ctypes.byref(self._error_code))
            self._handle = None
