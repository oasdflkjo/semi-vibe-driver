#!/usr/bin/env python3
"""
Run script for Semi-Vibe-Device simulator and driver.
This script provides a unified testing system for the device and driver.
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


def perform_basic_tests(driver):
    """Perform basic tests to verify device connectivity and read all registers."""
    print("\n======== BASIC DEVICE TESTS ========")

    # Get device status
    print("\nReading device status...")
    status = driver.get_status()
    if not status:
        print("❌ Failed to get device status")
        return False

    print("Device status:")
    print(f"  Connected: {status['connected']}")
    print(f"  Sensors powered: {status['sensors_powered']}")
    print(f"  Actuators powered: {status['actuators_powered']}")
    print(f"  Has errors: {status['has_errors']}")

    # Get sensor data
    print("\nReading sensor data...")
    sensors = driver.get_sensors()
    if not sensors:
        print("❌ Failed to get sensor data")
        return False

    print("Sensor data:")
    print(f"  Temperature ID: 0x{sensors['temperature_id']:02X}")
    print(f"  Temperature value: {sensors['temperature_value']}")
    print(f"  Humidity ID: 0x{sensors['humidity_id']:02X}")
    print(f"  Humidity value: {sensors['humidity_value']}")

    # Get actuator data
    print("\nReading actuator data...")
    actuators = driver.get_actuators()
    if not actuators:
        print("❌ Failed to get actuator data")
        return False

    print("Actuator data:")
    print(f"  LED value: {actuators['led_value']}")
    print(f"  Fan value: {actuators['fan_value']}")
    print(f"  Heater value: {actuators['heater_value']}")
    print(f"  Doors value: 0x{actuators['doors_value']:02X}")

    print("\n✅ Basic device tests completed successfully")
    return True


def run_unified_tests():
    """Run the unified testing system."""
    print("\n======== STARTING UNIFIED TESTING SYSTEM ========")

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

    # Initialize driver
    print("\nInitializing driver...")
    driver = Driver()
    if not driver.init():
        print("❌ Failed to initialize driver")
        server.terminate()
        return 1

    # Connect to device
    print("\nConnecting to device...")
    if not driver.connect("localhost"):
        print("❌ Failed to connect to device")
        server.terminate()
        return 1

    print("✅ Successfully connected to device")

    try:
        # Perform basic tests
        if not perform_basic_tests(driver):
            print("❌ Basic tests failed")
            return 1

        # Import the test runner
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from tests.test_runner import run_all_tests

        # Run all tests
        print("\n======== RUNNING TEST MODULES ========")
        test_result = run_all_tests(driver)

        # Display the communication log
        if communications:
            display_communication(communications)

        return 0 if test_result else 1
    finally:
        # Disconnect from device
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

        # Wait for the output thread to finish
        output_thread.join(timeout=2)
        process_thread.join(timeout=2)

        print("Server stopped.")


def main():
    """Main function."""
    # Handle commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "test":
            # Run the unified tests
            return run_unified_tests()
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python run.py [test]")
    else:
        # Default to running the unified tests if no command is provided
        return run_unified_tests()

    return 0


if __name__ == "__main__":
    sys.exit(main())
