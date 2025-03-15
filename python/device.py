"""
Simulated device for the Semi-Vibe-Device.
This script provides a simple device simulator that communicates via sockets.
"""

import socket
import threading
import json
import time


class Device:
    """Semi-Vibe-Device simulator class."""

    def __init__(self, print_callback=None):
        """Initialize the device simulator.

        Args:
            print_callback: Optional function to handle print messages
        """
        self.server_socket = None
        self.client_socket = None
        self.running = False
        self.server_thread = None
        self.print_callback = print_callback or print

        # Device state
        self.state = {
            "status": {
                "connected": False,
                "sensors_powered": True,
                "actuators_powered": True,
                "has_errors": False,
            },
            "sensors": {
                "temperature_id": 0x01,
                "temperature_value": 25,
                "humidity_id": 0x02,
                "humidity_value": 50,
            },
            "actuators": {
                "led_value": 0,
                "fan_value": 0,
                "heater_value": 0,
                "doors_value": 0,
            },
        }

    def _log(self, message):
        """Log a message using the callback or print."""
        self.print_callback(f"[DEVICE] {message}")

    def start(self, host="localhost", port=8989):
        """Start the device server."""
        if self.running:
            self._log("Server already running")
            return True

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(1)

            self.running = True
            self._log(f"Server started on {host}:{port}")

            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            return True
        except Exception as e:
            self._log(f"Failed to start server: {e}")
            return False

    def stop(self):
        """Stop the device server."""
        if not self.running:
            return True

        try:
            self.running = False

            # Close client socket if connected
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None

            # Wait for server thread to finish
            if self.server_thread:
                self.server_thread.join(timeout=1)
                self.server_thread = None

            self._log("Server stopped")
            return True
        except Exception as e:
            self._log(f"Failed to stop server: {e}")
            return False

    def _server_loop(self):
        """Main server loop."""
        self._log("Server loop started")

        while self.running:
            try:
                # Wait for a connection
                self._log("Waiting for connection...")
                self.server_socket.settimeout(
                    1.0
                )  # 1 second timeout to check running flag
                try:
                    self.client_socket, addr = self.server_socket.accept()
                    self.state["status"]["connected"] = True
                    self._log(f"Connection from {addr}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self._log(f"Accept error: {e}")
                    continue

                # Handle client communication
                self.client_socket.settimeout(
                    None
                )  # No timeout for client communication
                while self.running and self.client_socket:
                    try:
                        # Receive data
                        data = self.client_socket.recv(1024)
                        if not data:
                            self._log("Client disconnected")
                            break

                        # Process command
                        message = data.decode("utf-8").strip()
                        self._log(f"Received: {message}")

                        # Parse and handle command
                        try:
                            command = json.loads(message)
                            response = self._handle_command(command)
                            response_str = json.dumps(response)

                            # Send response
                            self._log(f"Sent response: {response_str}")
                            self.client_socket.sendall(
                                f"{response_str}\n".encode("utf-8")
                            )
                        except json.JSONDecodeError:
                            self._log(f"Invalid JSON: {message}")
                            error_response = json.dumps({"error": "Invalid JSON"})
                            self.client_socket.sendall(
                                f"{error_response}\n".encode("utf-8")
                            )
                    except Exception as e:
                        self._log(f"Client communication error: {e}")
                        break

                # Close client socket
                if self.client_socket:
                    self.client_socket.close()
                    self.client_socket = None
                    self.state["status"]["connected"] = False
            except Exception as e:
                if self.running:
                    self._log(f"Server error: {e}")
                    time.sleep(1)  # Prevent tight loop on error

        self._log("Server loop ended")

    def _handle_command(self, command):
        """Handle a command from the client."""
        cmd = command.get("command", "").upper()
        data = command.get("data", {})

        if cmd == "GET_STATUS":
            return {"status": self.state["status"]}

        elif cmd == "GET_SENSORS":
            return {"sensors": self.state["sensors"]}

        elif cmd == "GET_ACTUATORS":
            return {"actuators": self.state["actuators"]}

        elif cmd == "SET_LED":
            value = data.get("value", 0)
            if 0 <= value <= 255:
                self.state["actuators"]["led_value"] = value
                return {"success": True}
            return {"success": False, "error": "Invalid value"}

        elif cmd == "SET_FAN":
            value = data.get("value", 0)
            if 0 <= value <= 255:
                self.state["actuators"]["fan_value"] = value
                return {"success": True}
            return {"success": False, "error": "Invalid value"}

        elif cmd == "SET_HEATER":
            value = data.get("value", 0)
            if 0 <= value <= 255:
                self.state["actuators"]["heater_value"] = value
                return {"success": True}
            return {"success": False, "error": "Invalid value"}

        elif cmd == "SET_DOORS":
            value = data.get("value", 0)
            if 0 <= value <= 255:
                self.state["actuators"]["doors_value"] = value
                return {"success": True}
            return {"success": False, "error": "Invalid value"}

        else:
            return {"success": False, "error": f"Unknown command: {cmd}"}

    # Direct access methods (for testing without sockets)
    def get_status(self):
        """Get device status directly."""
        return self.state["status"]

    def get_sensors(self):
        """Get sensor data directly."""
        return self.state["sensors"]

    def get_actuators(self):
        """Get actuator data directly."""
        return self.state["actuators"]

    def set_led(self, value):
        """Set LED value directly."""
        if 0 <= value <= 255:
            self.state["actuators"]["led_value"] = value
            return True
        return False

    def set_fan(self, value):
        """Set fan value directly."""
        if 0 <= value <= 255:
            self.state["actuators"]["fan_value"] = value
            return True
        return False

    def set_heater(self, value):
        """Set heater value directly."""
        if 0 <= value <= 255:
            self.state["actuators"]["heater_value"] = value
            return True
        return False

    def set_doors(self, value):
        """Set doors value directly."""
        if 0 <= value <= 255:
            self.state["actuators"]["doors_value"] = value
            return True
        return False
