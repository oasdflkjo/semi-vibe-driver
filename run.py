#!/usr/bin/env python3
"""Minimal run script for Semi-Vibe-Device simulator."""

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


def main():
    # Check if build exists
    if not (
        Path("build/bin/Debug/semi_vibe_device.dll").exists()
        or Path("build/bin/semi_vibe_device.dll").exists()
        or Path("build/lib/libsemi_vibe_device.so").exists()
    ):
        print("Error: Build not found. Run build.py first.")
        sys.exit(1)

    # Handle commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "server":
            # Run server
            subprocess.run([sys.executable, "python/server.py"])

        elif cmd == "client":
            # Run client
            subprocess.run([sys.executable, "python/socket_test.py"])

        elif cmd == "both":
            # Start server in background
            if os.name == "nt":  # Windows
                server = subprocess.Popen(
                    [sys.executable, "python/server.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            else:
                server = subprocess.Popen([sys.executable, "python/server.py"])

            # Wait for server to start and be ready
            print("Starting server and waiting for it to be ready...")
            if not is_server_ready():
                print("Server failed to start properly. Terminating.")
                server.terminate()
                return 1

            try:
                # Run client
                subprocess.run([sys.executable, "python/socket_test.py"])
            finally:
                # Kill server
                server.terminate()
                print("Server stopped.")
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python run.py [server|client|both]")
    else:
        print("Usage: python run.py [server|client|both]")


if __name__ == "__main__":
    main()
