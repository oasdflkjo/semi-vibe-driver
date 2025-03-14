# Semi-Vibe-Device Simulator

A simulator for a fictional device with sensors and actuators, designed for Windows.

## Project Structure

- `src/` - C source code for the device simulator
  - `semi_vibe_device.c` - Main implementation of the device simulator
  - `semi_vibe_device.h` - Header file with device definitions
- `test/` - Test code
  - `test_device.c` - C test program for the device
- `python/` - Python scripts
  - `server.py` - Server script that loads the DLL and starts the device server
  - `test_device.py` - Python test script for the device DLL
  - `socket_test.py` - Socket test script for the device
- `build.py` - Simple build script
- `run.py` - Simple run script

## Building the Project

### Using the build script

```
python build.py
```

This will build the project using CMake and place the output in the `build/` directory.

To clean the build:

```
python build.py clean
```

### Manual Build

1. Create a build directory:
   ```
   mkdir build
   cd build
   ```

2. Configure with CMake:
   ```
   cmake ..
   ```

3. Build:
   ```
   cmake --build .
   ```

## Running the Project

### Using the run script

```
python run.py server  # Run the server only
python run.py client  # Run the client only
python run.py both    # Run both server and client
```

When running both server and client, the server will start in a separate window. You'll need to close this window manually when done.

### Manual Running

#### Running the C test program

```
build/bin/Debug/test_device.exe
```

#### Running the Python server

```
python python/server.py
```

#### Running the Python client

```
python python/socket_test.py
```

## Device Specification

The device simulates:
- 2 sensors (temperature and humidity)
- 4 actuators (LED, fan, heater, and doors)

Commands are sent to the device using a simple protocol as defined in the LAW.md file.

## Requirements

- Windows
- Python 3.6+
- CMake 3.10+
- Visual Studio 2019+ or other C compiler 