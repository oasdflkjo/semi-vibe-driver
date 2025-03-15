#!/usr/bin/env python3
"""
Run script for Semi-Vibe-Device simulator and driver.
Entry point for the unified testing system.
"""

import os
import sys
import time
import socket
import threading
import queue
import ctypes
import traceback

# Add the tests directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"))
import test_utils


def is_server_ready(host="localhost", port=8989, max_attempts=10):
    """Check if the server is ready to accept connections."""
    print(f"Checking if server is ready on {host}:{port}...")

    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                print(f"Server is ready after {attempt + 1} attempts!")
                return True
        except (ConnectionRefusedError, socket.timeout):
            print(f"Server not ready yet (attempt {attempt + 1}/{max_attempts})...")
            time.sleep(1)

    print(f"Server did not become ready after {max_attempts} attempts")
    return False


def check_dll_exists(dll_path):
    """Check if a DLL file exists and print an error if it doesn't."""
    if not os.path.exists(dll_path):
        print(f"ERROR: DLL file does not exist at {dll_path}")
        return False
    return True


def load_device_dll(device_dll_path):
    """Load the device DLL with error handling."""
    print(f"Attempting to load device DLL from: {device_dll_path}")

    if not check_dll_exists(device_dll_path):
        return None

    try:
        # Import the device module
        sys.path.append(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "python")
        )
        from device import DeviceDLL

        try:
            device = DeviceDLL(device_dll_path)
            print("Device DLL loaded successfully")
            return device
        except Exception as e:
            print(f"ERROR: Failed to load device DLL: {str(e)}")
            traceback.print_exc()
            return None
    except Exception as e:
        print(f"ERROR: Failed to import device module: {str(e)}")
        traceback.print_exc()
        return None


def load_driver_dll(driver_dll_path):
    """Load the driver DLL with error handling."""
    print(f"Attempting to load driver DLL from: {driver_dll_path}")

    if not check_dll_exists(driver_dll_path):
        return None

    try:
        # Import the driver module
        sys.path.append(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "python")
        )
        from driver import DriverDLL

        try:
            driver = DriverDLL(driver_dll_path)
            print("Driver DLL loaded successfully")
            return driver
        except Exception as e:
            print(f"ERROR: Failed to load driver DLL: {str(e)}")
            traceback.print_exc()
            return None
    except Exception as e:
        print(f"ERROR: Failed to import driver module: {str(e)}")
        traceback.print_exc()
        return None


def initialize_device(device):
    """Initialize the device with error handling."""
    print("Initializing device...")
    try:
        result = device.init(test_utils.device_log_callback)
        print(f"Device initialization result: {result}")
        return result
    except Exception as e:
        print(f"ERROR during device initialization: {str(e)}")
        traceback.print_exc()
        return False


def start_device(device):
    """Start the device with error handling."""
    print("Starting device server...")
    try:
        result = device.start()
        print(f"Device start result: {result}")
        return result
    except Exception as e:
        print(f"ERROR during device start: {str(e)}")
        traceback.print_exc()
        return False


def stop_device(device):
    """Stop the device with error handling."""
    print("Stopping device server...")
    try:
        result = device.stop()
        print(f"Device stop result: {result}")
        return result
    except Exception as e:
        print(f"ERROR during device stop: {str(e)}")
        traceback.print_exc()
        return False


def initialize_driver(driver):
    """Initialize the driver with error handling."""
    print("Initializing driver...")
    try:
        result = driver.init(test_utils.driver_log_callback)
        print(f"Driver initialization result: {result}")
        return result
    except Exception as e:
        print(f"ERROR during driver initialization: {str(e)}")
        traceback.print_exc()
        return False


def connect_driver(driver, host, port):
    """Connect the driver to the device with error handling."""
    print(f"Connecting driver to {host}:{port}...")
    try:
        result = driver.connect(host, port)
        print(f"Driver connect result: {result}")
        return result
    except Exception as e:
        print(f"ERROR during driver connect: {str(e)}")
        traceback.print_exc()
        return False


def disconnect_driver(driver):
    """Disconnect the driver from the device with error handling."""
    print("Disconnecting driver...")
    try:
        result = driver.disconnect()
        print(f"Driver disconnect result: {result}")
        return result
    except Exception as e:
        print(f"ERROR during driver disconnect: {str(e)}")
        traceback.print_exc()
        return False


def run_tests():
    """Run the unified testing system."""
    print("\n======== SEMI-VIBE-DEVICE TESTING SYSTEM ========")

    # Print system information
    print("System Information:")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    print(f"Current directory: {os.getcwd()}")
    print(
        f"DLL directory: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', 'bin', 'Debug')}"
    )

    # Get the path to the DLLs
    device_dll_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build",
        "bin",
        "Debug",
        "semi_vibe_device.dll",
    )
    driver_dll_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "build",
        "bin",
        "Debug",
        "semi_vibe_driver.dll",
    )

    print(f"Device DLL exists: {os.path.exists(device_dll_path)}")
    print(f"Driver DLL exists: {os.path.exists(driver_dll_path)}")

    # Enable callback prints for setup
    test_utils.enable_callback_prints()

    # Load the device DLL
    device = load_device_dll(device_dll_path)
    if not device:
        print("[FAIL] Failed to load device DLL")
        return 1

    # Initialize the device
    if not initialize_device(device):
        print("[FAIL] Failed to initialize device")
        return 1

    # Start the device server
    if not start_device(device):
        print("[FAIL] Failed to start device server")
        return 1

    # Wait for the server to be ready
    if not is_server_ready():
        print("[FAIL] Server did not become ready")
        stop_device(device)
        return 1

    # Load the driver DLL
    driver = load_driver_dll(driver_dll_path)
    if not driver:
        print("[FAIL] Failed to load driver DLL")
        stop_device(device)
        return 1

    # Initialize the driver
    if not initialize_driver(driver):
        print("[FAIL] Failed to initialize driver")
        stop_device(device)
        return 1

    # Connect the driver to the device
    if not connect_driver(driver, "localhost", 8989):
        print("[FAIL] Failed to connect to device")
        stop_device(device)
        return 1

    # Import the utils module
    try:
        from python.utils import get_driver_status

        # Verify connection using utility function
        print("Verifying connection...")
        status = get_driver_status(driver)
        if not status or not status["connected"]:
            print("[FAIL] Connection verification failed")
            disconnect_driver(driver)
            stop_device(device)
            return 1

        print("[OK] Connected to device")
    except Exception as e:
        print(f"ERROR during connection verification: {str(e)}")
        traceback.print_exc()
        disconnect_driver(driver)
        stop_device(device)
        return 1

    try:
        # Import the test runner
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from tests.test_runner import run_all_tests

        # Run all tests
        test_result = run_all_tests(driver, device)

        return 0 if test_result else 1
    except Exception as e:
        print(f"ERROR during test execution: {str(e)}")
        traceback.print_exc()
        return 1
    finally:
        # Clean up
        print("\nDisconnecting and shutting down...")
        disconnect_driver(driver)
        stop_device(device)


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] != "test":
        print(f"Unknown command: {sys.argv[1]}")
        print("Usage: python run.py [test]")
        return 1

    return run_tests()


if __name__ == "__main__":
    sys.exit(main())
