#!/usr/bin/env python3
"""
Test cases for fan actuator functionality.
"""

import sys
import os
import ctypes

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import ActuatorData
from device import DeviceMemory
import test_utils


def get_fan_value_direct(driver):
    """Get fan value using direct command interface for cleaner output."""
    response_buffer = ctypes.create_string_buffer(7)
    if not driver.send_command("320000", response_buffer):
        test_utils.print_func("❌ Failed to send direct command to get fan value")
        return None

    # Parse the response (format: 3200XX where XX is the fan value in hex)
    response = response_buffer.value.decode("utf-8")
    if len(response) != 6 or not response.startswith("3200"):
        test_utils.print_func(f"❌ Invalid response format: {response}")
        return None

    try:
        fan_value = int(response[4:], 16)
        return fan_value
    except ValueError:
        test_utils.print_func(f"❌ Failed to parse fan value from response: {response}")
        return None


def set_fan_value_direct(driver, value):
    """Set fan value using direct command interface for cleaner output."""
    command = f"3201{value:02X}"
    response_buffer = ctypes.create_string_buffer(7)
    if not driver.send_command(command, response_buffer):
        test_utils.print_func(
            f"❌ Failed to send direct command to set fan value to {value}"
        )
        return False

    # Verify the response matches the command
    response = response_buffer.value.decode("utf-8")
    if response != command:
        test_utils.print_func(f"❌ Response mismatch: sent {command}, got {response}")
        return False

    return True


def test_fan_range_direct(driver):
    """Test fan control across the full range (0-255) using direct commands."""
    test_utils.print_func("\n=== Testing Fan Range (Direct Commands) ===")

    # Get initial fan value
    initial_value = get_fan_value_direct(driver)
    if initial_value is None:
        test_utils.print_func("❌ Failed to get initial fan value")
        return False

    test_utils.print_func(f"Initial fan value: {initial_value}")

    # Test the full range from 0 to 255
    test_utils.print_func("Testing all fan values from 0 to 255...")

    # Test every value in the range
    all_passed = True
    failed_values = []

    for test_value in range(256):
        # Print value before sending
        test_utils.print_func(f"Setting fan value to {test_value}...")

        # Set fan to test value using direct command
        if not set_fan_value_direct(driver, test_value):
            all_passed = False
            failed_values.append(test_value)
            continue

        # Read back the value using direct command
        read_value = get_fan_value_direct(driver)
        if read_value is None:
            test_utils.print_func("❌ Failed to read back fan value")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print value after receiving
        test_utils.print_func(f"Read back fan value: {read_value}")

        if read_value != test_value:
            test_utils.print_func(
                f"❌ Fan value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            test_utils.print_func(f"✅ Tested fan values 0-{test_value}")

    # Reset fan to initial value
    test_utils.print_func(f"Resetting fan to initial value {initial_value}...")
    if not set_fan_value_direct(driver, initial_value):
        test_utils.print_func("❌ Failed to reset fan value")
        return False

    # Verify the reset value
    final_value = get_fan_value_direct(driver)
    if final_value is None:
        test_utils.print_func("❌ Failed to get final fan value")
        return False

    test_utils.print_func(f"Final fan value after reset: {final_value}")

    if all_passed:
        test_utils.print_func("✅ Fan range test passed for all 256 values")
    else:
        test_utils.print_func(f"❌ Fan range test failed for values: {failed_values}")

    return all_passed


def test_fan_range(driver):
    """Test fan control across the full range (0-255)."""
    test_utils.print_func("\n=== Testing Fan Range (Full) ===")

    # Get initial fan value
    actuator_data = ActuatorData()
    if not driver.get_actuators(actuator_data):
        test_utils.print_func("❌ Failed to get actuator data")
        return False

    initial_value = actuator_data.fan_value
    test_utils.print_func(f"Initial fan value: {initial_value}")

    # Test the full range from 0 to 255
    test_utils.print_func("Testing all fan values from 0 to 255...")

    # Test every value in the range
    all_passed = True
    failed_values = []

    for test_value in range(256):
        # Print value before sending
        test_utils.print_func(f"Setting fan value to {test_value}...")

        # Set fan to test value
        if not driver.set_fan(test_value):
            test_utils.print_func(f"❌ Failed to set fan value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value
        actuator_data = ActuatorData()
        if not driver.get_actuators(actuator_data):
            test_utils.print_func("❌ Failed to get updated actuator data")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print value after receiving
        test_utils.print_func(f"Read back fan value: {actuator_data.fan_value}")

        if actuator_data.fan_value != test_value:
            test_utils.print_func(
                f"❌ Fan value mismatch: expected {test_value}, got {actuator_data.fan_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            test_utils.print_func(f"✅ Tested fan values 0-{test_value}")

    # Reset fan to initial value
    test_utils.print_func(f"Resetting fan to initial value {initial_value}...")
    if not driver.set_fan(initial_value):
        test_utils.print_func("❌ Failed to reset fan value")
        return False

    # Verify the reset value
    actuator_data = ActuatorData()
    if not driver.get_actuators(actuator_data):
        test_utils.print_func("❌ Failed to get actuator data after reset")
        return False

    test_utils.print_func(f"Final fan value after reset: {actuator_data.fan_value}")

    if all_passed:
        test_utils.print_func("✅ Fan range test passed for all 256 values")
    else:
        test_utils.print_func(f"❌ Fan range test failed for values: {failed_values}")

    return all_passed


def run_tests(driver, device=None):
    """Run all fan tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    # Run fan range test using direct commands for cleaner output
    result = test_fan_range_direct(driver)

    # Print summary
    test_utils.print_func("\n=== Fan Tests Summary ===")
    status = "✅ PASSED" if result else "❌ FAILED"
    test_utils.print_func(f"Fan Range Control: {status}")

    return result


def main():
    """Run the test in standalone mode."""
    device, driver = test_utils.setup_test_environment()
    if not device or not driver:
        return 1

    try:
        # Enable prints for standalone test
        global print_func
        test_utils.print_func = print  # Use the real print function

        # Run the test with direct commands for cleaner output
        test_utils.print_func("\n=== Running Fan Test ===")
        success = test_fan_range_direct(driver)

        # Print overall result
        if success:
            test_utils.print_func("\n✅ Test passed!")
        else:
            test_utils.print_func("\n❌ Test failed!")

        return 0 if success else 1
    finally:
        test_utils.teardown_test_environment(device, driver)


if __name__ == "__main__":
    sys.exit(main())
