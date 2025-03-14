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
3. Run a series of tests to verify functionality
4. Display a detailed communication log showing:
   - All commands sent from driver to device
   - All responses sent from device to driver
   - Human-readable descriptions of each command
   - Interpretations of the response values
5. Automatically clean up when done

All output is displayed in a single console window for a clean, integrated experience.

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