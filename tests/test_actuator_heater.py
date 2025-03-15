#!/usr/bin/env python3
"""
Test cases for heater actuator functionality.
"""

import sys
import os

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import ActuatorData
import test_utils


def test_heater_range(driver):
    """Test heater control across the valid range (0-15)."""
    test_utils.print_func("\n=== Testing Heater Range (Brute Force) ===")

    # Get initial heater value
    initial_value = driver.get_heater()
    if initial_value is None:
        test_utils.print_func("[FAIL] Failed to get initial heater value")
        return False

    test_utils.print_func(f"Initial heater value: {initial_value}")

    # Test every value in the valid range 0-15 (only lower 4 bits are used)
    all_passed = True
    failed_values = []

    test_utils.print_func("Testing all heater values from 0 to 15...")
    for test_value in range(16):
        # Set heater to test value
        test_utils.print_func(f"Setting heater value to {test_value}...")
        if not driver.set_heater(test_value):
            test_utils.print_func(f"[FAIL] Failed to set heater value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value
        read_value = driver.get_heater()
        if read_value is None:
            test_utils.print_func("[FAIL] Failed to get updated heater value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read back heater value: {read_value}")
        if read_value != test_value:
            test_utils.print_func(
                f"[FAIL] Heater value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 5 values
        if test_value % 5 == 0 or test_value == 15:
            test_utils.print_func(f"[PASSED] Tested heater values 0-{test_value}")

    # Reset heater to initial value
    test_utils.print_func(f"Resetting heater to initial value {initial_value}...")
    if not driver.set_heater(initial_value):
        test_utils.print_func("[FAIL] Failed to reset heater value")
        return False

    # Verify the reset value
    final_value = driver.get_heater()
    if final_value is None:
        test_utils.print_func("[FAIL] Failed to get heater value after reset")
        return False

    test_utils.print_func(f"Final heater value after reset: {final_value}")

    if all_passed:
        test_utils.print_func("[PASSED] Heater range test passed for all 16 values")
    else:
        test_utils.print_func(
            f"[FAIL] Heater range test failed for values: {failed_values}"
        )

    return all_passed


def test_heater_get_api(driver):
    """Test the get_heater API function."""
    test_utils.print_func("\n=== Testing Heater Get API ===")

    # Test all values in the valid range 0-15
    test_values = list(range(16))
    all_passed = True
    failed_values = []

    # Get initial heater value
    initial_value = driver.get_heater()
    if initial_value is None:
        test_utils.print_func("[FAIL] Failed to get initial heater value")
        return False

    test_utils.print_func(f"Initial heater value: {initial_value}")
    test_utils.print_func(f"Testing {len(test_values)} heater values...")

    for test_value in test_values:
        test_utils.print_func(f"\nSetting heater value to {test_value}...")

        # Set heater to test value
        if not driver.set_heater(test_value):
            test_utils.print_func(f"[FAIL] Failed to set heater value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value using the get_heater API
        read_value = driver.get_heater()
        if read_value is None:
            test_utils.print_func("[FAIL] Failed to read heater value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read heater value: {read_value}")

        # Check if the read value matches what we set
        if read_value != test_value:
            test_utils.print_func(
                f"[FAIL] Value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"[PASSED] Verified heater value {test_value}")

    # Reset heater to initial value
    test_utils.print_func(f"\nResetting heater to initial value {initial_value}...")
    if not driver.set_heater(initial_value):
        test_utils.print_func("[FAIL] Failed to reset heater value")
        return False

    # Verify reset value
    final_value = driver.get_heater()
    if final_value is None:
        test_utils.print_func("[FAIL] Failed to get final heater value")
        return False

    test_utils.print_func(f"Final heater value after reset: {final_value}")

    if final_value != initial_value:
        test_utils.print_func(
            f"[FAIL] Failed to reset heater value: expected {initial_value}, got {final_value}"
        )
        all_passed = False

    if all_passed:
        test_utils.print_func(
            f"[PASSED] Heater get API test passed for all {len(test_values)} values"
        )
    else:
        test_utils.print_func(
            f"[FAIL] Heater get API test failed for values: {failed_values}"
        )

    return all_passed


def run_tests(driver, device=None):
    """Run all heater tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run heater range test
    results.append(("Heater Range Control", test_heater_range(driver)))

    # Run heater get API test
    results.append(("Heater Get API", test_heater_get_api(driver)))

    # Print summary
    test_utils.print_func("\n=== Heater Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "[PASSED] PASSED" if result else "[FAIL] FAILED"
        test_utils.print_func(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed


def main():
    """Run the test in standalone mode."""
    device, driver = test_utils.setup_test_environment()
    if not device or not driver:
        return 1

    try:
        # Enable prints for standalone test
        test_utils.print_func = print  # Use the real print function

        # Run the tests
        test_utils.print_func("\n=== Running Heater Tests ===")

        # Run both tests
        range_test_result = test_heater_range(driver)
        api_test_result = test_heater_get_api(driver)

        success = range_test_result and api_test_result

        # Print overall result
        if success:
            test_utils.print_func("\n[PASSED] All tests passed!")
        else:
            test_utils.print_func("\n[FAIL] Some tests failed!")

        return 0 if success else 1
    finally:
        test_utils.teardown_test_environment(device, driver)


if __name__ == "__main__":
    sys.exit(main())
