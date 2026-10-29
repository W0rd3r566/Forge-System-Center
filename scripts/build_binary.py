#!/usr/bin/env python3
"""Build a native Forge desktop bundle with PyInstaller."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    entry_point = ROOT / "run.py"
    assets = ROOT / "assets"
    if not entry_point.is_file():
        raise SystemExit(f"Entry point not found: {entry_point}")
    if not assets.is_dir():
        raise SystemExit(f"Assets directory not found: {assets}")

    system = platform.system()
    # PyInstaller uses the platform's native path separator in --add-data.
    asset_argument = f"{assets}{os.pathsep}assets"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        "ForgeSystemCenter",
        "--add-data",
        asset_argument,
        "--hidden-import",
        "PySide6.QtSvg",
    ]

    if system == "Darwin":
        # On macOS, --windowed produces a normal .app bundle suitable for Finder.
        command.extend(
            [
                "--windowed",
                "--onedir",
                "--osx-bundle-identifier",
                "dev.w0rd3r.forge-system-center",
            ]
        )
    else:
        # Native one-file bundles for Windows and Linux.
        command.extend(["--windowed", "--onefile"])

    command.append(str(entry_point))
    print("Building Forge for", f"{system}/{platform.machine()}")
    print("Command:", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)

    if system == "Darwin":
        expected = ROOT / "dist" / "ForgeSystemCenter.app"
    else:
        executable_name = "ForgeSystemCenter.exe" if system == "Windows" else "ForgeSystemCenter"
        expected = ROOT / "dist" / executable_name
    if not expected.exists():
        raise SystemExit(f"PyInstaller finished without creating {expected}")
    print("Build complete:", expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
