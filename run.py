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
import re
from pathlib import Path
import threading
import queue


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


def get_command_description(command, response):
    """Get a description of what a command does based on its format."""
    if not command or len(command) < 6:
        return "Unknown command", "Unknown response"

    base_addr = int(command[0], 16)
    offset = command[1:3]
    rw = int(command[3], 16)
    data = command[4:6]

    # Initialize response interpretation
    response_interpretation = ""

    # Determine the command type based on base address
    if base_addr == 1:  # MAIN
        if offset == "00":
            cmd_desc = "Read connected device status"
            if response:
                resp_val = int(response[4:6], 16)
                connected = []
                if resp_val & 0x80:
                    connected.append("Door")
                if resp_val & 0x40:
                    connected.append("Heater")
                if resp_val & 0x20:
                    connected.append("Fan")
                if resp_val & 0x10:
                    connected.append("LED")
                if resp_val & 0x02:
                    connected.append("Humidity")
                if resp_val & 0x01:
                    connected.append("Temperature")
                response_interpretation = f"Connected: {', '.join(connected)}"
        elif offset == "02":
            cmd_desc = "Read power state"
            if response:
                resp_val = int(response[4:6], 16)
                powered = []
                if resp_val & 0x80:
                    powered.append("Door")
                if resp_val & 0x40:
                    powered.append("Heater")
                if resp_val & 0x20:
                    powered.append("Fan")
                if resp_val & 0x10:
                    powered.append("LED")
                if resp_val & 0x02:
                    powered.append("Humidity")
                if resp_val & 0x01:
                    powered.append("Temperature")
                response_interpretation = f"Powered: {', '.join(powered)}"
        elif offset == "03":
            cmd_desc = "Read error state"
            if response:
                resp_val = int(response[4:6], 16)
                errors = []
                if resp_val & 0x80:
                    errors.append("Door")
                if resp_val & 0x40:
                    errors.append("Heater")
                if resp_val & 0x20:
                    errors.append("Fan")
                if resp_val & 0x10:
                    errors.append("LED")
                if resp_val & 0x02:
                    errors.append("Humidity")
                if resp_val & 0x01:
                    errors.append("Temperature")
                if errors:
                    response_interpretation = f"Errors in: {', '.join(errors)}"
                else:
                    response_interpretation = "No errors"
    elif base_addr == 2:  # SENSOR
        if offset == "10":
            cmd_desc = "Read temperature sensor ID"
            if response:
                resp_val = int(response[4:6], 16)
                response_interpretation = f"Temperature ID: 0x{resp_val:02X}"
        elif offset == "11":
            cmd_desc = "Read temperature value"
            if response:
                resp_val = int(response[4:6], 16)
                response_interpretation = f"Temperature: {resp_val} units"
        elif offset == "20":
            cmd_desc = "Read humidity sensor ID"
            if response:
                resp_val = int(response[4:6], 16)
                response_interpretation = f"Humidity ID: 0x{resp_val:02X}"
        elif offset == "21":
            cmd_desc = "Read humidity value"
            if response:
                resp_val = int(response[4:6], 16)
                response_interpretation = f"Humidity: {resp_val} units"
    elif base_addr == 3:  # ACTUATOR
        if offset == "10":
            if rw == 0:
                cmd_desc = "Read LED value"
                if response:
                    resp_val = int(response[4:6], 16)
                    response_interpretation = f"LED brightness: {resp_val}/255"
            else:
                cmd_desc = f"Set LED value to 0x{data}"
                response_interpretation = "Command acknowledged"
        elif offset == "20":
            if rw == 0:
                cmd_desc = "Read fan value"
                if response:
                    resp_val = int(response[4:6], 16)
                    response_interpretation = f"Fan speed: {resp_val}/255"
            else:
                cmd_desc = f"Set fan value to 0x{data}"
                response_interpretation = "Command acknowledged"
        elif offset == "30":
            if rw == 0:
                cmd_desc = "Read heater value"
                if response:
                    resp_val = int(response[4:6], 16)
                    response_interpretation = f"Heater level: {resp_val}/15"
            else:
                cmd_desc = f"Set heater value to 0x{data}"
                response_interpretation = "Command acknowledged"
        elif offset == "40":
            if rw == 0:
                cmd_desc = "Read doors value"
                if response:
                    resp_val = int(response[4:6], 16)
                    doors = []
                    if resp_val & 0x01:
                        doors.append("Door 1 closed")
                    if resp_val & 0x04:
                        doors.append("Door 2 closed")
                    if resp_val & 0x10:
                        doors.append("Door 3 closed")
                    if resp_val & 0x40:
                        doors.append("Door 4 closed")
                    if doors:
                        response_interpretation = f"Doors: {', '.join(doors)}"
                    else:
                        response_interpretation = "All doors open"
            else:
                cmd_desc = f"Set doors value to 0x{data}"
                response_interpretation = "Command acknowledged"
    elif base_addr == 4:  # CONTROL
        if offset == "FB":
            if rw == 0:
                cmd_desc = "Read sensor power state"
                if response:
                    resp_val = int(response[4:6], 16)
                    sensors = []
                    if resp_val & 0x01:
                        sensors.append("Temperature")
                    if resp_val & 0x04:
                        sensors.append("Humidity")
                    if sensors:
                        response_interpretation = (
                            f"Powered sensors: {', '.join(sensors)}"
                        )
                    else:
                        response_interpretation = "All sensors off"
            else:
                cmd_desc = f"Set sensor power state to 0x{data}"
                response_interpretation = "Command acknowledged"
        elif offset == "FC":
            if rw == 0:
                cmd_desc = "Read actuator power state"
                if response:
                    resp_val = int(response[4:6], 16)
                    actuators = []
                    if resp_val & 0x01:
                        actuators.append("LED")
                    if resp_val & 0x04:
                        actuators.append("Fan")
                    if resp_val & 0x10:
                        actuators.append("Heater")
                    if resp_val & 0x40:
                        actuators.append("Doors")
                    if actuators:
                        response_interpretation = (
                            f"Powered actuators: {', '.join(actuators)}"
                        )
                    else:
                        response_interpretation = "All actuators off"
            else:
                cmd_desc = f"Set actuator power state to 0x{data}"
                response_interpretation = "Command acknowledged"
        elif offset == "FD":
            if rw == 0:
                cmd_desc = "Read sensor reset state"
                response_interpretation = "Reset state read"
            else:
                cmd_desc = f"Reset sensors with mask 0x{data}"
                response_interpretation = "Sensors reset"
        elif offset == "FE":
            if rw == 0:
                cmd_desc = "Read actuator reset state"
                response_interpretation = "Reset state read"
            else:
                cmd_desc = f"Reset actuators with mask 0x{data}"
                response_interpretation = "Actuators reset"
    else:
        cmd_desc = "Unknown command"
        response_interpretation = "Unknown response"

    return cmd_desc, response_interpretation


