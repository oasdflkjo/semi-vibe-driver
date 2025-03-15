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


def test_led_range(driver):
    """Test LED control across the full range (0-255)."""
    print("\n=== Testing LED Range (Brute Force) ===")

    # Get initial LED value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    initial_value = actuators["led_value"]
    print(f"Initial LED value: {initial_value}")

    # Test every value in the range 0-255
    all_passed = True
    failed_values = []

    print("Testing all LED values from 0 to 255...")
    for test_value in range(256):
        # Set LED to test value
        if not driver.set_led(test_value):
            print(f"❌ Failed to set LED value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value
        actuators = driver.get_actuators()
        if not actuators:
            print("❌ Failed to get updated actuator data")
            all_passed = False
            failed_values.append(test_value)
            continue

        if actuators["led_value"] != test_value:
            print(
                f"❌ LED value mismatch: expected {test_value}, got {actuators['led_value']}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            print(f"✅ Tested LED values 0-{test_value}")

    # Reset LED to initial value
    print(f"Resetting LED to initial value {initial_value}...")
    if not driver.set_led(initial_value):
        print("❌ Failed to reset LED value")
        return False

    if all_passed:
        print("✅ LED range test passed for all 256 values")
    else:
        print(f"❌ LED range test failed for values: {failed_values}")

    return all_passed


def test_fan_range(driver):
    """Test fan control across the full range (0-255)."""
    print("\n=== Testing Fan Range (Brute Force) ===")

    # Get initial fan value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    initial_value = actuators["fan_value"]
    print(f"Initial fan value: {initial_value}")

    # Test every value in the range 0-255
    all_passed = True
    failed_values = []

    print("Testing all fan values from 0 to 255...")
    for test_value in range(256):
        # Set fan to test value
        if not driver.set_fan(test_value):
            print(f"❌ Failed to set fan value to {test_value}")
            all_passed = False
            failed_values.append(test_value)
            continue

        # Verify the value
        actuators = driver.get_actuators()
        if not actuators:
            print("❌ Failed to get updated actuator data")
            all_passed = False
            failed_values.append(test_value)
            continue

        if actuators["fan_value"] != test_value:
            print(
                f"❌ Fan value mismatch: expected {test_value}, got {actuators['fan_value']}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 25 values
        if test_value % 25 == 0 or test_value == 255:
            print(f"✅ Tested fan values 0-{test_value}")

    # Reset fan to initial value
    print(f"Resetting fan to initial value {initial_value}...")
    if not driver.set_fan(initial_value):
        print("❌ Failed to reset fan value")
        return False

    if all_passed:
        print("✅ Fan range test passed for all 256 values")
    else:
        print(f"❌ Fan range test failed for values: {failed_values}")

    return all_passed


def run_tests(driver):
    """Run all actuator tests."""
    results = []

    # Run basic LED control test
    results.append(("LED Control", test_led_control(driver)))

    # Run basic fan control test
    results.append(("Fan Control", test_fan_control(driver)))

    # Run LED range test
    results.append(("LED Range", test_led_range(driver)))

    # Run fan range test
    results.append(("Fan Range", test_fan_range(driver)))

    # Print summary
    print("\n=== Actuator Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
