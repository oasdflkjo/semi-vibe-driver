"""
Python wrapper for the Semi-Vibe-Device DLL.
This script provides a direct 1:1 interface to the device DLL functions with zero logic.
"""

import ctypes
import os
from ctypes import c_bool, c_char_p, c_uint8, CFUNCTYPE, Structure, POINTER

# Define the callback function type
LOGCALLBACK = CFUNCTYPE(None, c_char_p)


# Define the DeviceMemory structure to match the C structure
class DeviceMemory(Structure):
    _fields_ = [
        # MAIN
        ("connected_device", c_uint8),
        ("reserved_main", c_uint8),
        ("power_state", c_uint8),
        ("error_state", c_uint8),
        # SENSOR
        ("sensor_a_id", c_uint8),
        ("sensor_a_reading", c_uint8),
        ("sensor_b_id", c_uint8),
        ("sensor_b_reading", c_uint8),
        # ACTUATOR
        ("actuator_a", c_uint8),  # LED
        ("actuator_b", c_uint8),  # Fan
        ("actuator_c", c_uint8),  # Heater
        ("actuator_d", c_uint8),  # Doors
        # CONTROL
        ("power_sensors", c_uint8),
        ("power_actuators", c_uint8),
        ("reset_sensors", c_uint8),
        ("reset_actuators", c_uint8),
    ]


class DeviceDLL:
    """Direct 1:1 wrapper for the Semi-Vibe-Device DLL with zero logic."""

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
                "semi_vibe_device.dll",
            )

        self.dll = ctypes.WinDLL(dll_path)
        self._callback = None  # Store the callback to prevent garbage collection

        # Define function prototypes
        self.dll.device_init.argtypes = [LOGCALLBACK]
        self.dll.device_init.restype = c_bool

        self.dll.device_start.argtypes = []
        self.dll.device_start.restype = c_bool

        self.dll.device_stop.argtypes = []
        self.dll.device_stop.restype = c_bool

        self.dll.device_get_memory.argtypes = [POINTER(DeviceMemory)]
        self.dll.device_get_memory.restype = c_bool

        self.dll.device_set_memory.argtypes = [POINTER(DeviceMemory)]
        self.dll.device_set_memory.restype = c_bool

        self.dll.device_process_command.argtypes = [c_char_p, c_char_p]
        self.dll.device_process_command.restype = c_bool

    def init(self, log_callback):
        """Initialize the device.

        Args:
            log_callback: Callback function for logging

        Returns:
            bool: True if successful
        """
        self._callback = LOGCALLBACK(log_callback)
        return self.dll.device_init(self._callback)

    def start(self):
        """Start the device server.

        Returns:
            bool: True if successful
        """
        return self.dll.device_start()

    def stop(self):
        """Stop the device server.

        Returns:
            bool: True if successful
        """
        return self.dll.device_stop()

    def get_memory(self, memory):
        """Get the current device memory.

        Args:
            memory: DeviceMemory structure to fill

        Returns:
            bool: True if successful
        """
        return self.dll.device_get_memory(ctypes.byref(memory))

    def set_memory(self, memory):
        """Set the device memory.

        Args:
            memory: DeviceMemory structure with new values

        Returns:
            bool: True if successful
        """
        return self.dll.device_set_memory(ctypes.byref(memory))

    def process_command(self, command, response_buffer):
        """Process a command manually.

        Args:
            command: Command string (6 hex digits)
            response_buffer: Buffer to store the response

        Returns:
            bool: True if successful
        """
        command_bytes = command.encode("utf-8")
        return self.dll.device_process_command(command_bytes, response_buffer)
