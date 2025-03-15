#!/usr/bin/env python3
"""
Test cases for power down functionality.
"""


def test_power_sensors(driver):
    """Test powering sensors on and off."""
    print("\n=== Testing Sensor Power Control ===")

    # Get initial status
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    print(f"Initial sensors powered state: {status['sensors_powered']}")

    # Power off all sensors
    print("Powering off all sensors...")
    if not driver.power_sensors(False, False):
        print("❌ Failed to power off sensors")
        return False

    # Verify sensors are powered off
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if status["sensors_powered"]:
        print("❌ Sensors still powered on after power off command")
        return False

    print("✅ All sensors powered off successfully")

    # Try to read sensor data (should still work but values might be invalid)
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    print(
        f"Sensor values when powered off: Temperature={sensors['temperature_value']}, Humidity={sensors['humidity_value']}"
    )

    # Power on temperature sensor only
    print("Powering on temperature sensor only...")
    if not driver.power_sensors(True, False):
        print("❌ Failed to power on temperature sensor")
        return False

    # Verify temperature sensor is powered on
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["sensors_powered"]:
        print("❌ Sensors still powered off after power on command")
        return False

    print("✅ Temperature sensor powered on successfully")

    # Power on all sensors
    print("Powering on all sensors...")
    if not driver.power_sensors(True, True):
        print("❌ Failed to power on all sensors")
        return False

    # Verify all sensors are powered on
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["sensors_powered"]:
        print("❌ Sensors still powered off after power on command")
        return False

    print("✅ All sensors powered on successfully")

    return True


def test_power_actuators(driver):
    """Test powering actuators on and off."""
    print("\n=== Testing Actuator Power Control ===")

    # Get initial status
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    print(f"Initial actuators powered state: {status['actuators_powered']}")

    # Power off all actuators
    print("Powering off all actuators...")
    if not driver.power_actuators(False, False, False, False):
        print("❌ Failed to power off actuators")
        return False

    # Verify actuators are powered off
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if status["actuators_powered"]:
        print("❌ Actuators still powered on after power off command")
        return False

    print("✅ All actuators powered off successfully")

    # Try to set actuator values (should fail or have no effect)
    print("Attempting to set LED value while powered off...")
    test_value = 128
    driver.set_led(test_value)

    # Verify the value didn't change or is ignored
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    print(f"LED value after attempt to set while powered off: {actuators['led_value']}")

    # Power on LED only
    print("Powering on LED only...")
    if not driver.power_actuators(True, False, False, False):
        print("❌ Failed to power on LED")
        return False

    # Verify LED is powered on
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["actuators_powered"]:
        print("❌ Actuators still powered off after power on command")
        return False

    print("✅ LED powered on successfully")

    # Set LED value now that it's powered on
    print(f"Setting LED value to {test_value}...")
    if not driver.set_led(test_value):
        print("❌ Failed to set LED value")
        return False

    # Verify the value changed
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    if actuators["led_value"] != test_value:
        print(
            f"❌ LED value mismatch: expected {test_value}, got {actuators['led_value']}"
        )
        return False

    print(f"✅ LED value successfully set to {test_value} when powered on")

    # Power on all actuators
    print("Powering on all actuators...")
    if not driver.power_actuators(True, True, True, True):
        print("❌ Failed to power on all actuators")
        return False

    # Verify all actuators are powered on
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["actuators_powered"]:
        print("❌ Actuators still powered off after power on command")
        return False

    print("✅ All actuators powered on successfully")

    return True


def test_power_cycle(driver):
    """Test power cycling all components."""
    print("\n=== Testing Power Cycling ===")

    # Power off everything
    print("Powering off all components...")
    if not driver.power_sensors(False, False) or not driver.power_actuators(
        False, False, False, False
    ):
        print("❌ Failed to power off all components")
        return False

    # Verify everything is off
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if status["sensors_powered"] or status["actuators_powered"]:
        print("❌ Some components still powered on after power off command")
        return False

    print("✅ All components powered off successfully")

    # Power on everything
    print("Powering on all components...")
    if not driver.power_sensors(True, True) or not driver.power_actuators(
        True, True, True, True
    ):
        print("❌ Failed to power on all components")
        return False

    # Verify everything is on
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status["sensors_powered"] or not status["actuators_powered"]:
        print("❌ Some components still powered off after power on command")
        return False

    print("✅ All components powered on successfully")

    return True


def run_tests(driver):
    """Run all power down tests."""
    results = []

    # Run power tests
    results.append(("Sensor Power Control", test_power_sensors(driver)))
    results.append(("Actuator Power Control", test_power_actuators(driver)))
    results.append(("Power Cycling", test_power_cycle(driver)))

    # Print summary
    print("\n=== Power Down Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
