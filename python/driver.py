"""
Driver script for the Semi-Vibe-Driver.
This script provides a simple interface to communicate with the device via sockets.
"""

import socket
import json


class Driver:
    """Semi-Vibe-Driver wrapper class."""

    def __init__(self, print_callback=None):
        """Initialize the driver.

        Args:
            print_callback: Optional function to handle print messages
        """
        self.socket = None
        self.connected = False
        self.print_callback = print_callback or print

    def _log(self, message):
        """Log a message using the callback or print."""
        self.print_callback(f"[DRIVER] {message}")

    def init(self):
        """Initialize the driver."""
        self._log("Initializing driver")
        return True

    def connect(self, host="localhost", port=8989):
        """Connect to the device."""
        if self.connected:
            return True

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            self._log(f"Connected to device at {host}:{port}")
            return True
        except Exception as e:
            self._log(f"Failed to connect to device: {e}")
            return False

    def disconnect(self):
        """Disconnect from the device."""
        if not self.connected:
            return True

        try:
            self.socket.close()
            self.connected = False
            self._log("Disconnected from device")
            return True
        except Exception as e:
            self._log(f"Failed to disconnect from device: {e}")
            return False

    def _send_command(self, command, data=None):
        """Send a command to the device and get the response."""
        if not self.connected:
            self._log("Not connected to device")
            return None

        message = {"command": command}
        if data:
            message["data"] = data

        try:
            # Convert message to JSON and send
            message_str = json.dumps(message)
            self._log(f"Sending: {message_str}")
            self.socket.sendall(f"{message_str}\n".encode("utf-8"))

            # Receive response
            response = self.socket.recv(1024).decode("utf-8").strip()
            self._log(f"Received: {response}")

            # Parse response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                self._log(f"Failed to parse response: {response}")
                return None
        except Exception as e:
            self._log(f"Communication error: {e}")
            return None

    def get_status(self):
        """Get device status."""
        response = self._send_command("GET_STATUS")
        if not response or "status" not in response:
            return None
        return response["status"]

    def get_sensors(self):
        """Get sensor data."""
        response = self._send_command("GET_SENSORS")
        if not response or "sensors" not in response:
            return None
        return response["sensors"]

    def get_actuators(self):
        """Get actuator data."""
        response = self._send_command("GET_ACTUATORS")
        if not response or "actuators" not in response:
            return None
        return response["actuators"]

    def set_led(self, value):
        """Set LED value."""
        response = self._send_command("SET_LED", {"value": value})
        return response and response.get("success", False)

    def set_fan(self, value):
        """Set fan value."""
        response = self._send_command("SET_FAN", {"value": value})
        return response and response.get("success", False)

    def set_heater(self, value):
        """Set heater value."""
        response = self._send_command("SET_HEATER", {"value": value})
        return response and response.get("success", False)

    def set_doors(self, value):
        """Set doors value."""
        response = self._send_command("SET_DOORS", {"value": value})
        return response and response.get("success", False)
