#!/usr/bin/env python3
"""
Test cases for temperature and humidity sensors.
"""


def test_temperature_sensor(driver):
    """Test the temperature sensor functionality."""
    print("\n=== Testing Temperature Sensor ===")

    # Get sensor data
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    print(f"Temperature ID: 0x{sensors['temperature_id']:02X}")
    print(f"Temperature value: {sensors['temperature_value']}")

    # Test if temperature sensor is powered
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["sensors_powered"]:
        print("❌ Temperature sensor is not powered")
        return False

    print("✅ Temperature sensor test passed")
    return True


def test_humidity_sensor(driver):
    """Test the humidity sensor functionality."""
    print("\n=== Testing Humidity Sensor ===")

    # Get sensor data
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    print(f"Humidity ID: 0x{sensors['humidity_id']:02X}")
    print(f"Humidity value: {sensors['humidity_value']}")

    # Test if humidity sensor is powered
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["sensors_powered"]:
        print("❌ Humidity sensor is not powered")
        return False

    print("✅ Humidity sensor test passed")
    return True


def run_tests(driver):
    """Run all sensor tests."""
    results = []

    # Run temperature sensor test
    results.append(("Temperature Sensor", test_temperature_sensor(driver)))

    # Run humidity sensor test
    results.append(("Humidity Sensor", test_humidity_sensor(driver)))

    # Print summary
    print("\n=== Sensor Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
