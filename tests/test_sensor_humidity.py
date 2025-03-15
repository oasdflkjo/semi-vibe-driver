#!/usr/bin/env python3
"""
Test cases for humidity sensor functionality.
"""

import sys
import os
import ctypes
import time

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import SensorData
from device import DeviceMemory
import test_utils


def get_humidity_value_direct(driver):
    """Get humidity value using direct command interface."""
    response_buffer = ctypes.create_string_buffer(7)
    if not driver.send_command("221000", response_buffer):
        test_utils.print_func("❌ Failed to send direct command to get humidity value")
        return None

    # Parse the response (format: 2210XX where XX is the humidity value in hex)
    response = response_buffer.value.decode("utf-8")
    if len(response) != 6 or not response.startswith("2210"):
        test_utils.print_func(f"❌ Invalid response format: {response}")
        return None

    try:
        humidity_value = int(response[4:], 16)
        return humidity_value
    except ValueError:
        test_utils.print_func(
            f"❌ Failed to parse humidity value from response: {response}"
        )
        return None


def test_humidity_sensor_direct(driver, device):
    """Test humidity sensor using direct memory access and direct commands."""
    test_utils.print_func("\n=== Testing Humidity Sensor (Direct Commands) ===")

    # Get initial humidity value using direct command
    initial_value = get_humidity_value_direct(driver)
    if initial_value is None:
        test_utils.print_func("❌ Failed to get initial humidity value")
        return False

    test_utils.print_func(f"Initial humidity value: {initial_value}")

    # Test a smaller set of values to keep the test manageable
    test_values = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 255]
    all_passed = True
    failed_values = []

    test_utils.print_func(f"Testing {len(test_values)} humidity values...")
    for test_value in test_values:
        test_utils.print_func(f"\nSetting humidity value to {test_value}...")

        # Get current device memory
        device_memory = DeviceMemory()
        if not device.get_memory(device_memory):
            test_utils.print_func("❌ Failed to get device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Update memory with new humidity value
        device_memory.sensor_b_reading = test_value
        if not device.set_memory(device_memory):
            test_utils.print_func("❌ Failed to set device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Small delay to ensure memory update is processed
        time.sleep(0.1)

        # Verify the value using direct command
        read_value = get_humidity_value_direct(driver)
        if read_value is None:
            test_utils.print_func("❌ Failed to read humidity value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read humidity value: {read_value}")

        # Check if the read value matches what we set
        if read_value != test_value:
            test_utils.print_func(
                f"❌ Value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"✅ Verified humidity value {test_value}")

    # Reset humidity to initial value
    test_utils.print_func(f"\nResetting humidity to initial value {initial_value}...")
    device_memory = DeviceMemory()
    if device.get_memory(device_memory):
        device_memory.sensor_b_reading = initial_value
        device.set_memory(device_memory)

    # Small delay to ensure memory update is processed
    time.sleep(0.1)

    # Verify reset value
    final_value = get_humidity_value_direct(driver)
    if final_value is None:
        test_utils.print_func("❌ Failed to get final humidity value")
        return False

    test_utils.print_func(f"Final humidity value after reset: {final_value}")

    if final_value != initial_value:
        test_utils.print_func(
            f"❌ Failed to reset humidity value: expected {initial_value}, got {final_value}"
        )
        all_passed = False

    if all_passed:
        test_utils.print_func(
            f"✅ Humidity sensor test passed for all {len(test_values)} values"
        )
    else:
        test_utils.print_func(
            f"❌ Humidity sensor test failed for values: {failed_values}"
        )

    return all_passed


def test_humidity_get_api(driver, device):
    """Test the get_humidity API function."""
    test_utils.print_func("\n=== Testing Humidity Get API ===")

    # Test a smaller set of values to keep the test manageable
    test_values = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 255]
    all_passed = True
    failed_values = []

    # Get initial humidity value
    initial_value = driver.get_humidity()
    if initial_value is None:
        test_utils.print_func("❌ Failed to get initial humidity value")
        return False

    test_utils.print_func(f"Initial humidity value: {initial_value}")
    test_utils.print_func(f"Testing {len(test_values)} humidity values...")

    for test_value in test_values:
        test_utils.print_func(f"\nSetting humidity value to {test_value}...")

        # Get current device memory
        device_memory = DeviceMemory()
        if not device.get_memory(device_memory):
            test_utils.print_func("❌ Failed to get device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Update memory with new humidity value
        device_memory.sensor_b_reading = test_value
        if not device.set_memory(device_memory):
            test_utils.print_func("❌ Failed to set device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Small delay to ensure memory update is processed
        time.sleep(0.1)

        # Verify the value using the get_humidity API
        read_value = driver.get_humidity()
        if read_value is None:
            test_utils.print_func("❌ Failed to read humidity value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read humidity value: {read_value}")

        # Check if the read value matches what we set
        if read_value != test_value:
            test_utils.print_func(
                f"❌ Value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"✅ Verified humidity value {test_value}")

    # Reset humidity to initial value
    test_utils.print_func(f"\nResetting humidity to initial value {initial_value}...")
    device_memory = DeviceMemory()
    if device.get_memory(device_memory):
        device_memory.sensor_b_reading = initial_value
        device.set_memory(device_memory)

    # Small delay to ensure memory update is processed
    time.sleep(0.1)

    # Verify reset value
    final_value = driver.get_humidity()
    if final_value is None:
        test_utils.print_func("❌ Failed to get final humidity value")
        return False

    test_utils.print_func(f"Final humidity value after reset: {final_value}")

    if final_value != initial_value:
        test_utils.print_func(
            f"❌ Failed to reset humidity value: expected {initial_value}, got {final_value}"
        )
        all_passed = False

    if all_passed:
        test_utils.print_func(
            f"✅ Humidity get API test passed for all {len(test_values)} values"
        )
    else:
        test_utils.print_func(
            f"❌ Humidity get API test failed for values: {failed_values}"
        )

    return all_passed


def run_tests(driver, device=None):
    """Run all humidity sensor tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run humidity sensor direct test
    results.append(
        ("Humidity Sensor Direct", test_humidity_sensor_direct(driver, device))
    )

    # Run humidity get API test
    results.append(("Humidity Get API", test_humidity_get_api(driver, device)))

    # Print summary
    test_utils.print_func("\n=== Humidity Sensor Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
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
        test_utils.print_func("\n=== Running Humidity Sensor Tests ===")

        # Run both tests
        direct_test_result = test_humidity_sensor_direct(driver, device)
        api_test_result = test_humidity_get_api(driver, device)

        success = direct_test_result and api_test_result

        # Print overall result
        if success:
            test_utils.print_func("\n✅ All tests passed!")
        else:
            test_utils.print_func("\n❌ Some tests failed!")

        return 0 if success else 1
    finally:
        test_utils.teardown_test_environment(device, driver)


if __name__ == "__main__":
    sys.exit(main())
