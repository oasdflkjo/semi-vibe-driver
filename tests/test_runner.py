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

    return test_modules


def run_all_tests(driver, device=None):
    """Run all discovered tests."""
    test_modules = discover_test_modules()
    print(f"\n=== Found {len(test_modules)} test modules ===")

    # Define the order of test execution
    ordered_modules = []

    # Basic tests first
    if "test_basic" in test_modules:
        ordered_modules.append("test_basic")
        test_modules.remove("test_basic")

    # Sensor tests next
    sensor_tests = [m for m in test_modules if "sensor" in m]
    for module in sensor_tests:
        ordered_modules.append(module)
        test_modules.remove(module)

    # Actuator tests last
    actuator_tests = [
        m
        for m in test_modules
        if m in ["test_led", "test_fan", "test_heater", "test_doors"]
    ]
    for module in actuator_tests:
        ordered_modules.append(module)
        if module in test_modules:
            test_modules.remove(module)

    # Add any remaining tests
    ordered_modules.extend(test_modules)

    all_results = []
    all_passed = True

    for module_name in ordered_modules:
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