def display_communication_entry(comm):
    """Display a single communication entry in a nice format."""
    cmd_desc, resp_desc = comm["description"]
    print(
        f"SENT: {comm['driver_sent']:^13}  | RECEIVED: {comm['device_received']:^10} | {cmd_desc}"
    )
    print(
        f"RECEIVED: {comm['driver_received']:^9}  | SENT: {comm['device_sent']:^14} | {resp_desc}"
    )
    print(f"{'-'*20} | {'-'*20} | {'-'*50}")


def display_communication(communications):
    """Display the communication in a nice format."""
    print("\n======== COMMUNICATION LOG ========")
    print(f"{'DRIVER':^20} | {'DEVICE':^20} | {'DESCRIPTION'}")
    print(f"{'-'*21}|{'-'*22}|{'-'*50}")

    for comm in communications:
        display_communication_entry(comm)


def process_server_output(output_queue, communications):
    """Process server output in real-time and extract communication details."""
    received_cmd = None

    # Regular expressions to match the relevant log lines
    received_pattern = re.compile(r"\[DEVICE\] Received: (\w+)")
    sent_pattern = re.compile(r"\[DEVICE\] Sent response: (\w+)")

    while True:
        try:
            line = output_queue.get(timeout=0.1)
            if line is None:  # None is our signal to exit
                break

            # Don't print server output to console - just process it silently
            # Process the line to extract communication details
            received_match = received_pattern.search(line)
            if received_match:
                received_cmd = received_match.group(1)
                continue

            sent_match = sent_pattern.search(line)
            if sent_match and received_cmd:
                sent_response = sent_match.group(1)
                communications.append(
                    {
                        "driver_sent": received_cmd,
                        "device_received": received_cmd,
                        "device_sent": sent_response,
                        "driver_received": sent_response,
                        "description": get_command_description(
                            received_cmd, sent_response
                        ),
                    }
                )
                received_cmd = None  # Reset for the next command

        except queue.Empty:
            continue


def read_output(pipe, queue):
    """Read output from a pipe and put it in a queue."""
    for line in iter(pipe.readline, b""):
        queue.put(line.decode("utf-8").strip())
    queue.put(None)  # Signal that we're done


