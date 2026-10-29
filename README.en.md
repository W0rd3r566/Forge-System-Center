<p align="center">
  <img src="assets/forge.svg" alt="Forge logo" width="100">
</p>

<h1 align="center">Forge System Center</h1>
<p align="center"><strong>Understand your system. Keep your data yours.</strong></p>
<p align="center"><a href="README.md">Русская документация</a> · <a href="#features">Features</a> · <a href="#installation">Installation</a> · <a href="#customization">Customization</a> · <a href="docs/CUSTOMIZATION.en.md">Full QSS handbook</a></p>

<p align="center">
  <a href="https://github.com/W0rd3r566/Forge-System-Center/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/W0rd3r566/Forge-System-Center/ci.yml?branch=main&style=for-the-badge&label=CI" alt="CI status"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-7378d8?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Qt-PySide6-41a675?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/W0rd3r566/Forge-System-Center?style=for-the-badge" alt="MIT license"></a>
</p>

Forge is a desktop system monitoring and management hub for **Linux and Windows**. It brings performance statistics, processes, storage, network counters, available hardware sensors, and diagnostics into one PySide6 interface.

Forge is local-first: no account, built-in analytics, or automatic upload of system data. Preferences and the app activity log stay in the current user's profile.

---

## Features

<table>
  <tr>
    <td width="50%"><h3>◈ System overview</h3>CPU and memory usage, system disk space, process count, OS and device details.</td>
    <td width="50%"><h3>⌁ Monitoring</h3>CPU and memory history charts. Temperatures, fans, battery and NVIDIA GPU metrics when exposed by the system.</td>
  </tr>
  <tr>
    <td><h3>▤ Process manager</h3>Search by name, PID and user, sort by resource usage, and terminate a selected process with confirmation.</td>
    <td><h3>⇅ Network center</h3>Upload/download rates, aggregate traffic counters and a network-interface table. Per-application traffic attribution is not implemented yet.</td>
  </tr>
  <tr>
    <td><h3>▦ Storage</h3>Disk capacity and free space, plus folder-size analysis that does not follow symbolic links.</td>
    <td><h3>⚙ Services and startup</h3>Manage systemd services on Linux. User startup entries can be reversibly enabled or disabled on Linux and Windows.</td>
  </tr>
  <tr>
    <td><h3>⌕ Diagnostics</h3>Quick checks for CPU, memory, disk space and available temperatures; a local Forge activity log; JSON diagnostic export.</td>
    <td><h3>✳ Personalization</h3>Built-in themes, accent colors, wallpapers, font size, sidebar width, refresh interval, custom QSS and portable appearance profiles.</td>
  </tr>
  <tr>
    <td><h3>⌘ Command palette</h3>Press Ctrl+K to navigate sections and run common actions from one searchable list.</td>
    <td><h3>▤ Hardware and history</h3>CPU, memory, graphics and sensor details plus persistent local performance charts and CSV export.</td>
  </tr>
  <tr>
    <td><h3>◉ Mini monitor and tray</h3>A floating CPU/RAM/disk widget, configurable opacity, and tray-menu controls for Forge.</td>
    <td><h3>⚑ Smart alerts</h3>Configurable CPU, memory, disk and available temperature thresholds with local notifications.</td>
  </tr>
  <tr>
    <td><h3>⌁ Network lab</h3>Read-only checks for local interfaces, DNS servers, hostname resolution, external ICMP and the default route.</td>
    <td><h3>↶ Change journal</h3>Local action history and safe rollback for settings, selected user startup changes and supported service actions.</td>
  </tr>
  <tr>
    <td colspan="2"><h3>◈ Work modes and QSS presets</h3>Balanced, Gaming, Work and Quiet modes. Customize the appearance with Liquid Glass, Soft Acrylic, Miku Cyan, Minimal and custom QSS.</td>
  </tr>
</table>

## Customization

Open **Appearance** to make Forge your own:

- **Themes:** Graphite, Midnight, Emerald and Light.
- **Accent colors:** lavender, blue, mint, pink, amber, coral and teal.
- **Wallpapers:** PNG, JPEG, WebP, BMP and GIF. Images remain local and are blended into the window background using an adjustable intensity.
- **Fonts and geometry:** font family and size, sidebar width, corner radius and density.
- **Liquid Glass:** transparent window background, local wallpaper, softened backdrop and a configurable frosted tint. Real desktop blur depends on the window compositor.
- **QSS presets:** Liquid Glass, Soft Acrylic, Miku Cyan and Minimal. Import/export your own `.qss` or plain-text `.css` files.
- **Monitoring:** warning thresholds, floating mini monitor, opacity and refresh interval.
- **Work modes:** Balanced, Gaming, Work and Quiet. Appearance settings can also be imported/exported as JSON profiles.
- **Full handbook:** [widget selectors, QSS examples, states and limitations](docs/CUSTOMIZATION.en.md). QSS styles Qt widgets; it does not support JavaScript, a browser DOM, `backdrop-filter`, `box-shadow` or CSS animations.

Example QSS:

