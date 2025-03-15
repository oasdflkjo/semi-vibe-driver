#!/usr/bin/env python3
"""
Test runner for Semi-Vibe-Device simulator and driver.
"""

import os
import importlib
import inspect


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
    test_modules = discover_test_modules()
    print(f"\n=== Found {len(test_modules)} test modules ===")

    all_results = []
    all_passed = True

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

                all_results.append((module_name, result))
                all_passed = all_passed and result
            else:
                print(f"⚠️ {module_name} has no run_tests function")
        except Exception as e:
            print(f"❌ Error in {module_name}: {str(e)}")
            all_results.append((module_name, False))
            all_passed = False

    # Print overall summary
    print("\n=== TEST SUMMARY ===")
    for module_name, result in all_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {module_name}")

    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\n{overall_status}")

    return all_passed
