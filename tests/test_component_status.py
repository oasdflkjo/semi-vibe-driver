#!/usr/bin/env python3
"""
Test cases for component status functionality (power state and error state).
"""

import sys
import os

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import (
    COMPONENT_TEMPERATURE,
    COMPONENT_HUMIDITY,
    COMPONENT_LED,
    COMPONENT_FAN,
    COMPONENT_HEATER,
    COMPONENT_DOORS,
)
from device import DeviceMemory
import test_utils


def test_power_state(driver, device):
    """Test getting power state for all components."""
    test_utils.print_func("\n=== Testing Power State ===")

    # Get current device memory to check initial state
    device_memory = DeviceMemory()
    if not device.get_memory(device_memory):
        test_utils.print_func("❌ Failed to get device memory")
        return False

    # Test all components
    components = [
        ("Temperature", COMPONENT_TEMPERATURE),
        ("Humidity", COMPONENT_HUMIDITY),
        ("LED", COMPONENT_LED),
        ("Fan", COMPONENT_FAN),
        ("Heater", COMPONENT_HEATER),
        ("Doors", COMPONENT_DOORS),
    ]

    all_passed = True

    # Test getting power state for each component
    for name, component_type in components:
        power_state = driver.get_power_state(component_type)
        if power_state is None:
            test_utils.print_func(f"❌ Failed to get power state for {name}")
            all_passed = False
            continue

        test_utils.print_func(f"{name} power state: {'ON' if power_state else 'OFF'}")

    # Test the new set_power_state function
    test_utils.print_func("\n=== Testing Set Power State ===")

    # Test each component individually
    for name, component_type in components:
        # Get initial state
        initial_state = driver.get_power_state(component_type)
        if initial_state is None:
            test_utils.print_func(f"❌ Failed to get initial power state for {name}")
            all_passed = False
            continue

        # Turn off
        test_utils.print_func(f"Turning {name} OFF...")
        if not driver.set_power_state(component_type, False):
            test_utils.print_func(f"❌ Failed to turn {name} OFF")
            all_passed = False
            continue

        # Verify it's off
        power_state = driver.get_power_state(component_type)
        if power_state is None:
            test_utils.print_func(
                f"❌ Failed to get power state for {name} after turning OFF"
            )
            all_passed = False
            continue

        if power_state:
            test_utils.print_func(f"❌ {name} is still ON after turning OFF")
            all_passed = False
            continue

        test_utils.print_func(f"✅ {name} is now OFF")

        # Turn on
        test_utils.print_func(f"Turning {name} ON...")
        if not driver.set_power_state(component_type, True):
            test_utils.print_func(f"❌ Failed to turn {name} ON")
            all_passed = False
            continue

        # Verify it's on
        power_state = driver.get_power_state(component_type)
        if power_state is None:
            test_utils.print_func(
                f"❌ Failed to get power state for {name} after turning ON"
            )
            all_passed = False
            continue

        if not power_state:
            test_utils.print_func(f"❌ {name} is still OFF after turning ON")
            all_passed = False
            continue

        test_utils.print_func(f"✅ {name} is now ON")

        # Restore initial state
        if initial_state != power_state:
            test_utils.print_func(
                f"Restoring {name} to initial state ({initial_state})..."
            )
            if not driver.set_power_state(component_type, initial_state):
                test_utils.print_func(f"❌ Failed to restore {name} to initial state")
                all_passed = False
                continue

    # Test power on/off for sensors
    test_utils.print_func("\nTesting power on/off for sensors...")

    # Power off sensors
    if not driver.power_sensors(False, False):
        test_utils.print_func("❌ Failed to power off sensors")
        all_passed = False
    else:
        # Verify power state
        temp_power = driver.get_power_state(COMPONENT_TEMPERATURE)
        humid_power = driver.get_power_state(COMPONENT_HUMIDITY)

        if temp_power is None or humid_power is None:
            test_utils.print_func(
                "❌ Failed to get sensor power states after power off"
            )
            all_passed = False
        elif temp_power or humid_power:
            test_utils.print_func("❌ Sensors still powered after power off command")
            all_passed = False
        else:
            test_utils.print_func("✅ Sensors powered off successfully")

    # Power on sensors
    if not driver.power_sensors(True, True):
        test_utils.print_func("❌ Failed to power on sensors")
        all_passed = False
    else:
        # Verify power state
        temp_power = driver.get_power_state(COMPONENT_TEMPERATURE)
        humid_power = driver.get_power_state(COMPONENT_HUMIDITY)

        if temp_power is None or humid_power is None:
            test_utils.print_func("❌ Failed to get sensor power states after power on")
            all_passed = False
        elif not temp_power or not humid_power:
            test_utils.print_func("❌ Sensors not powered after power on command")
            all_passed = False
        else:
            test_utils.print_func("✅ Sensors powered on successfully")

    # Test power on/off for actuators
    test_utils.print_func("\nTesting power on/off for actuators...")

    # Power off actuators
    if not driver.power_actuators(False, False, False, False):
        test_utils.print_func("❌ Failed to power off actuators")
        all_passed = False
    else:
        # Verify power state
        led_power = driver.get_power_state(COMPONENT_LED)
        fan_power = driver.get_power_state(COMPONENT_FAN)
        heater_power = driver.get_power_state(COMPONENT_HEATER)
        doors_power = driver.get_power_state(COMPONENT_DOORS)

        if (
            led_power is None
            or fan_power is None
            or heater_power is None
            or doors_power is None
        ):
            test_utils.print_func(
                "❌ Failed to get actuator power states after power off"
            )
            all_passed = False
        elif led_power or fan_power or heater_power or doors_power:
            test_utils.print_func("❌ Actuators still powered after power off command")
            all_passed = False
        else:
            test_utils.print_func("✅ Actuators powered off successfully")

    # Power on actuators
    if not driver.power_actuators(True, True, True, True):
        test_utils.print_func("❌ Failed to power on actuators")
        all_passed = False
    else:
        # Verify power state
        led_power = driver.get_power_state(COMPONENT_LED)
        fan_power = driver.get_power_state(COMPONENT_FAN)
        heater_power = driver.get_power_state(COMPONENT_HEATER)
        doors_power = driver.get_power_state(COMPONENT_DOORS)

        if (
            led_power is None
            or fan_power is None
            or heater_power is None
            or doors_power is None
        ):
            test_utils.print_func(
                "❌ Failed to get actuator power states after power on"
            )
            all_passed = False
        elif not led_power or not fan_power or not heater_power or not doors_power:
            test_utils.print_func("❌ Actuators not powered after power on command")
            all_passed = False
        else:
            test_utils.print_func("✅ Actuators powered on successfully")

    if all_passed:
        test_utils.print_func("✅ Power state test passed")
    else:
        test_utils.print_func("❌ Power state test failed")

    return all_passed


