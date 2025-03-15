#!/usr/bin/env python3
"""
Template for standalone test cases.
Copy this file and modify it for your specific test needs.
"""

import sys
import os

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import DeviceStatus, SensorData, ActuatorData
from device import DeviceMemory
import test_utils


def test_example(driver):
    """Example test function.

    Args:
        driver: DriverDLL instance

    Returns:
        bool: True if test passed, False otherwise
    """
    test_utils.print_func("\n=== Example Test ===")

    # Your test code here
    # For example:
    status = DeviceStatus()
    if not driver.get_status(status):
        test_utils.print_func("[FAIL] Failed to get device status")
        return False

    test_utils.print_func(f"Device connected: {status.connected}")
    test_utils.print_func(f"Sensors powered: {status.sensors_powered}")
    test_utils.print_func(f"Actuators powered: {status.actuators_powered}")

    # Return True if test passed, False otherwise
    return True


def run_tests(driver):
    """Run all tests in this module.

    Args:
        driver: DriverDLL instance

    Returns:
        bool: True if all tests passed, False otherwise
    """
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Add your tests here
    results.append(("Example Test", test_example(driver)))

    # Add more tests as needed
    # results.append(("Another Test", test_another(driver)))

    # Print summary
    test_utils.print_func("\n=== Test Summary ===")
    all_passed = True
    for name, result in results:
        status = "[PASSED] PASSED" if result else "[FAIL] FAILED"
        test_utils.print_func(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed


def main():
    """Run the test in standalone mode."""
    return test_utils.run_standalone_test(test_example)


if __name__ == "__main__":
    sys.exit(main())
