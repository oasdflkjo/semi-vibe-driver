"""
Python wrapper for the Semi-Vibe-Device DLL.
This script provides a simple interface to communicate with the device via the DLL.
"""

import ctypes
import os
import sys
from ctypes import c_bool, c_char_p, c_uint8, CFUNCTYPE, Structure, POINTER

# Define the callback function type
LOGCALLBACK = CFUNCTYPE(None, c_char_p)


# Define the DeviceMemory structure
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


class Device:
    """Semi-Vibe-Device simulator wrapper class."""

    def __init__(self, print_callback=None):
        """Initialize the device simulator.

        Args:
            print_callback: Optional function to handle print messages
        """
        self.print_callback = print_callback or print
        self.dll = None
        self.log_callback = None
        self.running = False
        self.dll_prints_enabled = True
        self.wrapper_prints_enabled = True

        # Load the DLL
        dll_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "build",
            "bin",
            "Debug",
            "semi_vibe_device.dll",
        )
        self._log(f"Looking for DLL at: {dll_path}")

        try:
            self.dll = ctypes.CDLL(dll_path)
            self._log("DLL loaded successfully")

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

            # Create log callback
            def log_callback_wrapper(message):
                if self.dll_prints_enabled:
                    self.print_callback(f"[DEVICE] {message.decode('utf-8')}")

            self.log_callback = LOGCALLBACK(log_callback_wrapper)

            # Initialize the device
            if not self.dll.device_init(self.log_callback):
                self._log("Failed to initialize device")
        except Exception as e:
            self._log(f"Failed to load DLL: {e}")
            self.dll = None

    def _log(self, message):
        """Log a message using the callback or print."""
        if self.wrapper_prints_enabled:
            self.print_callback(f"[DEVICE] {message}")

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

    def start(self, host="localhost", port=8989):
        """Start the device server."""
        if self.running:
            self._log("Server already running")
            return True

        if not self.dll:
            self._log("DLL not loaded")
            return False

        if self.dll.device_start():
            self.running = True
            self._log(f"Server started on {host}:{port}")
            return True
        else:
            self._log("Failed to start device")
            return False

    def stop(self):
        """Stop the device server."""
        if not self.running:
            return True

        if not self.dll:
            self._log("DLL not loaded")
            return False

        if self.dll.device_stop():
            self.running = False
            self._log("Server stopped")
            return True
        else:
            self._log("Failed to stop device")
            return False

    def get_memory(self):
        """Get the current device memory."""
        if not self.dll:
            self._log("DLL not loaded")
            return None

        memory = DeviceMemory()
        if self.dll.device_get_memory(ctypes.byref(memory)):
            return memory
        else:
            self._log("Failed to get device memory")
            return None

    def set_memory(self, memory):
        """Set the device memory directly."""
        if not self.dll:
            self._log("DLL not loaded")
            return False

        if self.dll.device_set_memory(ctypes.byref(memory)):
            return True
        else:
            self._log("Failed to set device memory")
            return False

    def process_command(self, command):
        """Process a command manually."""
        if not self.dll:
            self._log("DLL not loaded")
            return None

        command_bytes = command.encode("utf-8")
        response = ctypes.create_string_buffer(7)
        if self.dll.device_process_command(command_bytes, response):
            return response.value.decode("utf-8")
        else:
            self._log("Failed to process command")
            return None

    # Convenience methods to access device state
    @property
    def state(self):
        """Get the current device state."""
        memory = self.get_memory()
        if not memory:
            return {
                "status": {
                    "connected": False,
                    "sensors_powered": False,
                    "actuators_powered": False,
                    "has_errors": False,
                },
                "sensors": {
                    "temperature_id": 1,
                    "temperature_value": 25,
                    "humidity_id": 2,
                    "humidity_value": 50,
                },
                "actuators": {
                    "led_value": 0,
                    "fan_value": 0,
                    "heater_value": 0,
                    "doors_value": 0,
                },
            }

        return {
            "status": {
                "connected": bool(memory.connected_device),
                "sensors_powered": bool(memory.power_sensors),
                "actuators_powered": bool(memory.power_actuators),
                "has_errors": bool(memory.error_state),
            },
            "sensors": {
                "temperature_id": memory.sensor_a_id,
                "temperature_value": memory.sensor_a_reading,
                "humidity_id": memory.sensor_b_id,
                "humidity_value": memory.sensor_b_reading,
            },
            "actuators": {
                "led_value": memory.actuator_a,
                "fan_value": memory.actuator_b,
                "heater_value": memory.actuator_c,
                "doors_value": memory.actuator_d,
            },
        }

    @state.setter
    def state(self, new_state):
        """Set the device state directly (for testing)."""
        if not self.dll:
            self._log("DLL not loaded")
            return

        # Get current memory
        memory = self.get_memory()
        if not memory:
            self._log("Failed to get device memory")
            return

        # Update memory with new state
        if "sensors" in new_state:
            sensors = new_state["sensors"]
            if "temperature_value" in sensors:
                temp_value = sensors["temperature_value"]
                self._log(f"Setting temperature value to {temp_value}")
                memory.sensor_a_reading = temp_value

            if "humidity_value" in sensors:
                humid_value = sensors["humidity_value"]
                self._log(f"Setting humidity value to {humid_value}")
                memory.sensor_b_reading = humid_value

        if "actuators" in new_state:
            actuators = new_state["actuators"]
            if "led_value" in actuators:
                memory.actuator_a = actuators["led_value"]
            if "fan_value" in actuators:
                memory.actuator_b = actuators["fan_value"]
            if "heater_value" in actuators:
                memory.actuator_c = actuators["heater_value"]
            if "doors_value" in actuators:
                memory.actuator_d = actuators["doors_value"]

        # Write memory back to device
        self._log(
            f"Writing memory back to device: temp={memory.sensor_a_reading}, humid={memory.sensor_b_reading}"
        )
        result = self.set_memory(memory)
        self._log(f"Set memory result: {result}")

        # Verify the memory was updated
        updated_memory = self.get_memory()
        if updated_memory:
            self._log(
                f"Verified memory: temp={updated_memory.sensor_a_reading}, humid={updated_memory.sensor_b_reading}"
            )
        else:
            self._log("Failed to verify memory update")

    def set_led(self, value):
        """Set the LED value directly."""
        self._log(f"Setting LED value to {value}")

        # Get current state
        current_state = self.state

        # Update LED value
        current_state["actuators"]["led_value"] = value

        # Set the updated state
        self.state = current_state

        # Verify the update
        updated_state = self.state
        led_value = updated_state["actuators"]["led_value"]
        self._log(f"Verified LED value: {led_value}")

        return led_value == value
