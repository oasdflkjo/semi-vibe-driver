#!/usr/bin/env python3
"""
Test cases for doors actuator functionality.
"""


def test_doors_range(driver):
    """Test doors control with valid bit patterns."""
    print("\n=== Testing Doors Control ===")

    # Get initial doors value
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    initial_value = actuators["doors_value"]
    print(f"Initial doors value: {initial_value}")

    # The doors only use bits 0, 2, 4, and 6 (mask 0x55 or 01010101 in binary)
    # This means we should only test values where these bits are set
    valid_values = []
    for i in range(16):  # Generate all combinations of the 4 door bits
        # Convert i to a 4-bit binary representation
        # Then place each bit at positions 0, 2, 4, 6
        value = 0
        for bit_pos in range(4):
            if (i & (1 << bit_pos)) != 0:
                value |= 1 << (bit_pos * 2)
        valid_values.append(value)

    print(f"Testing {len(valid_values)} valid door configurations...")

    # Test every valid value
    all_passed = True
    failed_values = []

    for test_value in valid_values:
        # Set doors to test value
        if not driver.set_doors(test_value):
            print(f"❌ Failed to set doors value to {test_value} (0x{test_value:02X})")
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

        if actuators["doors_value"] != test_value:
            print(
                f"❌ Doors value mismatch: expected {test_value} (0x{test_value:02X}), got {actuators['doors_value']} (0x{actuators['doors_value']:02X})"
            )
            all_passed = False
            failed_values.append(test_value)
            continue

        print(f"✅ Tested doors value: {test_value} (0x{test_value:02X})")

    # Reset doors to initial value
    print(f"Resetting doors to initial value {initial_value}...")
    if not driver.set_doors(initial_value):
        print("❌ Failed to reset doors value")
        return False

    if all_passed:
        print(f"✅ Doors test passed for all {len(valid_values)} valid configurations")
    else:
        print(f"❌ Doors test failed for values: {failed_values}")

    return all_passed


def run_tests(driver):
    """Run all doors tests."""
    results = []

    # Run doors test with valid configurations
    results.append(("Doors Control", test_doors_range(driver)))

    # Print summary
    print("\n=== Doors Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
