#!/usr/bin/env python3
"""
Utility functions for test cases.
This module provides common functionality for loading, initializing, and cleaning up DLLs.
"""

import ctypes
import sys
import os
import time
import socket
import traceback

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import DriverDLL
from device import DeviceDLL


# Use real print for standalone execution, disabled print for test runner
print_func = print
# Flag to control whether callbacks should print messages
enable_callback_prints = True


def print_disabled(string):
    """Disabled print function for when running as part of the test suite."""
    return


def set_print_disabled():
    """Set the print function to disabled."""
    global print_func
    print_func = print_disabled


def disable_callback_prints():
    """Disable printing from callbacks."""
    global enable_callback_prints
    enable_callback_prints = False


def enable_callback_prints():
    """Enable printing from callbacks."""
    global enable_callback_prints
    enable_callback_prints = True


def device_log_callback(message):
    """Callback function for device logging."""
    if enable_callback_prints:
        print_func(f"Device: {message.decode('utf-8')}")


def driver_log_callback(message):
    """Callback function for driver logging."""
    if enable_callback_prints:
        print_func(f"Driver: {message.decode('utf-8')}")


def is_server_ready(host="localhost", port=8989, max_attempts=10):
    """Check if the server is ready to accept connections."""
    print_func(f"Checking if server is ready on {host}:{port}...")

    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                print_func(f"Server is ready after {attempt + 1} attempts!")
                return True
        except (ConnectionRefusedError, socket.timeout):
            print_func(
                f"Server not ready yet (attempt {attempt + 1}/{max_attempts})..."
            )
            time.sleep(1)

    print_func(f"Server did not become ready after {max_attempts} attempts")
    return False


def load_device_dll(device_dll_path=None):
    """Load the device DLL.

    Args:
        device_dll_path: Optional path to the DLL file

    Returns:
        DeviceDLL instance or None if failed
    """
    if device_dll_path is None:
        # Get the default path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        device_dll_path = os.path.join(
            base_dir, "build", "bin", "Debug", "semi_vibe_device.dll"
        )

    print_func(f"Device DLL path: {device_dll_path}")

    # Check if DLL exists
    if not os.path.exists(device_dll_path):
        print_func(f"❌ Device DLL not found at {device_dll_path}")
        return None

    # Load the device DLL
    try:
        device = DeviceDLL(device_dll_path)
        print_func("✅ Device DLL loaded successfully")
        return device
    except Exception as e:
        print_func(f"❌ Failed to load device DLL: {str(e)}")
        traceback.print_exc()
        return None


def initialize_device(device):
    """Initialize the device.

    Args:
        device: DeviceDLL instance

    Returns:
        bool: True if successful
    """
    try:
        if not device.init(device_log_callback):
            print_func("❌ Failed to initialize device")
            return False
        print_func("✅ Device initialized successfully")
        return True
    except Exception as e:
        print_func(f"❌ Error during device initialization: {str(e)}")
        traceback.print_exc()
        return False


def start_device(device):
    """Start the device server.

    Args:
        device: DeviceDLL instance

    Returns:
        bool: True if successful
    """
    try:
        if not device.start():
            print_func("❌ Failed to start device server")
            return False
        print_func("✅ Device server started successfully")
        return True
    except Exception as e:
        print_func(f"❌ Error during device server start: {str(e)}")
        traceback.print_exc()
        return False


def stop_device(device):
    """Stop the device server.

    Args:
        device: DeviceDLL instance

    Returns:
        bool: True if successful
    """
    try:
        if not device.stop():
            print_func("❌ Failed to stop device server")
            return False
        print_func("✅ Device server stopped")
        return True
    except Exception as e:
        print_func(f"❌ Error during device server stop: {str(e)}")
        traceback.print_exc()
        return False


def load_driver_dll(driver_dll_path=None):
    """Load the driver DLL.

    Args:
        driver_dll_path: Optional path to the DLL file

    Returns:
        DriverDLL instance or None if failed
    """
    if driver_dll_path is None:
        # Get the default path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_dll_path = os.path.join(
            base_dir, "build", "bin", "Debug", "semi_vibe_driver.dll"
        )

    print_func(f"Driver DLL path: {driver_dll_path}")

    # Check if DLL exists
    if not os.path.exists(driver_dll_path):
        print_func(f"❌ Driver DLL not found at {driver_dll_path}")
        return None

    # Load the driver DLL
    try:
        driver = DriverDLL(driver_dll_path)
        print_func("✅ Driver DLL loaded successfully")
        return driver
    except Exception as e:
        print_func(f"❌ Failed to load driver DLL: {str(e)}")
        traceback.print_exc()
        return None


def initialize_driver(driver):
    """Initialize the driver.

    Args:
        driver: DriverDLL instance

    Returns:
        bool: True if successful
    """
    try:
        if not driver.init(driver_log_callback):
            print_func("❌ Failed to initialize driver")
            return False
        print_func("✅ Driver initialized successfully")
        return True
    except Exception as e:
        print_func(f"❌ Error during driver initialization: {str(e)}")
        traceback.print_exc()
        return False


def connect_driver(driver, host="localhost", port=8989):
    """Connect the driver to the device.

    Args:
        driver: DriverDLL instance
        host: Hostname or IP address
        port: Port number

    Returns:
        bool: True if successful
    """
    try:
        if not driver.connect(host, port):
            print_func(f"❌ Failed to connect to device at {host}:{port}")
            return False
        print_func("✅ Connected to device successfully")
        return True
    except Exception as e:
        print_func(f"❌ Error during driver connection: {str(e)}")
        traceback.print_exc()
        return False


def disconnect_driver(driver):
    """Disconnect the driver from the device.

    Args:
        driver: DriverDLL instance

    Returns:
        bool: True if successful
    """
    try:
        if not driver.disconnect():
            print_func("❌ Failed to disconnect driver")
            return False
        print_func("✅ Driver disconnected")
        return True
    except Exception as e:
        print_func(f"❌ Error during driver disconnect: {str(e)}")
        traceback.print_exc()
        return False


def setup_test_environment():
    """Set up the test environment by loading and initializing the DLLs.

    Returns:
        tuple: (device, driver) or (None, None) if failed
    """
    # Load and initialize device
    device = load_device_dll()
    if not device:
        return None, None

    if not initialize_device(device):
        return None, None

    if not start_device(device):
        return None, None

    # Wait for server to start
    if not is_server_ready():
        stop_device(device)
        return None, None

    # Load and initialize driver
    driver = load_driver_dll()
    if not driver:
        stop_device(device)
        return None, None

    if not initialize_driver(driver):
        stop_device(device)
        return None, None

    if not connect_driver(driver):
        stop_device(device)
        return None, None

    return device, driver


def teardown_test_environment(device, driver):
    """Clean up the test environment.

    Args:
        device: DeviceDLL instance
        driver: DriverDLL instance
    """
    print_func("\nCleaning up...")

    if driver:
        disconnect_driver(driver)

    if device:
        stop_device(device)


def run_standalone_test(test_func):
    """Run a test function in standalone mode.

    Args:
        test_func: Function that takes a driver parameter and returns a boolean

    Returns:
        int: 0 if successful, 1 if failed
    """
    # Enable callback prints for standalone tests
    enable_callback_prints()

    device, driver = setup_test_environment()
    if not device or not driver:
        return 1

    try:
        # Run the test
        print_func("\n=== Running Test ===")
        success = test_func(driver)

        # Print result
        if success:
            print_func("\n✅ Test passed!")
        else:
            print_func("\n❌ Test failed!")

        return 0 if success else 1
    finally:
        teardown_test_environment(device, driver)