def run_integration_test():
    """Run integration tests with both device and driver."""
    if not check_build():
        return 1

    print("\nRunning integration test...")
    print("==========================")

    # Start the server in a separate process with pipes for stdout/stderr
    print("Starting device server...")

    # On Windows, we need to use CREATE_NO_WINDOW flag to prevent a console window
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    server = subprocess.Popen(
        [sys.executable, "python/server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        startupinfo=startupinfo,
        bufsize=1,  # Line buffered
        universal_newlines=False,  # Binary mode
    )

    # Create a queue for the server output
    output_queue = queue.Queue()

    # Create a list to store communication details
    communications = []

    # Start a thread to read the server output
    output_thread = threading.Thread(
        target=read_output, args=(server.stdout, output_queue)
    )
    output_thread.daemon = True
    output_thread.start()

    # Start a thread to process the server output
    process_thread = threading.Thread(
        target=process_server_output, args=(output_queue, communications)
    )
    process_thread.daemon = True
    process_thread.start()

    # Wait for server to start
    if not is_server_ready():
        print("Server failed to start properly.")
        server.terminate()
        return 1

    # Import the driver module
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python"))
    from driver import Driver

    # Run driver tests
    print("\nRunning driver tests...")

    driver = Driver()
    if not driver.init():
        print("Failed to initialize driver")
        server.terminate()
        return 1

    if not driver.connect("localhost"):
        print("Failed to connect to device")
        server.terminate()
        return 1

    try:
        # Get device status
        status = driver.get_status()
        if not status:
            print("Failed to get device status")
            return 1

        print("\n======== TEST RESULTS ========")
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

        # Additional tests for read-only and write-only locations
        print("\n======== ADDITIONAL TESTS ========")

        # Test 1: Writing to read-only locations (MAIN and SENSOR)
        print("\nTesting writing to read-only locations...")

        print("Attempting to write to MAIN register (should fail)...")
        response = driver.send_command("102101")  # Try to write to power_state register
        print(f"  Response: {response}")
        print("  Expected: Error response or failure")

        print("Attempting to write to SENSOR register (should fail)...")
        response = driver.send_command("210101")  # Try to write to sensor_a_id register
        print(f"  Response: {response}")
        print("  Expected: Error response or failure")

        # Test 2: Writing to registers with reserved bits
        print("\nTesting writing to registers with reserved bits...")

        print("Writing 0xFF to heater (only lower 4 bits should be set)...")
        driver.set_heater(0xFF)  # Try to set all bits, but only lower 4 should be set
        actuators = driver.get_actuators()
        print(f"  Heater value after write: {actuators['heater_value']}")
        print("  Expected: 15 (0x0F) - only lower 4 bits should be set")

        print("Writing 0xFF to doors (only specific bits should be set)...")
        driver.set_doors(
            0xFF
        )  # Try to set all bits, but only specific bits should be set
        actuators = driver.get_actuators()
        print(f"  Doors value after write: 0x{actuators['doors_value']:02X}")
        print("  Expected: 0x55 - only bits 0, 2, 4, 6 should be set")

        # Test 3: Testing reset register behavior
        print("\nTesting reset register behavior...")

        # First, set some values to the actuators
        driver.set_led(200)
        driver.set_fan(150)

        # Reset only LED and fan
        print("Resetting only LED and fan...")
        driver.reset_actuators(True, True, False, False)

        # Check if only LED and fan are reset
        actuators = driver.get_actuators()
        print("Actuator values after partial reset:")
        print(f"  LED value: {actuators['led_value']} (Expected: 0)")
        print(f"  Fan value: {actuators['fan_value']} (Expected: 0)")
        print(f"  Heater value: {actuators['heater_value']} (Expected: unchanged)")
        print(f"  Doors value: 0x{actuators['doors_value']:02X} (Expected: unchanged)")

        # Check if reset register cleared itself
        print("Checking if reset register cleared itself...")
        response = driver.send_command("4FE000")  # Read reset_actuators register
        print(f"  Reset register value: {response}")
        print(
            "  Expected: Value with all bits cleared (reset register should auto-clear)"
        )

        print("\nAll additional tests completed!")

        # Disconnect from device
        print("\nDisconnecting from device...")
        driver.disconnect()

        # Now display the communication log
        if communications:
            display_communication(communications)

        return 0
    finally:
        # Terminate the server
        print("Stopping server...")
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Server did not terminate gracefully, forcing termination...")
            server.kill()

        # Wait for the output thread to finish
        output_thread.join(timeout=2)
        process_thread.join(timeout=2)

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