~~~css
/* QSS for the Qt interface, not a web page stylesheet. */
#panel {
    border-radius: 18px;
    border: 1px solid #423b61;
}
#navButton:checked {
    background: #292440;
    border: 1px solid #a99bff;
}
QPushButton {
    padding: 9px 14px;
}
~~~

Paste your rules into the QSS editor and select **Save and apply**. Custom styles are stored separately from the source code and do not modify project files.

## Installation

### Ready-to-download builds

Recommended: download the archive for your OS and architecture from [GitHub Releases](https://github.com/W0rd3r566/Forge-System-Center/releases/latest). The [platform guide](docs/PLATFORMS.en.md) lists system requirements, package types and detailed install instructions.

| Platform | Available package |
| --- | --- |
| Windows x64 / ARM64 | ZIP with portable EXE |
| Debian / Ubuntu x86_64 and ARM64 | DEB |
| Fedora and RPM-compatible distributions | RPM |
| CachyOS / Arch / Manjaro / other Linux | TAR.GZ |
| macOS Intel / Apple Silicon | ZIP with .app bundle |

32-bit Windows and Linux are currently outside the build matrix because Qt 6 through PySide6 does not provide suitable supported wheels for these targets. Choose x64 for Intel/AMD Windows computers and ARM64 for Windows on Arm devices. Linux binaries have different minimum glibc requirements, documented in the platform guide.

### Linux · CachyOS, Arch, Debian and more

Python 3.10 or newer is required. Arch/CachyOS may need the Qt/XCB runtime libraries:

~~~bash
sudo pacman -S --needed python python-pip libxcb xcb-util-cursor libxkbcommon mesa libglvnd fontconfig freetype2 dbus
~~~

Debian/Ubuntu:

~~~bash
sudo apt update
sudo apt install python3 python3-venv python3-pip libegl1 libgl1 libxkbcommon-x11-0 libdbus-1-3 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libxcb-xinerama0
~~~

Then, on either system:

~~~bash
git clone https://github.com/W0rd3r566/Forge-System-Center.git
cd Forge-System-Center
bash install.sh
~~~

The installer creates an isolated **.venv**, installs PySide6 and psutil, and adds a per-user desktop entry. It does not use **sudo** or modify the system Python installation.

Launch Forge:

~~~bash
bash run.sh
~~~

To update an existing clone, run **git pull** and then **bash run.sh**.

### Windows 10 / 11

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/windows/) and enable **Add Python to PATH**.
2. Open PowerShell in the project directory.
3. Run:

~~~powershell
.\install.ps1
.\run.bat
~~~

If PowerShell blocks the installer, temporarily allow scripts in the current window only:

~~~powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
.\run.bat
~~~

## Command palette

Press **Ctrl+K** or use the Commands button in the top bar. Search for a section or run an action such as refreshing system metrics, reading sensors, running diagnostics or exporting history.

## Performance history

Forge records CPU, memory, system-disk and available NVIDIA GPU usage about every 15 seconds to the current user's configuration directory. The history remains local, is size-bounded, and can be viewed, exported as CSV or cleared from the History page. Collection begins with the first run of version 0.2.0; earlier in-memory chart points are not backfilled.

## Platform support

| Feature | Linux | Windows |
|---|:---:|:---:|
| Overview, processes and storage | ✓ | ✓ |
| CPU and memory history charts | ✓ | ✓ |
| Network counters and interfaces | ✓ | ✓ |
| Temperature, battery and fan readings | When available | When available |
| NVIDIA metrics through nvidia-smi | If driver and utility are installed | If driver and utility are installed |
| User startup entries | ✓ | ✓ |
| systemd service management | ✓ | — |
| Linux user-cache cleanup | ✓ | — |
| Wallpapers, themes, QSS and profiles | ✓ | ✓ |

Sensor availability depends on hardware, drivers and the data exposed by the operating system. When readings are unavailable, Forge reports that instead of inventing values.

## Development

Create a virtual environment:

~~~bash
python -m venv .venv
~~~

Activate it:

~~~bash
# Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
~~~

Install dependencies and run checks:

~~~bash
python -m pip install -r requirements.txt
python -m compileall -q forge run.py
python -m unittest discover -s tests -v
python run.py
~~~

GitHub Actions checks Python compilation, unit tests and offscreen GUI initialization on Linux and Windows.

## Privacy and safety

- Forge does not require an account, send telemetry, or upload wallpapers or custom styles.
- Preferences and the app activity log are stored in the user's local configuration directory.
- Diagnostic reports are created only on explicit request and are never uploaded automatically. They may contain process names and hardware details; review the file before sharing it.
- Forge does not elevate privileges to terminate processes. Service operations and startup changes require confirmation.
- Cleanup is limited to the Linux user's cache directory. Documents, downloads and system directories are not targeted.

## Dependencies and license

Forge uses Python, [PySide6](https://www.qt.io/qt-for-python) and [psutil](https://github.com/giampaolo/psutil). The outline icons follow the style of [Tabler Icons](https://github.com/tabler/tabler-icons); see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for notices.

Licensed under the [MIT License](LICENSE).

<p align="center"><sub>Forge System Center · local tools for a clearer view of your computer.</sub></p>
