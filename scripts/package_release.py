#!/usr/bin/env python3
"""Create platform-native Forge archives and Linux DEB/RPM packages."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

from forge import __version__


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Name=Forge System Center
Comment=Local desktop system monitor
Exec=forge-system-center
Icon=forge-system-center
Terminal=false
Categories=System;Monitor;
StartupNotify=true
"""


def machine_labels() -> tuple[str, str, str, str]:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return "x64", "amd64", "x86_64", "2.35"
    if machine in {"aarch64", "arm64"}:
        return "arm64", "arm64", "aarch64", "2.39"
    raise SystemExit(f"Unsupported Linux architecture for this release workflow: {machine}")


def install_readme(platform_name: str) -> str:
    return f"""Forge System Center {__version__}
Platform bundle: {platform_name}

Windows:
  Extract the ZIP archive and launch ForgeSystemCenter.exe.

macOS:
  Extract the ZIP archive and move ForgeSystemCenter.app to Applications.
  This build is unsigned. macOS may show a Gatekeeper warning.

Linux:
  Run ./ForgeSystemCenter from a terminal or your desktop session.
  The binary is built for glibc { '2.35+' if platform.machine().lower() in {'x86_64', 'amd64'} else '2.39+' }.
  X11/XWayland or a compatible Qt platform plugin and the usual desktop
  runtime libraries are required. Recent Debian/Ubuntu, Fedora, openSUSE,
  Arch, CachyOS and related distributions are the target family.

The portable bundle does not install itself or modify system settings.
Forge stores its preferences in the current user's configuration directory.
See https://github.com/W0rd3r566/Forge-System-Center for documentation.
"""


def require_file(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Expected build output was not found: {path}")


def package_windows(output: Path) -> None:
    executable = DIST / "ForgeSystemCenter.exe"
    require_file(executable)
    arch = "arm64" if platform.machine().lower() in {"arm64", "aarch64"} else "x64"
    archive = output / f"ForgeSystemCenter-{__version__}-windows-{arch}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as zf:
        zf.write(executable, "ForgeSystemCenter.exe")
        zf.write(ROOT / "LICENSE", "LICENSE")
        zf.writestr("README-INSTALL.txt", install_readme(f"Windows {arch}"))
    print("Created", archive)


def package_macos(output: Path) -> None:
    app_bundle = DIST / "ForgeSystemCenter.app"
    require_file(app_bundle)
    arch = "arm64" if platform.machine().lower() in {"arm64", "aarch64"} else "x64"
    resources = app_bundle / "Contents" / "Resources"
    resources.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "LICENSE", resources / "LICENSE")
    (resources / "README-INSTALL.txt").write_text(install_readme(f"macOS {arch}"), encoding="utf-8")
    archive = output / f"ForgeSystemCenter-{__version__}-macos-{arch}.zip"
    subprocess.run(
        ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(app_bundle), str(archive)],
        check=True,
    )
    print("Created", archive)


