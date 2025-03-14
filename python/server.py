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
    message_str = f"[DEVICE] {message.decode('utf-8')}"
    print(message_str, flush=True)


def main():
    """Main function."""
    print("Semi-Vibe-Device Server", flush=True)
    print("----------------------", flush=True)

    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the build directory
    build_dir = os.path.abspath(os.path.join(script_dir, ".."))

    print(f"Looking for DLL in: {build_dir}", flush=True)

    # Try Debug folder first (Visual Studio default)
    dll_path = os.path.join(build_dir, "build", "bin", "Debug", "semi_vibe_device.dll")
    if not os.path.exists(dll_path):
        print(f"DLL not found at: {dll_path}", flush=True)
        # Fall back to regular bin folder
        dll_path = os.path.join(build_dir, "build", "bin", "semi_vibe_device.dll")
        print(f"Trying alternative path: {dll_path}", flush=True)

    if not os.path.exists(dll_path):
        print("Error: DLL not found. Make sure you have built the project.", flush=True)
        return 1

    print(f"Found DLL at: {dll_path}", flush=True)

    try:
        print("Loading DLL...", flush=True)
        device_lib = ctypes.CDLL(dll_path)
        print("DLL loaded successfully", flush=True)
    except OSError as e:
        print(f"Error: Failed to load DLL: {e}", flush=True)
        print("Make sure you have built the DLL using CMake.", flush=True)
        return 1

    # Define function prototypes
    print("Setting up function prototypes...", flush=True)
    device_lib.device_init.argtypes = [LogCallbackType]
    device_lib.device_init.restype = c_bool

    device_lib.device_start.argtypes = []
    device_lib.device_start.restype = c_bool

    device_lib.device_stop.argtypes = []
    device_lib.device_stop.restype = c_bool

    # Create callback function
    callback_func = LogCallbackType(log_callback)

    # Initialize device
    print("Initializing device...", flush=True)
    if not device_lib.device_init(callback_func):
        print("Failed to initialize device", flush=True)
        return 1
    print("Device initialized successfully", flush=True)

    # Start device - this now returns immediately as it starts a separate thread
    print("Starting device server...", flush=True)
    if not device_lib.device_start():
        print("Failed to start device", flush=True)
        return 1
    print("Device server started successfully", flush=True)

    print(
        "Device server is running on localhost:8989. Press Ctrl+C to stop.", flush=True
    )

    try:
        # Keep the script running until Ctrl+C is pressed
        counter = 0
        while True:
            if counter % 10 == 0:  # Log every 10 seconds
                print(f"Server running for {counter} seconds...", flush=True)
            time.sleep(1)
            counter += 1
    except KeyboardInterrupt:
        print("\nStopping device server...", flush=True)

        # Stop device
        if not device_lib.device_stop():
            print("Failed to stop device", flush=True)
            return 1

        print("Device server stopped.", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
