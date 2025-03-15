#!/usr/bin/env python3
"""
Test cases for heater actuator functionality.
"""


## quick fix to disable print statements
def print(string):
    return


def test_heater_range(driver):
    """Test heater control across the valid range (0-15)."""
    print("\n=== Testing Heater Range (Brute Force) ===")

    # Get initial heater value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    initial_value = actuators["heater_value"]
    print(f"Initial heater value: {initial_value}")

    # Test every value in the valid range 0-15 (only lower 4 bits are used)
    all_passed = True
    failed_values = []

    print("Testing all heater values from 0 to 15...")
    for test_value in range(16):  # Changed from 256 to 16
        # Set heater to test value
        if not driver.set_heater(test_value):
            print(f"❌ Failed to set heater value to {test_value}")
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

        if actuators["heater_value"] != test_value:
            print(
                f"❌ Heater value mismatch: expected {test_value}, got {actuators['heater_value']}"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        # Print progress every 5 values
        if (
            test_value % 5 == 0 or test_value == 15
        ):  # Changed from 25 to 5 and 255 to 15
            print(f"✅ Tested heater values 0-{test_value}")

    # Reset heater to initial value
    print(f"Resetting heater to initial value {initial_value}...")
    if not driver.set_heater(initial_value):
        print("❌ Failed to reset heater value")
        return False

    if all_passed:
        print("✅ Heater range test passed for all 16 values")  # Changed from 256 to 16
    else:
        print(f"❌ Heater range test failed for values: {failed_values}")

    return all_passed


def run_tests(driver):
    """Run all heater tests."""
    results = []

    # Run heater range test (comprehensive)
    results.append(("Heater Range Control", test_heater_range(driver)))

    # Print summary
    print("\n=== Heater Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
