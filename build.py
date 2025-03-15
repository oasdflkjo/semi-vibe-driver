#!/usr/bin/env python3
"""Minimal build script for Semi-Vibe-Device simulator."""

import shlex
import subprocess
from pathlib import Path

# "C-style" defines
CMAKE_CONFIGURE = "cmake .."
CMAKE_BUILD = "cmake --build ."
BUILD_DIR = "build"


def main():
    # Ensure build directory exists
    Path(BUILD_DIR).mkdir(exist_ok=True)

    # Configure and build
    try:
        run_command(CMAKE_CONFIGURE, BUILD_DIR)
        run_command(CMAKE_BUILD, BUILD_DIR)
        print("Build completed successfully.")
    except subprocess.CalledProcessError:
        print("Build failed.")
        exit(1)


def run_command(cmd_str, cwd=None):
    subprocess.run(
        shlex.split(cmd_str),
        cwd=cwd,
        check=True,
    )


if __name__ == "__main__":
    main()
