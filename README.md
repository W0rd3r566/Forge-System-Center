# Forge System Center

**Forge** is a local-first desktop control panel for Linux and Windows, built with Python and PySide6. The interface uses a graphite theme and keeps system data local.

## Features

- Live CPU, memory, root-disk, uptime, and process-count overview.
- Process table with filtering, CPU and memory usage, and normal termination.
- Mounted-volume overview and a read-only largest-entry folder scan.
- Linux systemd user/system service inspection and confirmed start/stop/restart actions.
- Current-user startup entry toggles for Linux and Windows startup folders.
- Review and explicitly confirmed cleanup of the current user's `~/.cache` directory on Linux.
- Linux desktop launcher, Windows Start Menu shortcut, and uninstall helper.

## Requirements

- Python 3.10+
- PySide6 6.10.x
- psutil 5.9+

## Install on Linux

Extract or clone this folder somewhere you will keep it, then run:

```bash
bash install.sh
```

The installer creates an isolated `.venv` and a desktop entry under your home directory. It does not use sudo, install system packages, or make automatic system changes.

## Install on Windows

Install Python 3.10+, extract the repository, open PowerShell in the project directory, then run:

```powershell
.\install.ps1
```

After setup, launch with `run.bat` or use the Start Menu shortcut.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run.py
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1`.

## Safety notes

- Forge has no account, telemetry, or required runtime network connection.
- Process termination never escalates privileges.
- Service changes are restricted to start/stop/restart and require explicit confirmation. System-level actions use the desktop authentication prompt.
- Folder scans are read-only and do not follow symlinks.
- Cache cleanup is limited to the current user's `~/.cache`; review the displayed path and confirmation prompt first.
- Windows support is partial. Linux systemd service controls are not available on Windows.

This is an early MVP. Test it on your system before relying on it for administration.

## License

MIT. See [LICENSE](LICENSE).
