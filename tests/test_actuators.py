#!/usr/bin/env python3
"""
Test cases for actuator functionality.
"""


def test_led_control(driver):
    """Test LED control functionality."""
    print("\n=== Testing LED Control ===")

    # Get initial LED value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    initial_value = actuators["led_value"]
    print(f"Initial LED value: {initial_value}")

    # Set LED to a new value
    test_value = 128
    print(f"Setting LED to {test_value}...")
    if not driver.set_led(test_value):
        print("❌ Failed to set LED value")
        return False

    # Verify the new value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get updated actuator data")
        return False

    if actuators["led_value"] != test_value:
        print(
            f"❌ LED value mismatch: expected {test_value}, got {actuators['led_value']}"
        )
        return False

    print(f"✅ LED value successfully set to {test_value}")

    # Reset LED to initial value
    print(f"Resetting LED to initial value {initial_value}...")
    if not driver.set_led(initial_value):
        print("❌ Failed to reset LED value")
        return False

    print("✅ LED control test passed")
    return True


def test_fan_control(driver):
    """Test fan control functionality."""
    print("\n=== Testing Fan Control ===")

    # Get initial fan value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    initial_value = actuators["fan_value"]
    print(f"Initial fan value: {initial_value}")

    # Set fan to a new value
    test_value = 200
    print(f"Setting fan to {test_value}...")
    if not driver.set_fan(test_value):
        print("❌ Failed to set fan value")
        return False

    # Verify the new value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get updated actuator data")
        return False

    if actuators["fan_value"] != test_value:
        print(
            f"❌ Fan value mismatch: expected {test_value}, got {actuators['fan_value']}"
        )
        return False

    print(f"✅ Fan value successfully set to {test_value}")

    # Reset fan to initial value
    print(f"Resetting fan to initial value {initial_value}...")
    if not driver.set_fan(initial_value):
        print("❌ Failed to reset fan value")
        return False

    print("✅ Fan control test passed")
    return True


def run_tests(driver):
    """Run all actuator tests."""
    results = []

    # Run LED control test
    results.append(("LED Control", test_led_control(driver)))

    # Run fan control test
    results.append(("Fan Control", test_fan_control(driver)))

    # Print summary
    print("\n=== Actuator Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