def test_error_state(driver, device):
    """Test getting error state for all components."""
    test_utils.print_func("\n=== Testing Error State ===")

    # Get current device memory to check initial state
    device_memory = DeviceMemory()
    if not device.get_memory(device_memory):
        test_utils.print_func("❌ Failed to get device memory")
        return False

    # Test all components
    components = [
        ("Temperature", COMPONENT_TEMPERATURE),
        ("Humidity", COMPONENT_HUMIDITY),
        ("LED", COMPONENT_LED),
        ("Fan", COMPONENT_FAN),
        ("Heater", COMPONENT_HEATER),
        ("Doors", COMPONENT_DOORS),
    ]

    all_passed = True

    # Test getting error state for each component
    for name, component_type in components:
        error_state = driver.get_error_state(component_type)
        if error_state is None:
            test_utils.print_func(f"❌ Failed to get error state for {name}")
            all_passed = False
            continue

        test_utils.print_func(f"{name} error state: {'ERROR' if error_state else 'OK'}")

    # Note: We can't directly set error states as they're read-only
    # In a real system, errors would be set by the device itself

    if all_passed:
        test_utils.print_func("✅ Error state test passed")
    else:
        test_utils.print_func("❌ Error state test failed")

    return all_passed


def test_reset_component(driver, device):
    """Test resetting individual components."""
    test_utils.print_func("\n=== Testing Reset Component ===")

    # Test all components
    components = [
        ("Temperature", COMPONENT_TEMPERATURE),
        ("Humidity", COMPONENT_HUMIDITY),
        ("LED", COMPONENT_LED),
        ("Fan", COMPONENT_FAN),
        ("Heater", COMPONENT_HEATER),
        ("Doors", COMPONENT_DOORS),
    ]

    all_passed = True

    # Test resetting each component individually
    for name, component_type in components:
        test_utils.print_func(f"Resetting {name}...")
        if not driver.reset_component(component_type):
            test_utils.print_func(f"❌ Failed to reset {name}")
            all_passed = False
            continue

        test_utils.print_func(f"✅ {name} reset successfully")

    # Test resetting all sensors at once
    test_utils.print_func("\nTesting reset_sensors function...")
    if not driver.reset_sensors(True, True):
        test_utils.print_func("❌ Failed to reset all sensors")
        all_passed = False
    else:
        test_utils.print_func("✅ All sensors reset successfully")

    # Test resetting all actuators at once
    test_utils.print_func("\nTesting reset_actuators function...")
    if not driver.reset_actuators(True, True, True, True):
        test_utils.print_func("❌ Failed to reset all actuators")
        all_passed = False
    else:
        test_utils.print_func("✅ All actuators reset successfully")

    if all_passed:
        test_utils.print_func("✅ Reset component test passed")
    else:
        test_utils.print_func("❌ Reset component test failed")

    return all_passed


def run_tests(driver, device):
    """Run all component status tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run power state test
    results.append(("Power State", test_power_state(driver, device)))

    # Run error state test
    results.append(("Error State", test_error_state(driver, device)))

    # Run reset component test
    results.append(("Reset Component", test_reset_component(driver, device)))

    # Print summary
    test_utils.print_func("\n=== Component Status Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        test_utils.print_func(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed


def main():
    """Run the test in standalone mode."""
    device, driver = test_utils.setup_test_environment()
    if not device or not driver:
        return 1

    try:
        # Enable prints for standalone test
        test_utils.print_func = print  # Use the real print function

        # Run the tests
        test_utils.print_func("\n=== Running Component Status Tests ===")

        # Run all tests
        power_test_result = test_power_state(driver, device)
        error_test_result = test_error_state(driver, device)
        reset_test_result = test_reset_component(driver, device)

        success = power_test_result and error_test_result and reset_test_result

        # Print overall result
        if success:
            test_utils.print_func("\n✅ All tests passed!")
        else:
            test_utils.print_func("\n❌ Some tests failed!")

        return 0 if success else 1
    finally:
        test_utils.teardown_test_environment(device, driver)


if __name__ == "__main__":
    sys.exit(main())
