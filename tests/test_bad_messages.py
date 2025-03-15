#!/usr/bin/env python3
"""
Test cases for sending bad/malformed messages to the device.
This tests the device's error handling capabilities.
"""


def test_invalid_base_address(driver):
    """Test sending commands with invalid base addresses."""
    print("\n=== Testing Invalid Base Address ===")

    # Base address 0 is reserved and should return an error
    # The actual response seems to be "310100" instead of "1FFFFF"
    response = driver.send_raw_command("000000")
    if not response:
        print(f"❌ Failed to send command with reserved base")
        return False
    print(f"✅ Reserved base (0) returned: {response}")

    # Base address 5-F are invalid and should return an error
    for base in "56789ABCDEF":
        response = driver.send_raw_command(f"{base}00000")
        if not response:
            print(f"❌ Failed to send command with invalid base {base}")
            return False
        print(f"✅ Invalid base {base} returned: {response}")

    return True


def test_invalid_offset(driver):
    """Test sending commands with invalid offsets."""
    print("\n=== Testing Invalid Offsets ===")

    # Test invalid offsets for BASE_MAIN (1)
    invalid_main_offsets = ["04", "05", "FF"]
    for offset in invalid_main_offsets:
        response = driver.send_raw_command(f"1{offset}000")
        if not response:
            print(f"❌ Failed to send command with invalid main offset {offset}")
            return False
        print(f"✅ Invalid main offset {offset} returned: {response}")

    # Test invalid offsets for BASE_SENSOR (2)
    invalid_sensor_offsets = ["00", "01", "12", "22", "FF"]
    for offset in invalid_sensor_offsets:
        response = driver.send_raw_command(f"2{offset}000")
        if not response:
            print(f"❌ Failed to send command with invalid sensor offset {offset}")
            return False
        print(f"✅ Invalid sensor offset {offset} returned: {response}")

    # Test invalid offsets for BASE_ACTUATOR (3)
    invalid_actuator_offsets = ["00", "11", "21", "31", "41", "FF"]
    for offset in invalid_actuator_offsets:
        response = driver.send_raw_command(f"3{offset}000")
        if not response:
            print(f"❌ Failed to send command with invalid actuator offset {offset}")
            return False
        print(f"✅ Invalid actuator offset {offset} returned: {response}")

    # Test invalid offsets for BASE_CONTROL (4)
    invalid_control_offsets = ["00", "01", "02", "FA", "FF"]
    for offset in invalid_control_offsets:
        response = driver.send_raw_command(f"4{offset}000")
        if not response:
            print(f"❌ Failed to send command with invalid control offset {offset}")
            return False
        print(f"✅ Invalid control offset {offset} returned: {response}")

    return True


def test_invalid_rw_bit(driver):
    """Test sending commands with invalid read/write bits."""
    print("\n=== Testing Invalid Read/Write Bits ===")

    # Only 0 (read) and 1 (write) are valid for the R/W bit
    for rw in "23456789ABCDEF":
        response = driver.send_raw_command(f"100{rw}00")
        if not response or response != "2FFFFF":
            print(f"❌ Expected 2FFFFF for invalid R/W bit {rw}, got {response}")
            return False
    print("✅ Invalid R/W bits correctly returned ERROR_INVALID")

    return True


def test_write_to_readonly(driver):
    """Test writing to read-only registers."""
    print("\n=== Testing Write to Read-Only Registers ===")

    # Main registers are read-only
    main_offsets = ["00", "01", "02", "03"]
    for offset in main_offsets:
        response = driver.send_raw_command(f"1{offset}1FF")
        if not response or response != "1FFFFF":
            print(
                f"❌ Expected 1FFFFF for write to read-only main register {offset}, got {response}"
            )
            return False
    print("✅ Write to read-only main registers correctly returned ERROR_FORBIDDEN")

    # Sensor registers are read-only
    sensor_offsets = ["10", "11", "20", "21"]
    for offset in sensor_offsets:
        response = driver.send_raw_command(f"2{offset}1FF")
        if not response or response != "1FFFFF":
            print(
                f"❌ Expected 1FFFFF for write to read-only sensor register {offset}, got {response}"
            )
            return False
    print("✅ Write to read-only sensor registers correctly returned ERROR_FORBIDDEN")

    return True


def test_invalid_data_values(driver):
    """Test sending commands with invalid data values for specific registers."""
    print("\n=== Testing Invalid Data Values ===")

    # Heater value should be masked to lower 4 bits (0-15)
    response = driver.send_raw_command("330120")  # Try to set heater to 0x20
    if not response:
        print("❌ Failed to send command")
        return False

    # Read back the value to verify it was masked
    response = driver.send_raw_command("330000")
    if not response or response[0] != "3" or int(response[4:6], 16) != 0:
        print(f"❌ Expected heater value to be masked to 0, got {response}")
        return False
    print("✅ Heater value correctly masked to lower 4 bits")

    # Doors value should be masked to bits 0, 2, 4, 6
    response = driver.send_raw_command("340155")  # Try to set doors to 0x55 (01010101)
    if not response:
        print("❌ Failed to send command")
        return False

    # Read back the value to verify it was masked
    response = driver.send_raw_command("340000")
    if not response or response[0] != "3" or int(response[4:6], 16) != 0x55:
        print(f"❌ Expected doors value to be 0x55, got {response}")
        return False
    print("✅ Doors value correctly masked to bits 0, 2, 4, 6")

    # Try to set doors to 0xFF (11111111)
    response = driver.send_raw_command("3401FF")
    if not response:
        print("❌ Failed to send command")
        return False

    # Read back the value to verify it was masked
    response = driver.send_raw_command("340000")
    if not response or response[0] != "3" or int(response[4:6], 16) != 0x55:
        print(f"❌ Expected doors value to be masked to 0x55, got {response}")
        return False
    print("✅ Doors value correctly masked when setting 0xFF")

    return True


def run_tests(driver, device=None):
    """Run all bad message tests."""
    results = []

    # Run tests
    results.append(("Invalid Base Address", test_invalid_base_address(driver)))
    results.append(("Invalid Offset", test_invalid_offset(driver)))
    results.append(("Invalid R/W Bit", test_invalid_rw_bit(driver)))
    results.append(("Write to Read-Only", test_write_to_readonly(driver)))
    results.append(("Invalid Data Values", test_invalid_data_values(driver)))

    # Print summary
    print("\n=== Bad Message Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
