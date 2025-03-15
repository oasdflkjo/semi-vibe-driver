# Semi-Vibe-Device Testing Framework

This directory contains the unified testing framework for the Semi-Vibe-Device simulator and driver.

## Overview

The testing framework is designed to be modular and extensible. It consists of:

1. A test runner (`test_runner.py`) that discovers and runs all test modules
2. Individual test modules for different device functionalities

## Test Structure

Each test module should:

1. Be named with a `test_` prefix (e.g., `test_sensors.py`, `test_actuators.py`)
2. Contain individual test functions that accept a `driver` parameter
3. Include a `run_tests(driver)` function that runs all tests in the module and returns a boolean result

## Adding New Tests

To add a new test module:

1. Create a new Python file with a `test_` prefix in the `tests` directory
2. Implement individual test functions that accept a `driver` parameter
3. Implement a `run_tests(driver)` function that runs all tests and returns a boolean result

### Example Test Module

```python
#!/usr/bin/env python3
"""
Test cases for a specific functionality.
"""

def test_feature_one(driver):
    """Test a specific feature."""
    print("\n=== Testing Feature One ===")
    
    # Test implementation
    # ...
    
    print("✅ Feature one test passed")
    return True


def test_feature_two(driver):
    """Test another feature."""
    print("\n=== Testing Feature Two ===")
    
    # Test implementation
    # ...
    
    print("✅ Feature two test passed")
    return True


def run_tests(driver):
    """Run all tests in this module."""
    results = []
    
    # Run tests
    results.append(("Feature One", test_feature_one(driver)))
    results.append(("Feature Two", test_feature_two(driver)))
    
    # Print summary
    print("\n=== Module Tests Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result
    
    return all_passed
```

## Running Tests

Tests are automatically discovered and run by the main `run.py` script:

```
python run.py test
```

This will:

1. Start the device server
2. Initialize the driver
3. Connect to the device
4. Perform basic device tests
5. Run all discovered test modules
6. Display a communication log and test summary 