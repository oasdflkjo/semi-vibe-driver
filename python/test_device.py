"""
Test script for the Semi-Vibe-Device simulator DLL.
"""

import ctypes
import os
import sys
import time
from ctypes import c_bool, c_char_p, c_uint8, Structure, CFUNCTYPE, POINTER

# Define the callback function type
LogCallbackType = CFUNCTYPE(None, c_char_p)

# Define the DeviceMemory structure
class DeviceMemory(Structure):
    _fields_ = [
        # MAIN (base address 1)
        ("connected_device", c_uint8),  # 0x00
        ("reserved_main", c_uint8),     # 0x01
        ("power_state", c_uint8),       # 0x02
        ("error_state", c_uint8),       # 0x03

        # SENSOR (base address 2)
        ("sensor_a_id", c_uint8),       # 0x10
        ("sensor_a_reading", c_uint8),  # 0x11
        ("sensor_b_id", c_uint8),       # 0x20
        ("sensor_b_reading", c_uint8),  # 0x21

        # ACTUATOR (base address 3)
        ("actuator_a", c_uint8),        # 0x10 (LED)
        ("actuator_b", c_uint8),        # 0x20 (fan)
        ("actuator_c", c_uint8),        # 0x30 (heater)
        ("actuator_d", c_uint8),        # 0x40 (doors)

        # CONTROL (base address 4)
        ("power_sensors", c_uint8),     # 0xFB
        ("power_actuators", c_uint8),   # 0xFC
        ("reset_sensors", c_uint8),     # 0xFD
        ("reset_actuators", c_uint8),   # 0xFE
    ]

def log_callback(message):
    """Callback function for device logging."""
    print(f"[DEVICE] {message.decode('utf-8')}")

def main():
    """Main function."""
    print("Semi-Vibe-Device Python Test")
    print("---------------------------")

    # Load the DLL
    if sys.platform == 'win32':
        dll_path = os.path.abspath('../build/bin/semi_vibe_device.dll')
        try:
            device_lib = ctypes.CDLL(dll_path)
        except OSError:
            print(f"Failed to load DLL from {dll_path}")
            print("Make sure you have built the DLL using CMake and it's in the correct location.")
            return 1
    else:
        lib_path = os.path.abspath('../build/lib/libsemi_vibe_device.so')
        try:
            device_lib = ctypes.CDLL(lib_path)
        except OSError:
            print(f"Failed to load shared library from {lib_path}")
            print("Make sure you have built the shared library using CMake and it's in the correct location.")
            return 1

    # Define function prototypes
    device_lib.device_init.argtypes = [LogCallbackType]
    device_lib.device_init.restype = c_bool

    device_lib.device_start.argtypes = []
    device_lib.device_start.restype = c_bool

    device_lib.device_stop.argtypes = []
    device_lib.device_stop.restype = c_bool

    device_lib.device_get_memory.argtypes = [POINTER(DeviceMemory)]
    device_lib.device_get_memory.restype = c_bool

    device_lib.device_process_command.argtypes = [c_char_p, c_char_p]
    device_lib.device_process_command.restype = c_bool

    # Create callback function
    callback_func = LogCallbackType(log_callback)

    # Initialize device
    if not device_lib.device_init(callback_func):
        print("Failed to initialize device")
        return 1

    # Start device
    if not device_lib.device_start():
        print("Failed to start device")
        return 1

    # Process some test commands
    test_commands = [
        "100000",  # Read MAIN connected_device
        "102000",  # Read MAIN power_state
        "103000",  # Read MAIN error_state
        "210000",  # Read SENSOR_A ID
        "211000",  # Read SENSOR_A reading
        "220000",  # Read SENSOR_B ID
        "221000",  # Read SENSOR_B reading
        "310180",  # Write ACTUATOR_A value 0x80
        "310000",  # Read ACTUATOR_A value
        "320140",  # Write ACTUATOR_B value 0x40
        "320000",  # Read ACTUATOR_B value
        "330108",  # Write ACTUATOR_C value 0x08
        "330000",  # Read ACTUATOR_C value
        "340155",  # Write ACTUATOR_D value 0x55
        "340000",  # Read ACTUATOR_D value
        "4FB111",  # Write CONTROL power_sensors
        "4FB000",  # Read CONTROL power_sensors
        "4FC155",  # Write CONTROL power_actuators
        "4FC000",  # Read CONTROL power_actuators
    ]

    response = ctypes.create_string_buffer(7)
    for cmd in test_commands:
        print(f"Command: {cmd}")
        if device_lib.device_process_command(cmd.encode('utf-8'), response):
            print(f"Response: {response.value.decode('utf-8')}")
        else:
            print("Failed to process command")
        print()
        time.sleep(0.1)  # Small delay between commands

    # Get device memory
    memory = DeviceMemory()
    if device_lib.device_get_memory(ctypes.byref(memory)):
        print("Device Memory:")
        print(f"  Connected Device: 0x{memory.connected_device:02X}")
        print(f"  Power State: 0x{memory.power_state:02X}")
        print(f"  Error State: 0x{memory.error_state:02X}")
        print(f"  Sensor A ID: 0x{memory.sensor_a_id:02X}")
        print(f"  Sensor A Reading: 0x{memory.sensor_a_reading:02X}")
        print(f"  Sensor B ID: 0x{memory.sensor_b_id:02X}")
        print(f"  Sensor B Reading: 0x{memory.sensor_b_reading:02X}")
        print(f"  Actuator A: 0x{memory.actuator_a:02X}")
        print(f"  Actuator B: 0x{memory.actuator_b:02X}")
        print(f"  Actuator C: 0x{memory.actuator_c:02X}")
        print(f"  Actuator D: 0x{memory.actuator_d:02X}")
    else:
        print("Failed to get device memory")

    # Stop device
    if not device_lib.device_stop():
        print("Failed to stop device")
        return 1

    print("Test completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 