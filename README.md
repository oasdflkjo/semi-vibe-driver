# Semi-Vibe-Driver Project

[![Build and Test Status](https://github.com/oasdflkjo/semi-vibe-driver/actions/workflows/build-and-test.yml/badge.svg?branch=master&event=build-status)](https://github.com/oasdflkjo/semi-vibe-driver/actions/workflows/build-and-test.yml)

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

The top layer is a testing application (`run.py`) that:

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

## Development Methodology

This project was developed using an LLM-assisted approach with Claude 3.7.

The architecture was specifically selected to allow an LLM to edit and improve the code while maintaining a stable testing environment. This approach enables:

- Rapid prototyping
- Continuous validation against integration tests
- Maintaining overall system stability during development

## Conclusion

The Semi-Vibe-Driver project demonstrates a approach to driver development that leverages comprehensive testing and LLM-assisted coding. This methodology enables rapid development, making it an template framework for similar embedded systems projects.

Altough the project goal was to create a driver for a imaginary device, the framework that was used is more valuable that the specific implementation of the driver. 

My current view on unit tests and integration tests in embedded systems is a bit wonky, i prefer much more integration tests over unit tests. 
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


