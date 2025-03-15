# Semi-Vibe-Device Testing Framework

This directory contains the testing framework for the Semi-Vibe-Device project. The framework is designed to be minimalist and easy to understand.

## Architecture

The testing framework consists of three main components:

1. **Driver Interface**: A Python wrapper that communicates with the device via sockets. It sends commands and receives responses in JSON format.

2. **Simulated Device**: A Python implementation of the device that responds to commands. It maintains an internal state and can be accessed directly for testing.

3. **Testing Framework**: A collection of test modules that verify the functionality of the driver and device.

## Test Structure

Each test module should follow this structure:

```python
def test_something(driver, device=None):
    """Test a specific functionality."""
    # Test implementation
    return True  # or False if the test fails

def run_tests(driver, device=None):
    """Run all tests in this module."""
    results = []
    
    # Run tests
    results.append(("Test Name", test_something(driver, device)))
    
    # Print summary
    print("\n=== Test Summary ===")
    all_passed = True
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        all_passed = all_passed and result
    
    return all_passed
```

## Running Tests

To run all tests:

```bash
python run.py
```

This will:
1. Start the simulated device
2. Initialize the driver and connect to the device
3. Run all test modules
4. Clean up and shut down

## Adding New Tests

To add a new test module:

1. Create a new file named `test_*.py` in the `tests` directory
2. Implement the test functions and the `run_tests` function
3. The test runner will automatically discover and run your tests

## Debugging

The driver and device both log all sent and received messages, making it easy to debug communication issues. Look for lines with `[DRIVER]` and `[DEVICE]` prefixes in the output.

## Direct Access vs Socket Communication

Tests can interact with the device in two ways:

1. **Through the driver** (using sockets): This tests the full communication stack
2. **Directly with the device**: This allows modifying the device state directly for testing

Most tests should use both approaches to verify that the driver correctly communicates with the device. 