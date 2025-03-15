#!/usr/bin/env python3
"""
Test cases for temperature sensor functionality.
"""


def test_temperature_sensor_range(driver, device):
    """Test temperature sensor across the full range (0-255)."""
    print("\n=== Testing Temperature Sensor Range (Brute Force) ===")

    # Get initial temperature value
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    initial_value = sensors["temperature_value"]
    print(f"Initial temperature value: {initial_value}")

    # Test every value in the range 0-255
    all_passed = True
    failed_values = []

    print("Testing all temperature values from 0 to 255...")
    for test_value in range(256):
        # Set temperature directly in the device
        print(f"Setting temperature value to {test_value}...")

        # Get current state
        current_state = device.state
        print(
            f"Current state before update: {current_state['sensors']['temperature_value']}"
        )

        # Update state
        current_state["sensors"]["temperature_value"] = test_value
        device.state = current_state

        # Verify the state was updated
        updated_state = device.state
        print(f"Updated state: {updated_state['sensors']['temperature_value']}")

        # Verify the value through the driver
        sensors = driver.get_sensors()
        if not sensors:
            print("❌ Failed to get updated sensor data")
            all_passed = False
            failed_values.append(test_value)
            continue

        print(f"Driver reports temperature value: {sensors['temperature_value']}")
        if sensors["temperature_value"] != test_value:
            print(
                f"❌ Temperature value mismatch: expected {test_value}, got {sensors['temperature_value']}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            print(f"✅ Tested temperature values 0-{test_value}")

    # Reset temperature to initial value
    print(f"Resetting temperature to initial value {initial_value}...")
    current_state = device.state
    current_state["sensors"]["temperature_value"] = initial_value
    device.state = current_state

    if all_passed:
        print("✅ Temperature sensor range test passed for all 256 values")
    else:
        print(f"❌ Temperature sensor range test failed for values: {failed_values}")

    return all_passed


def run_tests(driver, device):
    """Run all temperature sensor tests."""
    results = []

    # Run temperature sensor range test (comprehensive)
    results.append(
        ("Temperature Sensor Range", test_temperature_sensor_range(driver, device))
    )

    # Print summary
    print("\n=== Temperature Sensor Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
