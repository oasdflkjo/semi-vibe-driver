#!/usr/bin/env python3
"""
Test cases for sensor functionality.
"""


def test_temperature_sensor(driver, device):
    """Test temperature sensor functionality."""
    print("\n=== Testing Temperature Sensor ===")

    # Get initial temperature value
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    initial_value = sensors["temperature_value"]
    print(f"Initial temperature value: {initial_value}")

    # Modify temperature directly in the device
    new_temp = 35
    print(f"Setting temperature directly to {new_temp}...")
    device.state["sensors"]["temperature_value"] = new_temp

    # Verify the new value through the driver
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get updated sensor data")
        return False

    if sensors["temperature_value"] != new_temp:
        print(
            f"❌ Temperature value mismatch: expected {new_temp}, got {sensors['temperature_value']}"
        )
        return False

    print(f"✅ Temperature value successfully verified: {new_temp}")

    # Reset temperature to initial value
    print(f"Resetting temperature to initial value {initial_value}...")
    device.state["sensors"]["temperature_value"] = initial_value

    print("✅ Temperature sensor test passed")
    return True


def test_humidity_sensor(driver, device):
    """Test humidity sensor functionality."""
    print("\n=== Testing Humidity Sensor ===")

    # Get initial humidity value
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    initial_value = sensors["humidity_value"]
    print(f"Initial humidity value: {initial_value}")

    # Modify humidity directly in the device
    new_humidity = 75
    print(f"Setting humidity directly to {new_humidity}...")
    device.state["sensors"]["humidity_value"] = new_humidity

    # Verify the new value through the driver
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get updated sensor data")
        return False

    if sensors["humidity_value"] != new_humidity:
        print(
            f"❌ Humidity value mismatch: expected {new_humidity}, got {sensors['humidity_value']}"
        )
        return False

    print(f"✅ Humidity value successfully verified: {new_humidity}")

    # Reset humidity to initial value
    print(f"Resetting humidity to initial value {initial_value}...")
    device.state["sensors"]["humidity_value"] = initial_value

    print("✅ Humidity sensor test passed")
    return True


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
        device.state["sensors"]["temperature_value"] = test_value

        # Verify the value through the driver
        sensors = driver.get_sensors()
        if not sensors:
            print("❌ Failed to get updated sensor data")
            all_passed = False
            failed_values.append(test_value)
            continue

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
    device.state["sensors"]["temperature_value"] = initial_value

    if all_passed:
        print("✅ Temperature sensor range test passed for all 256 values")
    else:
        print(f"❌ Temperature sensor range test failed for values: {failed_values}")

    return all_passed


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
        device.state["sensors"]["humidity_value"] = test_value

        # Verify the value through the driver
        sensors = driver.get_sensors()
        if not sensors:
            print("❌ Failed to get updated sensor data")
            all_passed = False
            failed_values.append(test_value)
            continue

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
    device.state["sensors"]["humidity_value"] = initial_value

    if all_passed:
        print("✅ Humidity sensor range test passed for all 256 values")
    else:
        print(f"❌ Humidity sensor range test failed for values: {failed_values}")

    return all_passed


def run_tests(driver, device):
    """Run all sensor tests."""
    results = []

    # Run temperature sensor test
    results.append(("Temperature Sensor", test_temperature_sensor(driver, device)))

    # Run humidity sensor test
    results.append(("Humidity Sensor", test_humidity_sensor(driver, device)))

    # Run temperature sensor range test
    results.append(
        ("Temperature Sensor Range", test_temperature_sensor_range(driver, device))
    )

    # Run humidity sensor range test
    results.append(
        ("Humidity Sensor Range", test_humidity_sensor_range(driver, device))
    )

    # Print summary
    print("\n=== Sensor Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
