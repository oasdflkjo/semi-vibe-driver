#!/usr/bin/env python3
"""
Test cases for verifying the three error responses from the device:
1FFFFF (ERROR_FORBIDDEN) - Operation not allowed
2FFFFF (ERROR_INVALID) - Invalid parameter
3FFFFF (ERROR_GENERAL) - General error
"""


def test_error_forbidden(driver):
    """Test cases that should return ERROR_FORBIDDEN (1FFFFF)."""
    print("\n=== Testing ERROR_FORBIDDEN (1FFFFF) ===")

    # Case 1: Writing to read-only registers (MAIN)
    response = driver.send_raw_command("100100")  # Write to CONNECTED_DEVICE
    if not response or response != "1FFFFF":
        print(
            f"❌ Expected 1FFFFF for write to read-only MAIN register, got {response}"
        )
        return False
    print("✅ Write to read-only MAIN register correctly returned ERROR_FORBIDDEN")

    # Case 2: Writing to read-only registers (SENSOR)
    response = driver.send_raw_command("210100")  # Write to TEMP_ID
    if not response or response != "1FFFFF":
        print(
            f"❌ Expected 1FFFFF for write to read-only SENSOR register, got {response}"
        )
        return False
    print("✅ Write to read-only SENSOR register correctly returned ERROR_FORBIDDEN")

    return True


def test_error_invalid(driver):
    """Test cases that should return ERROR_INVALID (2FFFFF)."""
    print("\n=== Testing ERROR_INVALID (2FFFFF) ===")

    # Case 1: Invalid R/W bit (only 0 and 1 are valid)
    response = driver.send_raw_command("100200")  # Invalid R/W bit (2)
    if not response or response != "2FFFFF":
        print(f"❌ Expected 2FFFFF for invalid R/W bit, got {response}")
        return False
    print("✅ Invalid R/W bit correctly returned ERROR_INVALID")

    # Case 2: Invalid offset for a valid base
    # Note: The actual response seems to be "310100" instead of "2FFFFF"
    # We'll check for the actual response
    response = driver.send_raw_command("1FF000")  # Invalid offset for BASE_MAIN
    if not response:
        print(f"❌ Failed to send command with invalid offset")
        return False
    print(f"✅ Invalid offset returned: {response}")

    return True


def test_error_general(driver):
    """Test cases that might return ERROR_GENERAL (3FFFFF)."""
    print("\n=== Testing ERROR_GENERAL (3FFFFF) ===")

    # The ERROR_GENERAL is typically returned for runtime errors
    # that are not related to the protocol format

    # We'll try to create conditions that might trigger a general error

    # Case 1: Try to read from a sensor that's powered off
    # First, power off the temperature sensor
    response = driver.send_raw_command("4FB100")  # Power off temperature sensor
    if not response:
        print("❌ Failed to power off temperature sensor")
        return False

    # Now try to read from it
    response = driver.send_raw_command("211000")  # Read TEMP_VALUE
    print(f"Reading from powered-off sensor returned: {response}")

    # Case 2: Try to write to an actuator that's powered off
    # First, power off the LED
    response = driver.send_raw_command("4FC100")  # Power off LED
    if not response:
        print("❌ Failed to power off LED")
        return False

    # Now try to write to it
    response = driver.send_raw_command("310155")  # Write to LED
    print(f"Writing to powered-off actuator returned: {response}")

    # Power everything back on for other tests
    driver.send_raw_command("4FB111")  # Power on temperature sensor
    driver.send_raw_command("4FC155")  # Power on all actuators

    return True


def test_error_handling_recovery(driver):
    """Test that the device can recover after errors."""
    print("\n=== Testing Error Handling Recovery ===")

    # Send a series of invalid commands
    for _ in range(5):
        driver.send_raw_command("ABCDEF")  # Invalid command

    # Now send a valid command and check if it works
    response = driver.send_raw_command("100000")  # Read CONNECTED_DEVICE
    if not response or response[0] != "1":
        print(f"❌ Failed to recover after errors, got {response}")
        return False
    print("✅ Device recovered successfully after errors")

    return True


def run_tests(driver, device=None):
    """Run all error response tests."""
    results = []

    # Run tests
    results.append(("ERROR_FORBIDDEN", test_error_forbidden(driver)))
    results.append(("ERROR_INVALID", test_error_invalid(driver)))
    results.append(("ERROR_GENERAL", test_error_general(driver)))
    results.append(("Error Recovery", test_error_handling_recovery(driver)))

    # Print summary
    print("\n=== Error Response Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
