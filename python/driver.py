"""
Python wrapper for the Semi-Vibe-Driver DLL.
This script provides a simple interface to communicate with the device via the DLL.
"""

import ctypes
import os
import sys
from ctypes import c_bool, c_char_p, c_uint8, c_int, CFUNCTYPE, Structure, POINTER

# Define the callback function type
LOGCALLBACK = CFUNCTYPE(None, c_char_p)


# Define the structures
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

    def __init__(self, print_callback=None):
        """Initialize the driver.

        Args:
            print_callback: Optional function to handle print messages
        """
        self.print_callback = print_callback or print
        self.dll = None
        self.log_callback = None
        self.initialized = False
        self.connected = False
        self.dll_prints_enabled = True
        self.wrapper_prints_enabled = True

        # Load the DLL
        dll_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "build",
            "bin",
            "Debug",
            "semi_vibe_driver.dll",
        )
        self._log(f"Looking for DLL at: {dll_path}")

        try:
            self.dll = ctypes.CDLL(dll_path)
            self._log("DLL loaded successfully")

            # Define function prototypes
            self.dll.driver_init.argtypes = [LOGCALLBACK]
            self.dll.driver_init.restype = c_bool

            self.dll.driver_connect.argtypes = [c_char_p, c_int]
            self.dll.driver_connect.restype = c_bool

            self.dll.driver_disconnect.argtypes = []
            self.dll.driver_disconnect.restype = c_bool

            self.dll.driver_get_status.argtypes = [POINTER(DeviceStatus)]
            self.dll.driver_get_status.restype = c_bool

            self.dll.driver_get_sensors.argtypes = [POINTER(SensorData)]
            self.dll.driver_get_sensors.restype = c_bool

            self.dll.driver_get_actuators.argtypes = [POINTER(ActuatorData)]
            self.dll.driver_get_actuators.restype = c_bool

            self.dll.driver_set_led.argtypes = [c_uint8]
            self.dll.driver_set_led.restype = c_bool

            self.dll.driver_set_fan.argtypes = [c_uint8]
            self.dll.driver_set_fan.restype = c_bool

            self.dll.driver_set_heater.argtypes = [c_uint8]
            self.dll.driver_set_heater.restype = c_bool

            self.dll.driver_set_doors.argtypes = [c_uint8]
            self.dll.driver_set_doors.restype = c_bool

            self.dll.driver_power_sensors.argtypes = [c_bool, c_bool]
            self.dll.driver_power_sensors.restype = c_bool

            self.dll.driver_power_actuators.argtypes = [c_bool, c_bool, c_bool, c_bool]
            self.dll.driver_power_actuators.restype = c_bool

            # Create log callback
            def log_callback_wrapper(message):
                if self.dll_prints_enabled:
                    self.print_callback(f"[DRIVER] {message.decode('utf-8')}")

            self.log_callback = LOGCALLBACK(log_callback_wrapper)
        except Exception as e:
            self._log(f"Failed to load DLL: {e}")
            self.dll = None

    def _log(self, message):
        """Log a message using the callback or print."""
        if self.wrapper_prints_enabled:
            self.print_callback(f"[DRIVER] {message}")

    def enable_dll_prints(self, enabled=True):
        """Enable or disable prints from the DLL.

        Args:
            enabled: Whether DLL prints should be enabled

        Returns:
            None
        """
        self.dll_prints_enabled = enabled

    def disable_dll_prints(self):
        """Disable prints from the DLL.

        Returns:
            None
        """
        self.dll_prints_enabled = False

    def enable_wrapper_prints(self, enabled=True):
        """Enable or disable prints from the wrapper.

        Args:
            enabled: Whether wrapper prints should be enabled

        Returns:
            None
        """
        self.wrapper_prints_enabled = enabled

    def disable_wrapper_prints(self):
        """Disable prints from the wrapper.

        Returns:
            None
        """
        self.wrapper_prints_enabled = False

    def init(self):
        """Initialize the driver."""
        if self.initialized:
            self._log("Driver is already initialized")
            return True

        if not self.dll:
            self._log("DLL not loaded")
            return False

        if self.dll.driver_init(self.log_callback):
            self.initialized = True
            self._log("Driver initialized")
            return True
        else:
            self._log("Failed to initialize driver")
            return False

    def connect(self, host="localhost", port=8989):
        """Connect to the device."""
        if self.connected:
            self._log("Driver is already connected")
            return True

        if not self.initialized:
            self._log("Driver is not initialized")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        host_bytes = host.encode("utf-8")
        if self.dll.driver_connect(host_bytes, port):
            self.connected = True
            self._log(f"Connected to device at {host}:{port}")
            return True
        else:
            self._log("Failed to connect to device")
            return False

    def disconnect(self):
        """Disconnect from the device."""
        if not self.connected:
            self._log("Driver is not connected")
            return True

        if not self.dll:
            self._log("DLL not loaded")
            return False

        if self.dll.driver_disconnect():
            self.connected = False
            self._log("Disconnected from device")
            return True
        else:
            self._log("Failed to disconnect from device")
            return False

    def get_status(self):
        """Get device status."""
        if not self.connected:
            self._log("Driver is not connected")
            return None

        if not self.dll:
            self._log("DLL not loaded")
            return None

        status = DeviceStatus()
        if self.dll.driver_get_status(ctypes.byref(status)):
            return {
                "connected": status.connected,
                "sensors_powered": status.sensors_powered,
                "actuators_powered": status.actuators_powered,
                "has_errors": status.has_errors,
            }
        else:
            self._log("Failed to get device status")
            return None

    def get_sensors(self):
        """Get sensor data."""
        if not self.connected:
            self._log("Driver is not connected")
            return None

        if not self.dll:
            self._log("DLL not loaded")
            return None

        data = SensorData()
        if self.dll.driver_get_sensors(ctypes.byref(data)):
            return {
                "temperature_id": data.temperature_id,
                "temperature_value": data.temperature_value,
                "humidity_id": data.humidity_id,
                "humidity_value": data.humidity_value,
            }
        else:
            self._log("Failed to get sensor data")
            return None

    def get_actuators(self):
        """Get actuator data."""
        if not self.connected:
            self._log("Driver is not connected")
            return None

        if not self.dll:
            self._log("DLL not loaded")
            return None

        data = ActuatorData()
        if self.dll.driver_get_actuators(ctypes.byref(data)):
            return {
                "led_value": data.led_value,
                "fan_value": data.fan_value,
                "heater_value": data.heater_value,
                "doors_value": data.doors_value,
            }
        else:
            self._log("Failed to get actuator data")
            return None

    def set_led(self, value):
        """Set LED value."""
        if not self.connected:
            self._log("Driver is not connected")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        return self.dll.driver_set_led(value)

    def set_fan(self, value):
        """Set fan value."""
        if not self.connected:
            self._log("Driver is not connected")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        return self.dll.driver_set_fan(value)

    def set_heater(self, value):
        """Set heater value."""
        if not self.connected:
            self._log("Driver is not connected")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        return self.dll.driver_set_heater(value)

    def set_doors(self, value):
        """Set doors value."""
        if not self.connected:
            self._log("Driver is not connected")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        return self.dll.driver_set_doors(value)

    def power_sensors(self, temperature_on, humidity_on):
        """Power sensors on/off.

        Args:
            temperature_on: Whether temperature sensor should be powered
            humidity_on: Whether humidity sensor should be powered

        Returns:
            bool: True if successful
        """
        if not self.connected:
            self._log("Driver is not connected")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        # Define function prototype if not already defined
        if not hasattr(self.dll, "driver_power_sensors"):
            self.dll.driver_power_sensors.argtypes = [c_bool, c_bool]
            self.dll.driver_power_sensors.restype = c_bool

        return self.dll.driver_power_sensors(temperature_on, humidity_on)

    def power_actuators(self, led_on, fan_on, heater_on, doors_on):
        """Power actuators on/off.

        Args:
            led_on: Whether LED should be powered
            fan_on: Whether fan should be powered
            heater_on: Whether heater should be powered
            doors_on: Whether doors should be powered

        Returns:
            bool: True if successful
        """
        if not self.connected:
            self._log("Driver is not connected")
            return False

        if not self.dll:
            self._log("DLL not loaded")
            return False

        # Define function prototype if not already defined
        if not hasattr(self.dll, "driver_power_actuators"):
            self.dll.driver_power_actuators.argtypes = [c_bool, c_bool, c_bool, c_bool]
            self.dll.driver_power_actuators.restype = c_bool

        return self.dll.driver_power_actuators(led_on, fan_on, heater_on, doors_on)

    def send_raw_command(self, command):
        """Send a raw command to the device.

        Args:
            command: Command string (6 hex digits)

        Returns:
            str: Response from the device, or None if failed
        """
        if not self.connected:
            self._log("Driver is not connected")
            return None

        if not self.dll:
            self._log("DLL not loaded")
            return None

        # Validate command format
        if not command or len(command) != 6:
            self._log(f"Invalid command format: {command}")
            return None

        # Define function prototype if not already defined
        if not hasattr(self.dll, "driver_send_command"):
            self.dll.driver_send_command.argtypes = [c_char_p, c_char_p]
            self.dll.driver_send_command.restype = c_bool

        # Prepare buffers
        command_bytes = command.encode("utf-8")
        response_buffer = ctypes.create_string_buffer(
            7
        )  # 6 hex digits + null terminator

        # Send command
        result = self.dll.driver_send_command(command_bytes, response_buffer)
        if not result:
            self._log(f"Failed to send command: {command}")
            return None

        # Return response as string
        return response_buffer.value.decode("utf-8")
