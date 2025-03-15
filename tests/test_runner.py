#!/usr/bin/env python3
"""
Test runner for Semi-Vibe-Device simulator and driver.
"""

import os
import importlib
import inspect
import sys
import traceback

# Add the tests directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_utils


def discover_test_modules():
    """Discover all test modules in the tests directory."""
    test_modules = []
    tests_dir = os.path.dirname(os.path.abspath(__file__))

    # Find all test modules
    for filename in os.listdir(tests_dir):
        if (
            filename.startswith("test_")
            and filename.endswith(".py")
            and filename != "test_runner.py"
            and filename != "test_utils.py"
            and filename != "test_template.py"
            and filename != "__init__.py"
        ):
            module_name = filename[:-3]  # Remove .py extension
            test_modules.append(module_name)

    # Sort modules alphabetically for consistent execution order
    test_modules.sort()
    return test_modules


def run_all_tests(driver, device=None):
    """Run all discovered tests.

    Args:
        driver: DriverDLL instance
        device: DeviceDLL instance (optional)

    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Set print function to disabled for test modules
    test_utils.set_print_disabled()

    # Disable callback prints for cleaner output
    test_utils.disable_callback_prints()

    test_modules = discover_test_modules()
    print(f"\n=== Found {len(test_modules)} test modules ===")

    results = []

    for module_name in test_modules:
        try:
            # Import the module
            module = importlib.import_module(f"tests.{module_name}")

            # Check if the module has a run_tests function
            if hasattr(module, "run_tests") and inspect.isfunction(module.run_tests):
                print(f"\n=== Running {module_name} ===")

                # Pass both driver and device if the function accepts both
                sig = inspect.signature(module.run_tests)
                if len(sig.parameters) > 1 and device is not None:
                    result = module.run_tests(driver, device)
                else:
                    result = module.run_tests(driver)

                results.append((module_name, result))
            else:
                print(f"⚠️ {module_name} has no run_tests function")
        except Exception as e:
            print(f"[ERROR] Error in {module_name}: {str(e)}")
            traceback.print_exc()
            results.append((module_name, False))

    # Print summary
    print("\n=== TEST SUMMARY ===")
    all_passed = True
    for module_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {module_name}")
        all_passed = all_passed and result

    overall_status = "[ALL TESTS PASSED]" if all_passed else "[SOME TESTS FAILED]"
    print(f"\n{overall_status}\n")

    return all_passed
