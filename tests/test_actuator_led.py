#!/usr/bin/env python3
"""
Test cases for LED actuator functionality.
"""


## quick fix to disable print statements
def print(string):
    return


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


def run_tests(driver):
    """Run all LED tests."""
    results = []

    # Run LED range test (comprehensive)
    results.append(("LED Range Control", test_led_range(driver)))

    # Print summary
    print("\n=== LED Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
