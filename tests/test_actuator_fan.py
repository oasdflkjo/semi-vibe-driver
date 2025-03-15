#!/usr/bin/env python3
"""
Test cases for fan actuator functionality.
"""


## quick fix to disable print statements
def print(string):
    return


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
    """Run all fan tests."""
    results = []

    # Run fan range test (comprehensive)
    results.append(("Fan Range Control", test_fan_range(driver)))

    # Print summary
    print("\n=== Fan Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
