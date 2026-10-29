# Forge Platforms and Native Builds

[Русская версия](PLATFORMS.md) · [Project home](../README.en.md) · [Latest releases](https://github.com/W0rd3r566/Forge-System-Center/releases/latest)

Forge is built **on the target operating system and architecture**. A Windows executable is not a Linux build, and an ARM64 binary cannot replace an x64 binary. GitHub Actions builds each target independently, runs tests, and attaches checksums to published releases.

## Supported build matrix

| Platform | Architecture | Format |
| --- | --- | --- |
| Windows 10/11 | x64 (Intel/AMD, 64-bit) | Portable EXE inside ZIP |
| Windows 11 on Arm | ARM64 | Portable EXE inside ZIP |
| Debian/Ubuntu and derivatives | x86_64 | DEB, RPM, TAR.GZ |
| Modern Linux distributions | ARM64/aarch64 | DEB, RPM, TAR.GZ |
| macOS 14+ | Intel x64 | ZIP containing an .app bundle |
| macOS 14+ | Apple Silicon ARM64 | ZIP containing an .app bundle |

**32-bit Windows (x86) is not included.** Forge uses Qt 6 through PySide6. Current supported PySide6 Windows wheels are available for x64 and ARM64, not Win32. Promising a working 32-bit EXE without replacing the GUI stack or building Qt independently would be misleading. The ready-made Qt 6 Forge binaries also do not target 32-bit Linux.

## Files in a release

Open the [latest releases page](https://github.com/W0rd3r566/Forge-System-Center/releases/latest).

- **Windows:** ForgeSystemCenter-version-windows-x64.zip or ForgeSystemCenter-version-windows-arm64.zip. Extract the archive and launch ForgeSystemCenter.exe.
- **Debian, Ubuntu, Linux Mint, Pop!_OS and derivatives:** forge-system-center_version_amd64.deb or forge-system-center_version_arm64.deb.
- **Fedora and RPM-compatible distributions:** forge-system-center-version-1.x86_64.rpm or forge-system-center-version-1.aarch64.rpm.
- **Arch, CachyOS, Manjaro and other GNU/Linux distributions:** ForgeSystemCenter-version-linux-x86_64.tar.gz or ForgeSystemCenter-version-linux-arm64.tar.gz. The archive does not install system packages.
- **macOS:** ForgeSystemCenter-version-macos-x64.zip or ForgeSystemCenter-version-macos-arm64.zip.

Every public GitHub Release also includes SHA256SUMS.txt. Verify the downloaded archive's checksum to confirm its integrity.

## Linux compatibility

Linux bundles are built on Ubuntu 22.04 for x86_64 and Ubuntu 24.04 for ARM64. This sets the minimum glibc version:

| Architecture | Minimum glibc | Build environment |
| --- | --- | --- |
| x86_64 | 2.35 | Ubuntu 22.04 |
| ARM64/aarch64 | 2.39 | Ubuntu 24.04 |

Older distributions may not run a binary even when the package architecture matches. Modern Debian/Ubuntu and current rolling-release distros are generally suitable for x86_64. ARM64 requires glibc 2.39 or newer. Alpine Linux with musl is not a target for these prebuilt bundles.

### DEB

Install the local package in a graphical package manager or run:

~~~bash
sudo apt install ./forge-system-center_<version>_amd64.deb
~~~

For ARM64, replace amd64 with arm64. apt needs access to repositories that provide the package dependencies.

### RPM

On Fedora or a compatible system, install the downloaded RPM, for example:

~~~bash
sudo dnf install ./forge-system-center-<version>-1.x86_64.rpm
~~~

On ARM64, use the aarch64 file. On openSUSE, use its native package manager.

### TAR.GZ

~~~bash
tar -xzf ForgeSystemCenter-<version>-linux-x86_64.tar.gz
cd ForgeSystemCenter-<version>-linux-x86_64
./ForgeSystemCenter
~~~

For ARM64, select the archive containing linux-arm64. Without X11/XWayland or the required Qt system libraries, the GUI may not start. Arch/CachyOS may need packages such as libxcb, xcb-util-cursor, libxkbcommon, libxkbcommon-x11, mesa, libglvnd and dbus.

## Windows

The ZIP is a portable build, so no installer is needed. Extract it to a normal folder and launch ForgeSystemCenter.exe. Forge preferences remain in the current user's profile.

The executable is not publisher-signed, so SmartScreen may show an unknown-publisher warning. Verify the download source and SHA256SUMS.txt.

## macOS

macOS 14 or newer is required. Extract the ZIP and move ForgeSystemCenter.app to Applications. The Intel package is intended for Intel Macs; arm64 is for Apple Silicon. The apps are not currently signed or notarized by Apple, so macOS may show a Gatekeeper warning.

## Running builds and publishing

Run the **Native builds and releases** workflow manually from the **Actions** tab. Its artifacts remain available in the workflow run for 30 days. When a Git tag such as v0.2.0 is pushed, the workflow builds all targets and creates a GitHub Release with the archives and SHA256SUMS.txt.

Builds and tests use native Windows, Linux and macOS runners, including ARM64. This improves confidence in the output but does not replace testing on every device model and distribution.