def copy_linux_layout(root: Path, binary: Path) -> None:
    (root / "usr" / "bin").mkdir(parents=True, exist_ok=True)
    (root / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
    (root / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps").mkdir(parents=True, exist_ok=True)
    (root / "usr" / "share" / "doc" / "forge-system-center").mkdir(parents=True, exist_ok=True)
    shutil.copy2(binary, root / "usr" / "bin" / "forge-system-center")
    os.chmod(root / "usr" / "bin" / "forge-system-center", 0o755)
    (root / "usr" / "share" / "applications" / "forge-system-center.desktop").write_text(DESKTOP_ENTRY, encoding="utf-8")
    shutil.copy2(ROOT / "assets" / "forge.svg", root / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "forge-system-center.svg")
    shutil.copy2(ROOT / "LICENSE", root / "usr" / "share" / "doc" / "forge-system-center" / "copyright")
    (root / "usr" / "share" / "doc" / "forge-system-center" / "README").write_text(install_readme("Linux"), encoding="utf-8")


def package_linux(output: Path) -> None:
    binary = DIST / "ForgeSystemCenter"
    require_file(binary)
    arch_label, deb_arch, rpm_arch, glibc_min = machine_labels()
    portable_name = f"ForgeSystemCenter-{__version__}-linux-{arch_label}"
    portable_root = output / portable_name
    portable_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(binary, portable_root / "ForgeSystemCenter")
    os.chmod(portable_root / "ForgeSystemCenter", 0o755)
    shutil.copy2(ROOT / "LICENSE", portable_root / "LICENSE")
    shutil.copy2(ROOT / "assets" / "forge.svg", portable_root / "forge.svg")
    (portable_root / "forge-system-center.desktop").write_text(DESKTOP_ENTRY, encoding="utf-8")
    (portable_root / "README-INSTALL.txt").write_text(install_readme(f"Linux {arch_label}"), encoding="utf-8")

    tar_path = output / f"{portable_name}.tar.gz"
    with tarfile.open(tar_path, "w:gz", compresslevel=9) as archive:
        archive.add(portable_root, arcname=portable_name)
    print("Created", tar_path)

    with tempfile.TemporaryDirectory(prefix="forge-deb-") as temporary:
        deb_root = Path(temporary) / "root"
        copy_linux_layout(deb_root, binary)
        control_dir = deb_root / "DEBIAN"
        control_dir.mkdir(parents=True)
        dependencies = [
            f"libc6 (>= {glibc_min})",
            "libegl1",
            "libgl1",
            "libdbus-1-3",
            "libxkbcommon-x11-0",
            "libxcb-cursor0",
            "libxcb-icccm4",
            "libxcb-keysyms1",
            "libxcb-shape0",
            "libxcb-xinerama0",
            "libxcb-randr0",
            "libxcb-render-util0",
            "libxcb-xkb1",
            "libxcb-util1",
        ]
        control = (
            "Package: forge-system-center\n"
            f"Version: {__version__}\n"
            f"Architecture: {deb_arch}\n"
            "Section: utils\n"
            "Priority: optional\n"
            "Maintainer: W0rd3r566\n"
            "Homepage: https://github.com/W0rd3r566/Forge-System-Center\n"
            f"Depends: {', '.join(dependencies)}\n"
            "Description: Local-first desktop system monitor and control center\n"
            " Forge System Center provides hardware monitoring, diagnostics,\n"
            " process management and appearance customization.\n"
        )
        (control_dir / "control").write_text(control, encoding="utf-8")
        (control_dir / "postinst").write_text("#!/bin/sh\nset -e\nif command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q /usr/share/applications || true; fi\nexit 0\n", encoding="utf-8")
        os.chmod(control_dir / "postinst", 0o755)
        deb_path = output / f"forge-system-center_{__version__}_{deb_arch}.deb"
        subprocess.run(
            ["dpkg-deb", "--build", "--root-owner-group", str(deb_root), str(deb_path)],
            check=True,
        )
        print("Created", deb_path)

    with tempfile.TemporaryDirectory(prefix="forge-rpm-") as temporary:
        topdir = Path(temporary) / "rpmbuild"
        for directory in ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"):
            (topdir / directory).mkdir(parents=True)
        sources = topdir / "SOURCES"
        shutil.copy2(binary, sources / "ForgeSystemCenter")
        shutil.copy2(ROOT / "assets" / "forge.svg", sources / "forge.svg")
        shutil.copy2(ROOT / "LICENSE", sources / "LICENSE")
        (sources / "forge-system-center.desktop").write_text(DESKTOP_ENTRY, encoding="utf-8")
        sonames = [
            "libxcb.so.1()(64bit)", "libxcb-cursor.so.0()(64bit)",
            "libxcb-icccm.so.4()(64bit)", "libxcb-keysyms.so.1()(64bit)",
            "libxcb-randr.so.0()(64bit)", "libxcb-render-util.so.0()(64bit)",
            "libxcb-shape.so.0()(64bit)", "libxcb-xinerama.so.0()(64bit)",
            "libxcb-xkb.so.1()(64bit)", "libxkbcommon.so.0()(64bit)",
            "libxkbcommon-x11.so.0()(64bit)", "libX11.so.6()(64bit)",
            "libXrender.so.1()(64bit)", "libEGL.so.1()(64bit)",
            "libGL.so.1()(64bit)", "libdbus-1.so.3()(64bit)",
        ]
        requires = "\n".join(f"Requires: {soname}" for soname in sonames)
        spec = f"""Name: forge-system-center
Version: {__version__}
Release: 1%{{?dist}}
Summary: Local-first desktop system monitor and control center
License: MIT
BuildArch: {rpm_arch}
Requires: glibc >= {glibc_min}
{requires}

%description
Forge System Center provides hardware monitoring, diagnostics,
process management and appearance customization.

%prep

%build

%install
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/icons/hicolor/scalable/apps
mkdir -p %{{buildroot}}/usr/share/licenses/forge-system-center
install -m 0755 %{{SOURCE0}} %{{buildroot}}/usr/bin/forge-system-center
install -m 0644 %{{SOURCE1}} %{{buildroot}}/usr/share/applications/forge-system-center.desktop
install -m 0644 %{{SOURCE2}} %{{buildroot}}/usr/share/icons/hicolor/scalable/apps/forge-system-center.svg
install -m 0644 %{{SOURCE3}} %{{buildroot}}/usr/share/licenses/forge-system-center/LICENSE

%files
%attr(0755,root,root) /usr/bin/forge-system-center
%attr(0644,root,root) /usr/share/applications/forge-system-center.desktop
%attr(0644,root,root) /usr/share/icons/hicolor/scalable/apps/forge-system-center.svg
%license /usr/share/licenses/forge-system-center/LICENSE

%changelog
* Thu Oct 29 2026 Forge System Center contributors - {__version__}-1
- Initial multi-architecture package
"""
        spec_path = topdir / "SPECS" / "forge-system-center.spec"
        spec_path.write_text(spec, encoding="utf-8")
        subprocess.run(
            [
                "rpmbuild", "-bb", "--target", rpm_arch,
                "--define", f"_topdir {topdir}",
                str(spec_path),
            ],
            check=True,
        )
        built_rpms = list((topdir / "RPMS" / rpm_arch).glob("*.rpm"))
        if not built_rpms:
            raise SystemExit("rpmbuild finished without creating an RPM")
        rpm_path = output / f"forge-system-center-{__version__}-1.{rpm_arch}.rpm"
        shutil.copy2(built_rpms[0], rpm_path)
        print("Created", rpm_path)


def main() -> int:
    output = DIST / "packages"
    output.mkdir(parents=True, exist_ok=True)
    system = platform.system()
    if system == "Windows":
        package_windows(output)
    elif system == "Darwin":
        package_macos(output)
    elif system == "Linux":
        package_linux(output)
    else:
        raise SystemExit(f"Unsupported packaging platform: {system}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
