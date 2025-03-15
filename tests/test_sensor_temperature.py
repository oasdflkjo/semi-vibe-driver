#!/usr/bin/env python3
"""
Test cases for temperature sensor functionality.
"""

import sys
import os

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import SensorData
from device import DeviceMemory
import test_utils


def test_temperature_sensor_range(driver, device):
    """Test temperature sensor across the full range (0-255)."""
    test_utils.print_func("\n=== Testing Temperature Sensor Range (Brute Force) ===")

    # Get initial temperature value
    sensor_data = SensorData()
    if not driver.get_sensors(sensor_data):
        test_utils.print_func("❌ Failed to get sensor data")
        return False

    initial_value = sensor_data.temperature_value
    test_utils.print_func(f"Initial temperature value: {initial_value}")

    # Test every value in the range 0-255
    all_passed = True
    failed_values = []

    test_utils.print_func("Testing all temperature values from 0 to 255...")
    for test_value in range(256):
        # Set temperature directly in the device
        test_utils.print_func(f"Setting temperature value to {test_value}...")

        # Get current device memory
        device_memory = DeviceMemory()
        if not device.get_memory(device_memory):
            test_utils.print_func("❌ Failed to get device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Update memory
        device_memory.sensor_a_reading = test_value
        if not device.set_memory(device_memory):
            test_utils.print_func("❌ Failed to set device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value through the driver
        sensor_data = SensorData()
        if not driver.get_sensors(sensor_data):
            test_utils.print_func("❌ Failed to get updated sensor data")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(
            f"Driver reports temperature value: {sensor_data.temperature_value}"
        )
        if sensor_data.temperature_value != test_value:
            test_utils.print_func(
                f"❌ Temperature value mismatch: expected {test_value}, got {sensor_data.temperature_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            test_utils.print_func(f"✅ Tested temperature values 0-{test_value}")

    # Reset temperature to initial value
    test_utils.print_func(f"Resetting temperature to initial value {initial_value}...")
    device_memory = DeviceMemory()
    if device.get_memory(device_memory):
        device_memory.sensor_a_reading = initial_value
        device.set_memory(device_memory)

    if all_passed:
        test_utils.print_func(
            "✅ Temperature sensor range test passed for all 256 values"
        )
    else:
        test_utils.print_func(
            f"❌ Temperature sensor range test failed for values: {failed_values}"
        )

    return all_passed


def test_temperature_get_api(driver, device):
    """Test the get_temperature API function."""
    test_utils.print_func("\n=== Testing Temperature Get API ===")

    # Test a smaller set of values to keep the test manageable
    test_values = [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 255]
    all_passed = True
    failed_values = []

    # Get initial temperature value
    initial_value = driver.get_temperature()
    if initial_value is None:
        test_utils.print_func("❌ Failed to get initial temperature value")
        return False

    test_utils.print_func(f"Initial temperature value: {initial_value}")
    test_utils.print_func(f"Testing {len(test_values)} temperature values...")

    for test_value in test_values:
        test_utils.print_func(f"\nSetting temperature value to {test_value}...")

        # Get current device memory
        device_memory = DeviceMemory()
        if not device.get_memory(device_memory):
            test_utils.print_func("❌ Failed to get device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Update memory with new temperature value
        device_memory.sensor_a_reading = test_value
        if not device.set_memory(device_memory):
            test_utils.print_func("❌ Failed to set device memory")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value using the get_temperature API
        read_value = driver.get_temperature()
        if read_value is None:
            test_utils.print_func("❌ Failed to read temperature value")
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"Read temperature value: {read_value}")

        # Check if the read value matches what we set
        if read_value != test_value:
            test_utils.print_func(
                f"❌ Value mismatch: expected {test_value}, got {read_value}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        test_utils.print_func(f"✅ Verified temperature value {test_value}")

    # Reset temperature to initial value
    test_utils.print_func(
        f"\nResetting temperature to initial value {initial_value}..."
    )
    device_memory = DeviceMemory()
    if device.get_memory(device_memory):
        device_memory.sensor_a_reading = initial_value
        device.set_memory(device_memory)

    # Verify reset value
    final_value = driver.get_temperature()
    if final_value is None:
        test_utils.print_func("❌ Failed to get final temperature value")
        return False

    test_utils.print_func(f"Final temperature value after reset: {final_value}")

    if final_value != initial_value:
        test_utils.print_func(
            f"❌ Failed to reset temperature value: expected {initial_value}, got {final_value}"
        )
        all_passed = False

    if all_passed:
        test_utils.print_func(
            f"✅ Temperature get API test passed for all {len(test_values)} values"
        )
    else:
        test_utils.print_func(
            f"❌ Temperature get API test failed for values: {failed_values}"
        )

    return all_passed


def run_tests(driver, device):
    """Run all temperature sensor tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run temperature sensor range test (comprehensive)
    results.append(
        ("Temperature Sensor Range", test_temperature_sensor_range(driver, device))
    )

    # Run temperature get API test
    results.append(("Temperature Get API", test_temperature_get_api(driver, device)))

    # Print summary
    test_utils.print_func("\n=== Temperature Sensor Tests Summary ===")
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
        # Run the tests
        test_utils.print_func("\n=== Running Temperature Sensor Tests ===")

        # Run both tests
        range_test_result = test_temperature_sensor_range(driver, device)
        api_test_result = test_temperature_get_api(driver, device)

        success = range_test_result and api_test_result

        # Print result
        if success:
            test_utils.print_func("\n✅ All tests passed!")
        else:
            test_utils.print_func("\n❌ Some tests failed!")

        return 0 if success else 1
    finally:
        test_utils.teardown_test_environment(device, driver)


if __name__ == "__main__":
    sys.exit(main())
