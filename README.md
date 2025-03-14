# Semi-Vibe-Device Simulator

A simulator for a fictional device with sensors and actuators, designed for Windows.

## Project Overview

This project simulates a fictional device called Semi-Vibe-Device with sensors and actuators. It consists of two main components:

1. **Device Simulator**: Simulates the physical device with sensors and actuators
2. **Driver**: Provides a high-level API to interact with the device

The project is designed to be extremely minimal, with just two main scripts:
- `build.py`: Builds the project
- `run.py`: Runs integration tests between the device and driver

## Project Structure

- `src/` - C source code
  - `semi_vibe_device.c` - Device simulator implementation
  - `semi_vibe_device.h` - Device simulator header
  - `semi_vibe_driver.c` - Driver implementation
  - `semi_vibe_driver.h` - Driver header
- `python/` - Python support scripts
  - `server.py` - Server script for the device simulator
  - `driver.py` - Python wrapper for the driver
- `build.py` - Build script
- `run.py` - Run script for integration testing

## Building and Running

### Building the Project

To build the project, simply run:

```
python run.py build
```

This will build the project using CMake and place the output in the `build/` directory.

### Running Integration Tests

To run integration tests between the device and driver, simply run:

```
python run.py
```

or

```
python run.py test
```

This will:
1. Start the device simulator in the background
2. Connect to it using the driver
3. Run a series of tests to verify functionality, including:
   - Basic device status and sensor reading
   - Actuator control (LED, fan, heater, doors)
   - Power management
   - Reset functionality
   - Protocol compliance tests (read-only/write-only locations)
   - Reserved bit handling
   - Auto-clearing register behavior
4. Display test results in a clean, organized format
5. Show a detailed communication log with:
   - All commands sent from driver to device
   - All responses sent from device to driver
   - Human-readable descriptions of each command
   - Interpretations of the response values
6. Automatically clean up when done

All output is displayed in a single console window with a clean separation between test results and communication log for a perfect debugging experience.

## Device and Driver Architecture

### Device

The device simulates:
- 2 sensors (temperature and humidity)
- 4 actuators (LED, fan, heater, and doors)

Commands are sent to the device using a simple protocol as defined in the LAW.md file.

### Driver

The driver provides a high-level API to interact with the device:
- Connect/disconnect to the device
- Get device status
- Read sensor data
- Control actuators
- Power management
- Reset functionality

## Requirements

- Windows
- Python 3.6+
- CMake 3.10+
- Visual Studio 2019+ or other C compiler 

## Recent Improvements

### Driver Refactoring

The driver implementation has been refactored to improve code quality and maintainability:

1. **Improved Code Organization**: Introduced a `DriverState` struct to encapsulate global state variables, making the code more modular and easier to maintain.

2. **Command Builder Function**: Added a centralized `build_command` function to eliminate code duplication and standardize command construction.

3. **Enhanced Error Handling**: Improved error handling in the `send_and_receive` function to properly log error responses without treating them as failures.

4. **Protocol Compliance**: Ensured proper handling of protocol restrictions, including read-only registers and reserved bits.

5. **Memory Safety**: Implemented safer buffer handling to prevent potential buffer overflow issues.

6. **Bit Position Constants**: Added named constants for bit positions (e.g., `BIT_LED`, `BIT_FAN`) to improve code readability and maintainability.

7. **Comprehensive Documentation**: Added detailed function documentation with Doxygen-style comments to explain the purpose and parameters of each function.

8. **Improved Logging**: Enhanced logging to include both sent commands and received responses, making debugging easier.

9. **Bitmask Helper Function**: Added a `create_bitmask` helper function to centralize the creation of bitmasks from boolean values, reducing code duplication in power and reset functions.

10. **Protocol Message Struct**: Introduced a `SemiVibeMessage` struct in a new `semi_vibe_protocol.h` file to represent the protocol message format, making the code more elegant and easier to understand. This includes helper functions for parsing, formatting, and creating error messages.

These improvements make the driver more robust, maintainable, and easier to extend with new functionality.

### Code Formatting

Added a comprehensive `.clang-format` configuration with the following features:

1. **Increased Line Length**: Set column limit to 140 characters to allow for more readable code while still maintaining good practices.

2. **Consistent Indentation**: Standardized on 2-space indentation for all code.

3. **Pointer Alignment**: Configured left-aligned pointers (`Type* var`) for consistency.

4. **Brace Style**: Adopted the LLVM-style attached braces for all code blocks.

5. **Include Organization**: Enabled automatic sorting of includes for better organization.

These formatting rules help maintain a consistent code style throughout the project, making it easier to read and maintain. 