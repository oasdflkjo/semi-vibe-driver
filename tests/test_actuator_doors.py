#!/usr/bin/env python3
"""
Test cases for doors actuator functionality.
"""

import sys
import os
import ctypes

# Add the python directory to the path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "python")
)
from driver import DOOR_1, DOOR_2, DOOR_3, DOOR_4, DOOR_OPEN, DOOR_CLOSED
import test_utils


def test_doors_api(driver):
    """Test doors control using the new door API."""
    test_utils.print_func("\n=== Testing Doors Control (New API) ===")

    # Define all doors
    doors = [DOOR_1, DOOR_2, DOOR_3, DOOR_4]
    door_names = ["Door 1", "Door 2", "Door 3", "Door 4"]

    # Get initial door states
    initial_states = {}
    for door_id, door_name in zip(doors, door_names):
        state = driver.get_door_state(door_id)
        if state is None:
            test_utils.print_func(f"❌ Failed to get initial state of {door_name}")
            return False
        initial_states[door_id] = state
        state_name = "OPEN" if state == DOOR_OPEN else "CLOSED"
        test_utils.print_func(f"Initial state of {door_name}: {state_name}")

    # Test all 16 possible door configurations
    test_utils.print_func(f"Testing all 16 possible door configurations...")
    all_passed = True

    # Generate all 16 possible configurations (2^4 = 16)
    for config_num in range(16):
        # Convert configuration number to door states
        door_states = {
            DOOR_1: DOOR_OPEN if (config_num & 1) else DOOR_CLOSED,
            DOOR_2: DOOR_OPEN if (config_num & 2) else DOOR_CLOSED,
            DOOR_3: DOOR_OPEN if (config_num & 4) else DOOR_CLOSED,
            DOOR_4: DOOR_OPEN if (config_num & 8) else DOOR_CLOSED,
        }

        # Print the configuration
        config_desc = ", ".join(
            [
                f"Door {i+1}: {'OPEN' if door_states[doors[i]] == DOOR_OPEN else 'CLOSED'}"
                for i in range(4)
            ]
        )
        test_utils.print_func(f"\nTesting configuration {config_num}: {config_desc}")

        # Set each door state individually using the door API
        for door_id in doors:
            state = door_states[door_id]
            if not driver.set_door(door_id, state):
                test_utils.print_func(
                    f"❌ Failed to set Door {door_id} to {'OPEN' if state == DOOR_OPEN else 'CLOSED'}"
                )
                all_passed = False
                continue

        # Verify all door states individually using the door API
        for door_id, door_name in zip(doors, door_names):
            expected_state = door_states[door_id]
            actual_state = driver.get_door_state(door_id)

            if actual_state is None:
                test_utils.print_func(f"❌ Failed to get state of {door_name}")
                all_passed = False
                continue

            if actual_state != expected_state:
                expected_name = "OPEN" if expected_state == DOOR_OPEN else "CLOSED"
                actual_name = "OPEN" if actual_state == DOOR_OPEN else "CLOSED"
                test_utils.print_func(
                    f"❌ {door_name} state mismatch: expected {expected_name}, got {actual_name}"
                )
                all_passed = False
                continue

        test_utils.print_func(f"✅ Verified configuration {config_num}")

    # Reset doors to initial states
    test_utils.print_func(f"\nResetting doors to initial states...")
    for door_id, door_name in zip(doors, door_names):
        if not driver.set_door(door_id, initial_states[door_id]):
            test_utils.print_func(f"❌ Failed to reset {door_name} to initial state")
            all_passed = False
            continue

        # Verify reset
        state = driver.get_door_state(door_id)
        if state is None:
            test_utils.print_func(f"❌ Failed to get state of {door_name} after reset")
            all_passed = False
            continue

        if state != initial_states[door_id]:
            expected_name = "OPEN" if initial_states[door_id] == DOOR_OPEN else "CLOSED"
            actual_name = "OPEN" if state == DOOR_OPEN else "CLOSED"
            test_utils.print_func(
                f"❌ {door_name} state mismatch after reset: expected {expected_name}, got {actual_name}"
            )
            all_passed = False
            continue

        state_name = "OPEN" if state == DOOR_OPEN else "CLOSED"
        test_utils.print_func(f"✅ Reset {door_name} to {state_name}")

    if all_passed:
        test_utils.print_func(f"✅ Doors test passed for all 16 configurations")
    else:
        test_utils.print_func(f"❌ Doors test failed")

    return all_passed


def run_tests(driver):
    """Run all doors tests."""
    # When running as part of the test suite, disable print
    test_utils.set_print_disabled()

    results = []

    # Run doors test with the new API
    results.append(("Doors Control", test_doors_api(driver)))

    # Print summary
    test_utils.print_func("\n=== Doors Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        test_utils.print_func(f"{name}: {status}")
        all_passed = all_passed and result

    return all_passed


def main():
    """Run the test in standalone mode."""
    return test_utils.run_standalone_test(test_doors_api)


if __name__ == "__main__":
    sys.exit(main())
