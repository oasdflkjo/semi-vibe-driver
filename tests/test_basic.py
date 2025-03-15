#!/usr/bin/env python3
"""
Basic test cases for device connectivity.
"""


## quick fix to disable print statements
def print(string):
    return


def test_connection(driver):
    """Test basic connection to the device."""
    print("\n=== Testing Connection ===")

    # Get device status
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    if not status.get("connected", False):
        print("❌ Device reports not connected")
        return False

    print("✅ Device is connected")
    return True


def test_direct_access(driver, device):
    """Test direct access to the device (bypassing sockets)."""
    print("\n=== Testing Direct Access ===")

    # Set a value directly on the device
    test_value = 123
    print(f"Setting LED directly to {test_value}...")
    if not device.set_led(test_value):
        print("❌ Failed to set LED value directly")
        return False

    # Read the value through the driver
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data through driver")
        return False

    if actuators["led_value"] != test_value:
        print(
            f"❌ LED value mismatch: expected {test_value}, got {actuators['led_value']}"
        )
        return False

    print(f"✅ LED value successfully verified through driver: {test_value}")
    return True


def run_tests(driver, device=None):
    """Run all basic tests."""
    results = []

    # Run connection test
    results.append(("Connection", test_connection(driver)))

    # Run direct access test if device is provided
    if device:
        results.append(("Direct Access", test_direct_access(driver, device)))

    # Print summary
    print("\n=== Basic Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed
