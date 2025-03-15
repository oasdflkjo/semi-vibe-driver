#!/usr/bin/env python3
"""
Test script to check if we can load the DLLs directly.
"""

import os
import sys
import ctypes
from ctypes import windll, cdll, WinDLL, CDLL


def test_load_dll(dll_path, load_methods):
    """Test loading a DLL with different methods."""
    print(f"\nTesting DLL: {dll_path}")
    print(f"File exists: {os.path.exists(dll_path)}")

    for method_name, method in load_methods.items():
        print(f"\nTrying to load with {method_name}...")
        try:
            dll = method(dll_path)
            print(f"✅ Successfully loaded with {method_name}")
            return dll
        except Exception as e:
            print(f"❌ Failed to load with {method_name}: {str(e)}")
            if hasattr(ctypes, "FormatError"):
                print(f"Windows Error: {ctypes.FormatError()}")

    return None


def main():
    """Main function."""
    # Get the path to the DLLs
    base_dir = os.path.dirname(os.path.abspath(__file__))
    device_dll_path = os.path.join(
        base_dir, "build", "bin", "Debug", "semi_vibe_device.dll"
    )
    driver_dll_path = os.path.join(
        base_dir, "build", "bin", "Debug", "semi_vibe_driver.dll"
    )

    # Print system information
    print("System Information:")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    print(f"Current directory: {os.getcwd()}")

    # Define different methods to load DLLs
    load_methods = {
        "ctypes.CDLL": lambda path: ctypes.CDLL(path),
        "ctypes.WinDLL": lambda path: ctypes.WinDLL(path),
        "ctypes.cdll.LoadLibrary": lambda path: ctypes.cdll.LoadLibrary(path),
        "ctypes.windll.LoadLibrary": lambda path: ctypes.windll.LoadLibrary(path),
    }

    # Try to load the device DLL
    device_dll = test_load_dll(device_dll_path, load_methods)

    # Try to load the driver DLL
    driver_dll = test_load_dll(driver_dll_path, load_methods)

    # Summary
    print("\nSummary:")
    print(f"Device DLL: {'✅ Loaded' if device_dll else '❌ Failed to load'}")
    print(f"Driver DLL: {'✅ Loaded' if driver_dll else '❌ Failed to load'}")

    return 0 if device_dll and driver_dll else 1


if __name__ == "__main__":
    sys.exit(main())
