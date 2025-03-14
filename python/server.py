"""
Server script for the Semi-Vibe-Device simulator.
This script loads the DLL and starts the device server.
"""

import ctypes
import os
import sys
import time
from ctypes import c_bool, c_char_p, CFUNCTYPE

# Define the callback function type
LogCallbackType = CFUNCTYPE(None, c_char_p)


def log_callback(message):
    """Callback function for device logging."""
    print(f"[DEVICE] {message.decode('utf-8')}")


def main():
    """Main function."""
    print("Semi-Vibe-Device Server")
    print("----------------------")

    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the build directory
    build_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # Try Debug folder first (Visual Studio default)
    dll_path = os.path.join(build_dir, "build", "bin", "Debug", "semi_vibe_device.dll")
    if not os.path.exists(dll_path):
        # Fall back to regular bin folder
        dll_path = os.path.join(build_dir, "build", "bin", "semi_vibe_device.dll")

    if not os.path.exists(dll_path):
        print("Error: DLL not found. Make sure you have built the project.")
        return 1

    try:
        device_lib = ctypes.CDLL(dll_path)
    except OSError as e:
        print(f"Error: Failed to load DLL: {e}")
        print("Make sure you have built the DLL using CMake.")
        return 1

    # Define function prototypes
    device_lib.device_init.argtypes = [LogCallbackType]
    device_lib.device_init.restype = c_bool

    device_lib.device_start.argtypes = []
    device_lib.device_start.restype = c_bool

    device_lib.device_stop.argtypes = []
    device_lib.device_stop.restype = c_bool

    # Create callback function
    callback_func = LogCallbackType(log_callback)

    # Initialize device
    print("Initializing device...")
    if not device_lib.device_init(callback_func):
        print("Failed to initialize device")
        return 1

    # Start device - this now returns immediately as it starts a separate thread
    print("Starting device server...")
    if not device_lib.device_start():
        print("Failed to start device")
        return 1

    print("Device server is running. Press Ctrl+C to stop.")

    try:
        # Keep the script running until Ctrl+C is pressed
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping device server...")

        # Stop device
        if not device_lib.device_stop():
            print("Failed to stop device")
            return 1

        print("Device server stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
