#!/usr/bin/env python3
"""
Test cases for doors actuator functionality.
"""

import sys
import os
import ctypes

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import ActuatorData
import test_utils


def get_doors_value_direct(driver):
    """Get doors value using direct command interface."""
    response_buffer = ctypes.create_string_buffer(7)
    if not driver.send_command("340000", response_buffer):
        test_utils.print_func("❌ Failed to send direct command to get doors value")
        return None

    # Parse the response (format: 3400XX where XX is the doors value in hex)
    response = response_buffer.value.decode("utf-8")
    if len(response) != 6 or not response.startswith("3400"):
        test_utils.print_func(f"❌ Invalid response format: {response}")
        return None

    try:
        doors_value = int(response[4:], 16)
        return doors_value
    except ValueError:
        test_utils.print_func(
            f"❌ Failed to parse doors value from response: {response}"
        )
        return None


def set_doors_value_direct(driver, value):
    """Set doors value using direct command interface."""
    command = f"3401{value:02X}"
    response_buffer = ctypes.create_string_buffer(7)
    if not driver.send_command(command, response_buffer):
        test_utils.print_func(
            f"❌ Failed to send direct command to set doors value to {value}"
        )
        return False

    # Verify the response matches the command
    response = response_buffer.value.decode("utf-8")
    if response != command:
        test_utils.print_func(f"❌ Response mismatch: sent {command}, got {response}")
        return False

    return True


def test_doors_range_direct(driver):
    """Test doors control with valid bit patterns using direct commands."""
    test_utils.print_func("\n=== Testing Doors Control (Direct Commands) ===")

    # Get initial doors value using direct command
    initial_value = get_doors_value_direct(driver)
    if initial_value is None:
        test_utils.print_func("❌ Failed to get initial doors value")
        return False

    test_utils.print_func(f"Initial doors value: {initial_value}")

    # The doors only use bits 0, 2, 4, and 6 (mask 0x55 or 01010101 in binary)
    # This means we should only test values where these bits are set
    valid_values = []
    for i in range(16):  # Generate all combinations of the 4 door bits
        # Convert i to a 4-bit binary representation
        # Then place each bit at positions 0, 2, 4, 6
        value = 0
        for bit_pos in range(4):
            if (i & (1 << bit_pos)) != 0:
                value |= 1 << (bit_pos * 2)
        valid_values.append(value)

    test_utils.print_func(f"Testing {len(valid_values)} valid door configurations...")

    # Test every valid value
    all_passed = True
    failed_values = []

    for test_value in valid_values:
        # Set doors to test value using direct command
        test_utils.print_func(
            f"Setting doors value to {test_value} (0x{test_value:02X})..."
        )
        if not set_doors_value_direct(driver, test_value):
            test_utils.print_func(
                f"❌ Failed to set doors value to {test_value} (0x{test_value:02X})"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value using direct command
        read_value = get_doors_value_direct(driver)
        if read_value is None:
            test_utils.print_func("❌ Failed to read doors value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read doors value: {read_value} (0x{read_value:02X})")

        if read_value != test_value:
            test_utils.print_func(
                f"❌ Doors value mismatch: expected {test_value} (0x{test_value:02X}), got {read_value} (0x{read_value:02X})"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(
            f"✅ Verified doors value: {test_value} (0x{test_value:02X})"
        )

    # Reset doors to initial value
    test_utils.print_func(f"Resetting doors to initial value {initial_value}...")
    if not set_doors_value_direct(driver, initial_value):
        test_utils.print_func("❌ Failed to reset doors value")
        return False

    # Verify reset value
    final_value = get_doors_value_direct(driver)
    if final_value is None:
        test_utils.print_func("❌ Failed to get final doors value")
        return False

    test_utils.print_func(f"Final doors value after reset: {final_value}")

    if final_value != initial_value:
        test_utils.print_func(
            f"❌ Failed to reset doors value: expected {initial_value}, got {final_value}"
        )
        all_passed = False

    if all_passed:
        test_utils.print_func(
            f"✅ Doors test passed for all {len(valid_values)} valid configurations"
        )
    else:
        test_utils.print_func(f"❌ Doors test failed for values: {failed_values}")

    return all_passed


def run_tests(driver):
    """Run all doors tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run doors test with valid configurations
    results.append(("Doors Control", test_doors_range_direct(driver)))

    # Print summary
    test_utils.print_func("\n=== Doors Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        test_utils.print_func(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed


def main():
    """Run the test in standalone mode."""
    return test_utils.run_standalone_test(test_doors_range_direct)


if __name__ == "__main__":
    sys.exit(main())
