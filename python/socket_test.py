"""
Socket test script for the Semi-Vibe-Device simulator.
This script connects to the device via socket and sends commands.
"""

import socket
import time
import sys


def main():
    """Main function."""
    print("Semi-Vibe-Device Socket Test")
    print("---------------------------")

    # Connect to the device
    host = "localhost"
    port = 8989

    print(f"Connecting to {host}:{port}...")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    except ConnectionRefusedError:
        print("Connection refused. Make sure the device simulator is running.")
        return 1
    except Exception as e:
        print(f"Error connecting to device: {e}")
        return 1

    print("Connected to device.")

    # Wait for ACK message
    ack = s.recv(1024).decode("utf-8")
    print(f"Received: {ack}")

    if ack != "ACK":
        print("Did not receive ACK from device.")
        s.close()
        return 1

    # Send test commands
    test_commands = [
        "100000",  # Read MAIN connected_device
        "102000",  # Read MAIN power_state
        "103000",  # Read MAIN error_state
        "210000",  # Read SENSOR_A ID
        "211000",  # Read SENSOR_A reading
        "220000",  # Read SENSOR_B ID
        "221000",  # Read SENSOR_B reading
        "310180",  # Write ACTUATOR_A value 0x80
        "310000",  # Read ACTUATOR_A value
        "320140",  # Write ACTUATOR_B value 0x40
        "320000",  # Read ACTUATOR_B value
        "330108",  # Write ACTUATOR_C value 0x08
        "330000",  # Read ACTUATOR_C value
        "340155",  # Write ACTUATOR_D value 0x55
        "340000",  # Read ACTUATOR_D value
        "4FB111",  # Write CONTROL power_sensors
        "4FB000",  # Read CONTROL power_sensors
        "4FC155",  # Write CONTROL power_actuators
        "4FC000",  # Read CONTROL power_actuators
    ]

    for cmd in test_commands:
        print(f"Sending: {cmd}")
        s.sendall(cmd.encode("utf-8"))

        response = s.recv(1024).decode("utf-8")
        print(f"Received: {response}")

        time.sleep(0.1)  # Small delay between commands

    # Send exit command
    print("Sending exit command...")
    s.sendall("exit".encode("utf-8"))

    # Close socket
    s.close()
    print("Socket closed.")

    print("Test completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
