#!/usr/bin/env python3
"""
Test runner for Semi-Vibe-Device simulator and driver.
"""

import os
import importlib
import inspect
import sys


def discover_test_modules():
    """Discover all test modules in the tests directory."""
    test_modules = []
    tests_dir = os.path.dirname(os.path.abspath(__file__))

    for filename in os.listdir(tests_dir):
        if (
            filename.startswith("test_")
            and filename.endswith(".py")
            and filename != "test_runner.py"
        ):
            module_name = filename[:-3]  # Remove .py extension
            test_modules.append(module_name)

    return test_modules


def run_all_tests(driver):
    """Run all discovered tests."""
    test_modules = discover_test_modules()
    print(f"\nDiscovered {len(test_modules)} test modules: {', '.join(test_modules)}")

    all_results = []
    all_passed = True

    for module_name in test_modules:
        try:
            # Import the module
            module = importlib.import_module(f"tests.{module_name}")

            # Check if the module has a run_tests function
            if hasattr(module, "run_tests") and inspect.isfunction(module.run_tests):
                print(f"\n\n======== Running tests from {module_name} ========")
                result = module.run_tests(driver)
                all_results.append((module_name, result))
                all_passed = all_passed and result
            else:
                print(f"⚠️ Module {module_name} does not have a run_tests function")
        except Exception as e:
            print(f"❌ Error running tests from {module_name}: {str(e)}")
            all_results.append((module_name, False))
            all_passed = False

    # Print overall summary
    print("\n\n======== OVERALL TEST SUMMARY ========")
    for module_name, result in all_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{module_name}: {status}")

    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\nOverall result: {overall_status}")

    return all_passed
