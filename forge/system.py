from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import psutil

APP_NAME = "Forge"
_SAFE_UNIT = re.compile(r"^[A-Za-z0-9_@.:-]+$")


def format_bytes(value: int | float) -> str:
    amount = max(0.0, float(value))
    units = ("B", "KB", "MB", "GB", "TB", "PB")
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.0f} {unit}" if unit == "B" else f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} PB"


def get_system_snapshot() -> dict[str, Any]:
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    root_path = Path.home().anchor or "/"
    try:
        disk = psutil.disk_usage(root_path)
    except OSError:
        disk = psutil.disk_usage("/")
    boot = psutil.boot_time()
    uptime_seconds = max(0, int(time.time() - boot))
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime = f"{days}d {hours:02}h {minutes:02}m" if days else f"{hours}h {minutes:02}m"

    gpu = "Not detected"
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        try:
            result = subprocess.run(
                [nvidia_smi, "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu = result.stdout.strip().splitlines()[0]
        except (OSError, subprocess.TimeoutExpired):
            pass

    battery_text = ""
    try:
        battery = psutil.sensors_battery()
        if battery is not None:
            battery_text = f"{battery.percent:.0f}%" + (" · charging" if battery.power_plugged else "")
    except (AttributeError, OSError):
        pass

    return {
        "cpu": float(cpu),
        "memory_percent": float(memory.percent),
        "memory_used": int(memory.used),
        "memory_total": int(memory.total),
        "disk_percent": float(disk.percent),
        "disk_used": int(disk.used),
        "disk_total": int(disk.total),
        "uptime": uptime,
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "python": platform.python_version(),
        "hostname": platform.node() or "Unknown device",
        "gpu": gpu,
        "battery": battery_text,
        "process_count": len(psutil.pids()),
    }


def list_processes(limit: int = 500) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    attrs = ["pid", "name", "username", "memory_percent", "cpu_percent"]
    for proc in psutil.process_iter(attrs=attrs, ad_value=None):
        try:
            info = proc.info
            rows.append(
                {
                    "pid": int(info.get("pid") or 0),
                    "name": str(info.get("name") or "Unknown"),
                    "user": str(info.get("username") or "—"),
                    "memory_percent": float(info.get("memory_percent") or 0.0),
                    "cpu_percent": float(info.get("cpu_percent") or 0.0),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, TypeError, ValueError):
            continue
    rows.sort(key=lambda row: (row["cpu_percent"], row["memory_percent"]), reverse=True)
    return rows[: max(1, limit)]


def terminate_process(pid: int) -> None:
    if pid <= 1 or pid == os.getpid():
        raise ValueError("Forge will not terminate itself or a core system process.")
    try:
        process = psutil.Process(pid)
        process.terminate()
    except psutil.NoSuchProcess as exc:
        raise RuntimeError("That process has already exited.") from exc
    except psutil.AccessDenied as exc:
        raise PermissionError("Permission denied. Forge will not request elevated access to terminate processes.") from exc


def list_disks() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for part in psutil.disk_partitions(all=False):
        mountpoint = part.mountpoint
        if not mountpoint or mountpoint in seen:
            continue
        if platform.system() == "Linux" and part.fstype.lower() in {"squashfs", "tmpfs", "devtmpfs", "overlay", "proc", "sysfs", "cgroup2", "fuse.portal"}:
            continue
        seen.add(mountpoint)
        try:
            usage = psutil.disk_usage(mountpoint)
        except (OSError, PermissionError):
            continue
        rows.append(
            {
                "device": part.device,
                "mountpoint": mountpoint,
                "fstype": part.fstype or "Unknown",
                "used": int(usage.used),
                "total": int(usage.total),
                "free": int(usage.free),
                "percent": float(usage.percent),
            }
        )
    rows.sort(key=lambda row: row["mountpoint"])
    return rows


def _systemctl(scope: str, args: list[str], timeout: float = 12) -> subprocess.CompletedProcess[str]:
    if scope not in {"user", "system"}:
        raise ValueError("Unknown service scope.")
    command = ["systemctl"]
    if scope == "user":
        command.append("--user")
    command.extend(args)
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)


def list_services(scope: str = "user") -> list[dict[str, str]]:
    if platform.system() != "Linux" or not shutil.which("systemctl"):
        raise RuntimeError("The service manager in this build requires Linux with systemd.")
    result = _systemctl(scope, ["list-units", "--type=service", "--all", "--no-legend", "--no-pager"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "systemctl returned an error"
        raise RuntimeError(detail)
    services: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(maxsplit=4)
        if len(parts) < 4:
            continue
        unit, load_state, active, sub = parts[:4]
        description = parts[4] if len(parts) == 5 else ""
        if not _SAFE_UNIT.fullmatch(unit):
            continue
        services.append(
            {
                "unit": unit,
                "load": load_state,
                "active": active,
                "sub": sub,
                "description": description,
                "scope": scope,
            }
        )
    services.sort(key=lambda row: (row["active"] != "active", row["unit"].lower()))
    return services


def service_action(unit: str, scope: str, action: str) -> str:
    if not _SAFE_UNIT.fullmatch(unit):
        raise ValueError("Invalid service name.")
    if action not in {"start", "stop", "restart"}:
        raise ValueError("Unsupported service action.")
    if scope == "user":
        result = _systemctl("user", [action, unit], timeout=90)
    elif scope == "system":
        pkexec = shutil.which("pkexec")
        if not pkexec:
            raise RuntimeError("pkexec was not found. Install polkit and a compatible authentication agent to manage system services.")
        result = subprocess.run(
            [pkexec, "systemctl", action, unit],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
    else:
        raise ValueError("Unknown service scope.")
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"Command exited with code {result.returncode}."
        raise RuntimeError(detail)
    return result.stdout.strip() or f"{unit}: {action} command completed."


def _autostart_directory() -> Path:
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is not available.")
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / ".config" / "autostart"


def list_startup_apps() -> list[dict[str, str | bool]]:
    directory = _autostart_directory()
    if not directory.exists():
        return []
    rows: list[dict[str, str | bool]] = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name.lower()):
        disabled = path.name.endswith(".forge-disabled")
        if platform.system() == "Windows":
            if not (path.is_file() or path.is_symlink()):
                continue
            if path.suffix.lower() not in {".lnk", ".url", ".bat", ".cmd", ".exe", ".ps1"} and not disabled:
                continue
            name = path.name.removesuffix(".forge-disabled")
            rows.append({"name": name, "file": path.name, "path": str(path), "enabled": not disabled})
            continue
        if not (path.name.endswith(".desktop") or disabled):
            continue
        entry_path = path.with_name(path.name.removesuffix(".forge-disabled")) if disabled else path
        name = entry_path.stem
        try:
            for line in entry_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("Name="):
                    name = line.partition("=")[2].strip() or name
                    break
        except OSError:
            pass
        rows.append({"name": name, "file": path.name, "path": str(path), "enabled": not disabled})
    return rows


def toggle_startup(path_text: str, enabled: bool) -> str:
    directory = _autostart_directory().resolve()
    path = Path(path_text)
    if path.parent.resolve() != directory:
        raise ValueError("For safety, Forge can only change files directly inside the current user's autostart folder.")
    if not path.name or path.name in {".", ".."} or path.is_symlink():
        raise ValueError("The selected autostart entry is not a supported regular file.")
    if enabled:
        if not path.name.endswith(".forge-disabled"):
            raise ValueError("This entry is already enabled.")
        target = path.with_name(path.name.removesuffix(".forge-disabled"))
    else:
        if path.name.endswith(".forge-disabled"):
            raise ValueError("This entry is already disabled.")
        target = path.with_name(path.name + ".forge-disabled")
    if not path.is_file():
        raise FileNotFoundError("The autostart entry no longer exists.")
    if target.exists():
        raise FileExistsError(f"Cannot change state because {target.name} already exists.")
    path.rename(target)
    return f"{'Enabled' if enabled else 'Disabled'} {target.name if enabled else path.name}."


def get_cache_directory() -> Path:
    return Path.home() / ".cache"


def get_path_size(path: Path) -> int:
    total = 0
    try:
        if path.is_symlink():
            return 0
        if path.is_file():
            return path.stat().st_size
        for root, dirs, files in os.walk(path, followlinks=False, onerror=lambda _error: None):
            dirs[:] = [name for name in dirs if not (Path(root) / name).is_symlink()]
            for name in files:
                file_path = Path(root) / name
                try:
                    if not file_path.is_symlink():
                        total += file_path.stat().st_size
                except OSError:
                    continue
    except OSError:
        pass
    return total


def get_cache_info() -> dict[str, Any]:
    root = get_cache_directory()
    if not root.exists():
        return {"path": str(root), "size": 0, "items": 0}
    items = 0
    total = 0
    try:
        for child in root.iterdir():
            items += 1
            total += get_path_size(child)
    except OSError:
        pass
    return {"path": str(root), "size": total, "items": items}


def clear_user_cache() -> dict[str, Any]:
    home = Path.home().resolve()
    raw_root = home / ".cache"
    # Refuse symlinked cache roots: resolving one could turn a cache cleanup
    # into deletion inside an unrelated directory chosen by the user.
    if raw_root.is_symlink():
        raise RuntimeError("~/.cache is a symbolic link. Forge refuses to clear it automatically.")
    root = raw_root.resolve()
    if root.parent != home or root == home or str(root) in {"/", ""}:
        raise RuntimeError("Cache path safety check failed. Nothing was removed.")
    removed = 0
    errors: list[str] = []
    if not root.exists():
        return {"removed": 0, "errors": []}
    for child in list(root.iterdir()):
        try:
            if child.is_symlink() or child.is_file():
                child.unlink()
            elif child.is_dir():
                if os.path.ismount(child):
                    errors.append(f"{child.name}: skipped mounted directory")
                    continue
                shutil.rmtree(child)
            removed += 1
        except OSError as exc:
            errors.append(f"{child.name}: {exc}")
    return {"removed": removed, "errors": errors}


def scan_directory(path_text: str) -> dict[str, Any]:
    root = Path(path_text).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Choose a directory, not a file.")
    sizes: dict[str, int] = {}
    kinds: dict[str, str] = {}
    count = 0
    for item in root.iterdir():
        key = item.name
        sizes[key] = 0
        kinds[key] = "Folder" if item.is_dir() and not item.is_symlink() else "File"
    for current, dirs, files in os.walk(root, followlinks=False, onerror=lambda _error: None):
        current_path = Path(current)
        dirs[:] = [name for name in dirs if not (current_path / name).is_symlink()]
        for filename in files:
            file_path = current_path / filename
            try:
                if file_path.is_symlink():
                    continue
                parts = file_path.relative_to(root).parts
                if not parts:
                    continue
                key = parts[0]
                sizes.setdefault(key, 0)
                kinds.setdefault(key, "Folder" if (root / key).is_dir() else "File")
                sizes[key] += file_path.stat().st_size
                count += 1
            except (OSError, ValueError):
                continue
    entries = [
        {"name": name, "path": str(root / name), "size": size, "kind": kinds.get(name, "File")}
        for name, size in sizes.items()
    ]
    entries.sort(key=lambda entry: entry["size"], reverse=True)
    return {"root": str(root), "total": sum(sizes.values()), "files_counted": count, "entries": entries[:100]}
