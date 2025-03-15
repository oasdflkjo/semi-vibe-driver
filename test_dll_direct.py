#!/usr/bin/env python3
"""
Test script to directly call the DLL functions using ctypes.WinDLL.
"""

import os
import sys
import time
import ctypes
from ctypes import c_bool, c_char_p, CFUNCTYPE

# Define the callback function type
LOGCALLBACK = CFUNCTYPE(None, c_char_p)


# Define the callback function
def log_callback(message):
    print(f"DLL: {message.decode('utf-8')}")


def main():
    """Main function."""
    print("Testing DLL loading...")

    # Get the path to the DLL
    dll_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build",
        "bin",
        "Debug",
        "semi_vibe_device.dll",
    )

    print(f"DLL path: {dll_path}")
    print(f"DLL exists: {os.path.exists(dll_path)}")

    # Load the DLL
    try:
        dll = ctypes.WinDLL(dll_path)
        print("DLL loaded successfully")
    except Exception as e:
        print(f"Failed to load DLL: {str(e)}")
        return 1

    # Define function prototypes
    dll.device_init.argtypes = [LOGCALLBACK]
    dll.device_init.restype = c_bool

    dll.device_start.argtypes = []
    dll.device_start.restype = c_bool

    dll.device_stop.argtypes = []
    dll.device_stop.restype = c_bool

    print("Function prototypes defined")

    # Initialize the device
    print("Initializing device...")
    callback = LOGCALLBACK(log_callback)
    try:
        init_result = dll.device_init(callback)
        print(f"Initialization result: {init_result}")
    except Exception as e:
        print(f"Failed to initialize device: {str(e)}")
        return 1

    if init_result:
        # Start the device
        print("Starting device...")
        try:
            start_result = dll.device_start()
            print(f"Start result: {start_result}")
        except Exception as e:
            print(f"Failed to start device: {str(e)}")
            return 1

        if start_result:
            print("Device started successfully")

            # Wait for a moment
            print("Waiting for 5 seconds...")
            time.sleep(5)

            # Stop the device
            print("Stopping device...")
            try:
                stop_result = dll.device_stop()
                print(f"Stop result: {stop_result}")
            except Exception as e:
                print(f"Failed to stop device: {str(e)}")
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
