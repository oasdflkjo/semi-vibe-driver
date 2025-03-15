#!/usr/bin/env python3
"""
Test cases for LED actuator functionality.
"""

import sys
import os

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import ActuatorData
import test_utils


def test_led_range(driver):
    """Test LED control across the full range (0-255)."""
    test_utils.print_func("\n=== Testing LED Range (Brute Force) ===")

    # Get initial LED value
    initial_value = driver.get_led()
    if initial_value is None:
        test_utils.print_func("[FAIL] Failed to get initial LED value")
        return False

    test_utils.print_func(f"Initial LED value: {initial_value}")

    # Test every value in the range 0-255
    all_passed = True
    failed_values = []

    test_utils.print_func("Testing all LED values from 0 to 255...")
    for test_value in range(256):
        # Set LED to test value
        test_utils.print_func(f"Setting LED value to {test_value}...")
        if not driver.set_led(test_value):
            test_utils.print_func(f"[FAIL] Failed to set LED value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value
        read_value = driver.get_led()
        if read_value is None:
            test_utils.print_func("[FAIL] Failed to get updated LED value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read back LED value: {read_value}")
        if read_value != test_value:
            test_utils.print_func(
                f"[FAIL] LED value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            test_utils.print_func(f"[PASSED] Tested LED values 0-{test_value}")

    # Reset LED to initial value
    test_utils.print_func(f"Resetting LED to initial value {initial_value}...")
    if not driver.set_led(initial_value):
        test_utils.print_func("[FAIL] Failed to reset LED value")
        return False

    # Verify the reset value
    final_value = driver.get_led()
    if final_value is None:
        test_utils.print_func("[FAIL] Failed to get LED value after reset")
        return False

    test_utils.print_func(f"Final LED value after reset: {final_value}")

    if all_passed:
        test_utils.print_func("[PASSED] LED range test passed for all 256 values")
    else:
        test_utils.print_func(
            f"[FAIL] LED range test failed for values: {failed_values}"
        )

    return all_passed


def test_led_get_api(driver):
    """Test the get_led API function."""
    test_utils.print_func("\n=== Testing LED Get API ===")

    # Test a smaller set of values to keep the test manageable
    test_values = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 255]
    all_passed = True
    failed_values = []

    # Get initial LED value
    initial_value = driver.get_led()
    if initial_value is None:
        test_utils.print_func("[FAIL] Failed to get initial LED value")
        return False

    test_utils.print_func(f"Initial LED value: {initial_value}")
    test_utils.print_func(f"Testing {len(test_values)} LED values...")

    for test_value in test_values:
        test_utils.print_func(f"\nSetting LED value to {test_value}...")

        # Set LED to test value
        if not driver.set_led(test_value):
            test_utils.print_func(f"[FAIL] Failed to set LED value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value using the get_led API
        read_value = driver.get_led()
        if read_value is None:
            test_utils.print_func("[FAIL] Failed to read LED value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read LED value: {read_value}")

        # Check if the read value matches what we set
        if read_value != test_value:
            test_utils.print_func(
                f"[FAIL] Value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"[PASSED] Verified LED value {test_value}")

    # Reset LED to initial value
    test_utils.print_func(f"\nResetting LED to initial value {initial_value}...")
    if not driver.set_led(initial_value):
        test_utils.print_func("[FAIL] Failed to reset LED value")
        return False

    # Verify reset value
    final_value = driver.get_led()
    if final_value is None:
        test_utils.print_func("[FAIL] Failed to get final LED value")
        return False

    test_utils.print_func(f"Final LED value after reset: {final_value}")

    if final_value != initial_value:
        test_utils.print_func(
            f"[FAIL] Failed to reset LED value: expected {initial_value}, got {final_value}"
        )
        all_passed = False

    if all_passed:
        test_utils.print_func(
            f"[PASSED] LED get API test passed for all {len(test_values)} values"
        )
    else:
        test_utils.print_func(
            f"[FAIL] LED get API test failed for values: {failed_values}"
        )

    return all_passed


def run_tests(driver, device=None):
    """Run all LED tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run LED range test
    results.append(("LED Range Control", test_led_range(driver)))

    # Run LED get API test
    results.append(("LED Get API", test_led_get_api(driver)))

    # Print summary
    test_utils.print_func("\n=== LED Tests Summary ===")
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
        test_utils.print_func("\n=== Running LED Tests ===")

        # Run both tests
        range_test_result = test_led_range(driver)
        api_test_result = test_led_get_api(driver)

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
