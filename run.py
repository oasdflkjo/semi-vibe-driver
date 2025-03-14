#!/usr/bin/env python3
"""
Run script for Semi-Vibe-Device simulator and driver.
This script provides simple commands to build, test, and run the system.
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path


def is_server_ready(host="localhost", port=8989, max_attempts=10):
    """Check if the server is ready to accept connections."""
    print(f"Checking if server is ready on {host}:{port}...")

    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                print(f"Server is ready after {attempt + 1} attempts!")
                return True
        except (ConnectionRefusedError, socket.timeout):
            print(f"Server not ready yet (attempt {attempt + 1}/{max_attempts})...")
            time.sleep(1)

    print(f"Server did not become ready after {max_attempts} attempts")
    return False


def check_build():
    """Check if the project is built and return True if it is."""
    if not (
        Path("build/bin/Debug/semi_vibe_device.dll").exists()
        or Path("build/bin/semi_vibe_device.dll").exists()
    ):
        print("Error: Device DLL not found. Run 'python run.py build' first.")
        return False

    if not (
        Path("build/bin/Debug/semi_vibe_driver.dll").exists()
        or Path("build/bin/semi_vibe_driver.dll").exists()
    ):
        print("Error: Driver DLL not found. Run 'python run.py build' first.")
        return False

    return True


def build_project():
    """Build the project using the build.py script."""
    print("Building the project...")
    result = subprocess.run([sys.executable, "build.py"])
    if result.returncode != 0:
        print("Build failed.")
        return False
    print("Build completed successfully.")
    return True


def run_integration_test():
    """Run integration tests with both device and driver."""
    if not check_build():
        return 1

    print("\nRunning integration test...")
    print("==========================")

    # Start the server in a new window
    print("Starting device server...")
    server = subprocess.Popen(
        [sys.executable, "python/server.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    # Wait for server to start
    if not is_server_ready():
        print("Server failed to start properly.")
        return 1

    # Import the driver module
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python"))
    from driver import Driver

    # Run driver tests
    print("\nRunning driver tests...")

    driver = Driver()
    if not driver.init():
        print("Failed to initialize driver")
        return 1

    if not driver.connect("localhost"):
        print("Failed to connect to device")
        return 1

    try:
        # Get device status
        status = driver.get_status()
        if not status:
            print("Failed to get device status")
            return 1

        print("\nDevice status:")
        print(f"  Connected: {status['connected']}")
        print(f"  Sensors powered: {status['sensors_powered']}")
        print(f"  Actuators powered: {status['actuators_powered']}")
        print(f"  Has errors: {status['has_errors']}")

        # Get sensor data
        sensors = driver.get_sensors()
        if not sensors:
            print("Failed to get sensor data")
            return 1

        print("\nSensor data:")
        print(f"  Temperature ID: 0x{sensors['temperature_id']:02X}")
        print(f"  Temperature value: {sensors['temperature_value']}")
        print(f"  Humidity ID: 0x{sensors['humidity_id']:02X}")
        print(f"  Humidity value: {sensors['humidity_value']}")

        # Get actuator data
        actuators = driver.get_actuators()
        if not actuators:
            print("Failed to get actuator data")
            return 1

        print("\nActuator data:")
        print(f"  LED value: {actuators['led_value']}")
        print(f"  Fan value: {actuators['fan_value']}")
        print(f"  Heater value: {actuators['heater_value']}")
        print(f"  Doors value: 0x{actuators['doors_value']:02X}")

        # Test setting actuator values
        print("\nTesting actuator control...")

        print("Setting LED to 128...")
        if not driver.set_led(128):
            print("Failed to set LED value")
            return 1

        print("Setting fan to 200...")
        if not driver.set_fan(200):
            print("Failed to set fan value")
            return 1

        print("Setting heater to 10...")
        if not driver.set_heater(10):
            print("Failed to set heater value")
            return 1

        print("Setting doors to 0x55...")
        if not driver.set_doors(0x55):
            print("Failed to set doors value")
            return 1

        # Get updated actuator data
        actuators = driver.get_actuators()
        if not actuators:
            print("Failed to get updated actuator data")
            return 1

        print("\nUpdated actuator data:")
        print(f"  LED value: {actuators['led_value']}")
        print(f"  Fan value: {actuators['fan_value']}")
        print(f"  Heater value: {actuators['heater_value']}")
        print(f"  Doors value: 0x{actuators['doors_value']:02X}")

        # Test power control
        print("\nTesting power control...")

        print("Powering off all actuators...")
        if not driver.power_actuators(False, False, False, False):
            print("Failed to power off actuators")
            return 1

        # Get updated status
        status = driver.get_status()
        if not status:
            print("Failed to get updated status")
            return 1

        print("Updated device status:")
        print(f"  Actuators powered: {status['actuators_powered']}")

        # Power actuators back on
        print("Powering actuators back on...")
        if not driver.power_actuators(True, True, True, True):
            print("Failed to power on actuators")
            return 1

        # Test reset
        print("\nTesting reset...")

        print("Resetting all actuators...")
        if not driver.reset_actuators(True, True, True, True):
            print("Failed to reset actuators")
            return 1

        # Get updated actuator data after reset
        actuators = driver.get_actuators()
        if not actuators:
            print("Failed to get actuator data after reset")
            return 1

        print("Actuator data after reset:")
        print(f"  LED value: {actuators['led_value']}")
        print(f"  Fan value: {actuators['fan_value']}")
        print(f"  Heater value: {actuators['heater_value']}")
        print(f"  Doors value: 0x{actuators['doors_value']:02X}")

        print("\nAll tests completed successfully!")
        return 0
    finally:
        # Always disconnect from device
        print("\nDisconnecting from device...")
        driver.disconnect()

        # Terminate the server
        print("Stopping server...")
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Server did not terminate gracefully, forcing termination...")
            server.kill()
        print("Server stopped.")


def main():
    """Main function."""
    # Handle commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "build":
            # Build the project
            if build_project():
                return 0
            else:
                return 1

        elif cmd == "test":
            # Run the integration test
            return run_integration_test()

        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python run.py [build|test]")
    else:
        # Default to running the integration test if no command is provided
        if not check_build():
            print("Please build the project first with: python run.py build")
            return 1

        return run_integration_test()

    return 0


if __name__ == "__main__":
    sys.exit(main())
