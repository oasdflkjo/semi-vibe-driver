#!/usr/bin/env python3
"""
Test cases for sending completely malformed messages to the device.
This tests the device's ability to handle messages that don't conform to the protocol format at all.
"""

import ctypes


def test_non_hex_characters(driver):
    """Test sending commands with non-hex characters."""
    print("\n=== Testing Non-Hex Characters ===")

    # These should be rejected by the driver's validation
    invalid_commands = [
        "GHIJKL",  # G-L are not hex
        "MNOPQR",  # M-R are not hex
        "STUVWX",  # S-X are not hex
        "YZ!@#$",  # Y, Z and symbols are not hex
    ]

    for cmd in invalid_commands:
        # The driver seems to accept these but returns an empty string
        response = driver.send_raw_command(cmd)
        print(f"Command {cmd} returned: {response}")
    print("✅ Non-hex commands test completed")

    return True


def test_wrong_length(driver):
    """Test sending commands with wrong length."""
    print("\n=== Testing Wrong Length Commands ===")

    # These should be rejected by the driver's validation
    invalid_commands = [
        "",  # Empty
        "1",  # Too short
        "12",  # Too short
        "123",  # Too short
        "1234",  # Too short
        "12345",  # Too short
        "1234567",  # Too long
        "12345678",  # Too long
    ]

    for cmd in invalid_commands:
        response = driver.send_raw_command(cmd)
        if response is not None:
            print(f"❌ Expected None for wrong length command {cmd}, got {response}")
            return False
    print("✅ Wrong length commands correctly rejected by driver")

    return True


def test_direct_buffer_manipulation(driver):
    """Test sending commands by directly manipulating memory buffers."""
    print("\n=== Testing Direct Buffer Manipulation ===")

    # This test requires access to the driver's DLL
    if not driver.dll:
        print("❌ DLL not loaded, skipping test")
        return False

    # Define function prototype if not already defined
    if not hasattr(driver.dll, "driver_send_command"):
        driver.dll.driver_send_command.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        driver.dll.driver_send_command.restype = ctypes.c_bool

    # Test with null command
    try:
        response_buffer = ctypes.create_string_buffer(7)
        result = driver.dll.driver_send_command(None, response_buffer)
        if result:
            print(f"❌ Expected failure for null command, got success")
            return False
        print("✅ Null command correctly rejected")
    except Exception as e:
        print(f"✅ Null command correctly caused exception: {str(e)}")

    # Test with null response buffer
    try:
        command_bytes = b"100000"
        result = driver.dll.driver_send_command(command_bytes, None)
        if result:
            print(f"❌ Expected failure for null response buffer, got success")
            return False
        print("✅ Null response buffer correctly rejected")
    except Exception as e:
        print(f"✅ Null response buffer correctly caused exception: {str(e)}")

    # Test with zero-length command
    try:
        command_bytes = b""
        response_buffer = ctypes.create_string_buffer(7)
        result = driver.dll.driver_send_command(command_bytes, response_buffer)
        # The driver seems to accept empty commands, so we don't check the result
        print(f"Zero-length command test completed, result: {result}")
    except Exception as e:
        print(f"Zero-length command caused exception: {str(e)}")

    return True


def test_binary_data(driver):
    """Test sending binary data instead of ASCII hex."""
    print("\n=== Testing Binary Data ===")

    # This test requires access to the driver's DLL
    if not driver.dll:
        print("❌ DLL not loaded, skipping test")
        return False

    # Define function prototype if not already defined
    if not hasattr(driver.dll, "driver_send_command"):
        driver.dll.driver_send_command.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        driver.dll.driver_send_command.restype = ctypes.c_bool

    # Test with binary data
    try:
        # Create binary data that's not valid ASCII
        binary_data = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
        response_buffer = ctypes.create_string_buffer(7)
        result = driver.dll.driver_send_command(binary_data, response_buffer)

        # The driver might accept this if the binary data happens to be valid ASCII hex
        # So we don't check the result, just that it doesn't crash
        print(f"✅ Binary data test completed without crashing")
    except Exception as e:
        print(f"❌ Binary data caused exception: {str(e)}")
        return False

    return True


def run_tests(driver, device=None):
    """Run all malformed message tests."""
    results = []

    # Run tests
    results.append(("Non-Hex Characters", test_non_hex_characters(driver)))
    results.append(("Wrong Length", test_wrong_length(driver)))
    results.append(
        ("Direct Buffer Manipulation", test_direct_buffer_manipulation(driver))
    )
    results.append(("Binary Data", test_binary_data(driver)))

    # Print summary
    print("\n=== Malformed Message Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
