#!/usr/bin/env python3
"""
Basic test cases for device connectivity.
"""

import ctypes
import sys
import os

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from utils import get_driver_status, get_driver_actuators, set_led


## quick fix to disable print statements
def print(string):
    return


def test_connection(driver):
    """Test basic connection to the device."""
    print("\n=== Testing Connection ===")

    # Get device status
    status = get_driver_status(driver)
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["connected"]:
        print("❌ Device reports not connected")
        return False

    print("✅ Device is connected")
    return True


def test_direct_access(driver, device):
    """Test direct access to the device (bypassing sockets)."""
    print("\n=== Testing Direct Access ===")

    # Set a value directly on the device
    test_value = 123
    print(f"Setting LED directly to {test_value}...")

    # Set LED value using utility function
    if not set_led(device, test_value):
        print("❌ Failed to set LED value directly")
        return False

    # Read the value through the driver
    actuators = get_driver_actuators(driver)
    if not actuators:
        print("❌ Failed to get actuator data through driver")
        return False

    if actuators["led_value"] != test_value:
        print(
            f"❌ LED value mismatch: expected {test_value}, got {actuators['led_value']}"
        )
        return False

    print(f"✅ LED value successfully verified through driver: {test_value}")
    return True


def run_tests(driver, device=None):
    """Run all basic tests."""
    results = []

    # Run connection test
    results.append(("Connection", test_connection(driver)))

    # Run direct access test if device is provided
    if device:
        results.append(("Direct Access", test_direct_access(driver, device)))

    # Print summary
    print("\n=== Basic Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
