#!/usr/bin/env python3
"""Minimal build script for Semi-Vibe-Device simulator."""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        # Clean build directory
        if Path("build").exists():
            shutil.rmtree("build")
            print("Build directory cleaned.")
        return

    # Create build directory
    Path("build").mkdir(exist_ok=True)

    # Configure and build
    try:
        subprocess.run(["cmake", ".."], cwd="build", check=True)
        subprocess.run(["cmake", "--build", "."], cwd="build", check=True)
        print("Build completed successfully.")
    except subprocess.CalledProcessError:
        print("Build failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
