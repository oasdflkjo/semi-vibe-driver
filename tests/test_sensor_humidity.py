#!/usr/bin/env python3
"""
Test cases for humidity sensor functionality.
"""


## quick fix to disable print statements
def print(string):
    return


def test_humidity_sensor_range(driver, device):
    """Test humidity sensor across the full range (0-255)."""
    print("\n=== Testing Humidity Sensor Range (Brute Force) ===")

    # Get initial humidity value
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    initial_value = sensors["humidity_value"]
    print(f"Initial humidity value: {initial_value}")

    # Test every value in the range 0-255
    all_passed = True
    failed_values = []

    print("Testing all humidity values from 0 to 255...")
    for test_value in range(256):
        # Set humidity directly in the device
        print(f"Setting humidity value to {test_value}...")

        # Get current state
        current_state = device.state
        print(
            f"Current state before update: {current_state['sensors']['humidity_value']}"
        )

        # Update state
        current_state["sensors"]["humidity_value"] = test_value
        device.state = current_state

        # Verify the state was updated
        updated_state = device.state
        print(f"Updated state: {updated_state['sensors']['humidity_value']}")

        # Verify the value through the driver
        sensors = driver.get_sensors()
        if not sensors:
            print("❌ Failed to get updated sensor data")
            all_passed = False
            failed_values.append(test_value)
            continue

        print(f"Driver reports humidity value: {sensors['humidity_value']}")
        if sensors["humidity_value"] != test_value:
            print(
                f"❌ Humidity value mismatch: expected {test_value}, got {sensors['humidity_value']}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            print(f"✅ Tested humidity values 0-{test_value}")

    # Reset humidity to initial value
    print(f"Resetting humidity to initial value {initial_value}...")
    current_state = device.state
    current_state["sensors"]["humidity_value"] = initial_value
    device.state = current_state

    if all_passed:
        print("✅ Humidity sensor range test passed for all 256 values")
    else:
        print(f"❌ Humidity sensor range test failed for values: {failed_values}")

    return all_passed


def run_tests(driver, device):
    """Run all humidity sensor tests."""
    results = []

    # Run humidity sensor range test (comprehensive)
    results.append(
        ("Humidity Sensor Range", test_humidity_sensor_range(driver, device))
    )

    # Print summary
    print("\n=== Humidity Sensor Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
