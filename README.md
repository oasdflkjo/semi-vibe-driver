# Semi-Vibe-Driver

## Overview

Semi-Vibe-Driver is a software library developed by Semi-Vibe Technologies, Inc. for interfacing with Semi-Vibe-Device hardware. This driver provides a comprehensive API for controlling and monitoring all aspects of the Semi-Vibe-Device.

## Features

- Complete control of all device actuators (LED, fan, heater, doors)
- Real-time monitoring of all device sensors (temperature, humidity)
- Comprehensive error handling and reporting
- Thread-safe implementation for multi-threaded applications
- Memory-safe implementation with robust bounds checking
- Detailed logging capabilities

## License

This software is licensed under the MIT License with Attribution Requirement. This means you are free to use, modify, and distribute the software, provided you include the original copyright notice and an acknowledgment of Semi-Vibe Technologies, Inc. in your product. See LICENSE.md for the full license text.

## Requirements

- Windows 10 or later
- C99-compatible compiler
- WinSock2 library

## Usage

The Semi-Vibe-Driver is designed to be integrated into applications that need to interface with Semi-Vibe-Device hardware. The driver provides a simple, intuitive API for controlling all aspects of the device.

### Basic Usage Example

```c
#include "semi_vibe_driver.h"
#include <stdio.h>

void log_callback(const char *message) {
    printf("Driver: %s\n", message);
}

int main() {
    // Initialize the driver
    if (!driver_init(log_callback)) {
        printf("Failed to initialize driver\n");
        return 1;
    }
    
    // Connect to the device
    if (!driver_connect("localhost", 8989)) {
        printf("Failed to connect to device\n");
        return 1;
    }
    
    // Set LED brightness to 50%
    driver_set_led(128);
    
    // Turn on the fan at full speed
    driver_set_fan(255);
    
    // Read temperature
    uint8_t temperature;
    if (driver_get_temperature(&temperature)) {
        printf("Temperature: %d\n", temperature);
    }
    
    // Disconnect from the device
    driver_disconnect();
    
    return 0;
}
```

## Contact

For licensing inquiries or technical support, please contact:

Semi-Vibe Technologies, Inc.  
Email: support@semi-vibe-tech.com  
Website: https://www.semi-vibe-tech.com

## Legal Notice

© 2024 Semi-Vibe Technologies, Inc. All Rights Reserved.

This software is licensed under the MIT License with Attribution Requirement. 
See LICENSE.md for the full license text.

# Semi-Vibe-Driver Project

![example workflow](https://github.com/oasdflkjo/semi-vibe-driver/actions/workflows/build-and-test.yml/badge.svg)

## Project Overview

The Semi-Vibe-Driver project is a driver development framework designed to simulate and test device drivers for embedded systems. This project demonstrates an architecture for driver development, with a focus on testability and iterative development using LLM-assisted coding techniques.

## Architecture

The project is structured in multiple layers, creating a comprehensive testing and development environment:

```
┌─────────────────────────────────┐
│       Integration Tests         │
├─────────────────────────────────┤
│     Custom Testing Framework    │
├─────────────────────────────────┤
│        Python Wrappers          │
├─────────────────────────────────┤
│ C Base Layer (Driver & Device)  │
└─────────────────────────────────┘
```

### 1. C Base Layer

The foundation of the project is written in C and consists of two main components:

- **Device DLL (`semi_vibe_device.dll`)**: Simulates a hardware device with sensors (temperature, humidity) and actuators (LED, fan, heater, doors).
- **Driver DLL (`semi_vibe_driver.dll`)**: Provides the interface to communicate with the device using a defined protocol.

These components are compiled into separate DLLs using CMake, allowing them to be loaded dynamically by the higher layers.

### 2. Python Wrappers

Python wrappers provide a high-level interface to the C-based DLLs:

- **Device Wrapper (`device.py`)**: Wraps the device DLL, providing a Python interface to the simulated hardware.
- **Driver Wrapper (`driver.py`)**: Wraps the driver DLL, allowing Python code to interact with the driver.

These wrappers use `ctypes` to load and interact with the DLLs, exposing their functionality through Pythonic interfaces.

### 3. Custom Testing Framework

A handmade testing framework (`test_runner.py`) provides:

- Automatic test discovery
- Consistent test execution
- Result reporting
- Direct access to both driver and device for comprehensive testing

### 4. Testing Application

The top layer is a testing application (`run_tests.py`) that:

- Initializes the device and driver
- Establishes connections
- Runs the test suite
- Reports results
- Handles cleanup

## Protocol

The communication between the driver and device uses a custom protocol defined in `semi_vibe_protocol.h`. This protocol:

- Uses a register-based approach with base addresses and offsets
- Supports read and write operations
- Enables control and monitoring of various device components

## Conclusion

The Semi-Vibe-Driver project demonstrates a approach to driver development that leverages comprehensive testing and LLM-assisted coding. This methodology enables rapid development, making it an template framework for similar embedded systems projects.

Altough the project goal was to create a driver for a imaginary device, the framework that was used is more valuable that the specific implementation of the driver. 

My current view on unit tests and integration tests in embedded systems is a bit wonky, I prefer much more integration tests over unit tests. 
That way testing does not affect that acrchitectual decisions and at least reduces the amount of abstraction layers needed. Every codebase will have bugs and statistically having less code means less bugs.

## CI/CD with GitHub Actions

This project uses GitHub Actions for continuous integration and delivery:

### Build and Test Workflow

The [build-and-test.yml](.github/workflows/build-and-test.yml) workflow runs on every push to main branches and pull requests:

- Builds the driver and device DLLs in a Windows environment
- Runs the full test suite
- Creates artifacts containing header files and DLLs
- Updates status badges in the README

### Release Workflow

The [release.yml](.github/workflows/release.yml) workflow is triggered when a tag is pushed:

- Builds the driver and device DLLs in Release mode
- Runs the full test suite
- Creates a ZIP archive with headers, DLLs, and library files
- Creates a GitHub Release with the ZIP file attached

### Creating a Release

To create a new release:

```bash
# Tag the commit
git tag v1.0.0

# Push the tag to trigger the release workflow
git push origin v1.0.0
```

The release will be automatically created with the built artifacts.


