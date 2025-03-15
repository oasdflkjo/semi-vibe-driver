#!/usr/bin/env python3
"""
Run script for Semi-Vibe-Device simulator and driver.
Entry point for the unified testing system.
"""

import os
import sys
import time
import socket
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


def run_tests():
    """Run the unified testing system."""
    print("\n======== SEMI-VIBE-DEVICE TESTING SYSTEM ========")

    # Import the device module
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python"))
    from device import Device

    # Create and start the device
    print("Starting device server...")
    device = Device()
    if not device.start():
        print("❌ Failed to start device server")
        return 1

    # Wait for server to start
    if not is_server_ready():
        print("Server failed to start properly.")
        device.stop()
        return 1

    # Import the driver module
    from driver import Driver

    # Initialize driver and connect to device
    print("\nInitializing driver and connecting to device...")
    driver = Driver()
    if not driver.init():
        print("❌ Failed to initialize driver")
        device.stop()
        return 1

    if not driver.connect("localhost"):
        print("❌ Failed to connect to device")
        device.stop()
        return 1

    print("✅ Connected to device")

    try:
        # Import the test runner
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from tests.test_runner import run_all_tests

        # Run all tests
        test_result = run_all_tests(driver, device)

        return 0 if test_result else 1
    finally:
        # Clean up
        print("\nDisconnecting and shutting down...")
        driver.disconnect()
        device.stop()


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] != "test":
        print(f"Unknown command: {sys.argv[1]}")
        print("Usage: python run.py [test]")
        return 1

    return run_tests()


if __name__ == "__main__":
    sys.exit(main())
