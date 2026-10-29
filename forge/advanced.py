from __future__ import annotations

import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


def data_directory() -> Path:
    if platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "Forge System Center"


def preferences_path() -> Path:
    return data_directory() / "settings.json"


def default_preferences() -> dict[str, Any]:
    return {
        "theme": "graphite",
        "accent": "#a99bff",
        "font_size": 13,
        "sidebar_width": 238,
        "wallpaper": "",
        "wallpaper_strength": 18,
        "custom_qss": "",
        "refresh_ms": 2500,
        "history_points": 120,
        "custom_font": "Inter",
        "corner_radius": 12,
        "density": "comfortable",
        "active_profile": "balanced",
        "alerts_enabled": True,
        "alert_cpu_threshold": 90,
        "alert_memory_threshold": 90,
        "alert_disk_threshold": 95,
        "alert_temperature_threshold": 90,
        "overlay_enabled": False,
        "overlay_opacity": 94,
        "overlay_refresh_ms": 1500,
        "close_to_tray": False,
    }


def load_preferences() -> dict[str, Any]:
    settings = default_preferences()
    try:
        payload = json.loads(preferences_path().read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            settings.update({key: value for key, value in payload.items() if key in settings})
    except (OSError, ValueError, TypeError):
        pass
    if not isinstance(settings["theme"], str) or settings["theme"] not in {"graphite", "midnight", "emerald", "light"}:
        settings["theme"] = "graphite"
    accents = {"#a99bff", "#82b7ff", "#83d6b0", "#f0b7cf", "#f0c674", "#ff879d", "#65d4d0"}
    if not isinstance(settings["accent"], str) or settings["accent"] not in accents:
        settings["accent"] = "#a99bff"
    try:
        settings["font_size"] = max(10, min(17, int(settings["font_size"])))
        settings["sidebar_width"] = max(190, min(310, int(settings["sidebar_width"])))
        settings["wallpaper_strength"] = max(0, min(70, int(settings["wallpaper_strength"])))
        settings["refresh_ms"] = max(1000, min(10000, int(settings["refresh_ms"])))
        settings["history_points"] = max(30, min(360, int(settings["history_points"])))
        settings["corner_radius"] = max(4, min(28, int(settings["corner_radius"])))
        settings["alert_cpu_threshold"] = max(50, min(100, int(settings["alert_cpu_threshold"])))
        settings["alert_memory_threshold"] = max(50, min(100, int(settings["alert_memory_threshold"])))
        settings["alert_disk_threshold"] = max(50, min(100, int(settings["alert_disk_threshold"])))
        settings["alert_temperature_threshold"] = max(60, min(110, int(settings["alert_temperature_threshold"])))
        settings["overlay_opacity"] = max(40, min(100, int(settings["overlay_opacity"])))
        settings["overlay_refresh_ms"] = max(500, min(10000, int(settings["overlay_refresh_ms"])))
    except (ValueError, TypeError):
        defaults = default_preferences()
        for key in ("font_size", "sidebar_width", "wallpaper_strength", "refresh_ms", "history_points", "corner_radius", "alert_cpu_threshold", "alert_memory_threshold", "alert_disk_threshold", "alert_temperature_threshold", "overlay_opacity", "overlay_refresh_ms"):
            settings[key] = defaults[key]
    if not isinstance(settings["custom_font"], str) or not settings["custom_font"].strip():
        settings["custom_font"] = "Inter"
    settings["custom_font"] = settings["custom_font"][:100]
    if settings["density"] not in {"compact", "comfortable", "spacious"}:
        settings["density"] = "comfortable"
    if settings["active_profile"] not in {"balanced", "gaming", "work", "quiet"}:
        settings["active_profile"] = "balanced"
    for key in ("alerts_enabled", "overlay_enabled", "close_to_tray"):
        settings[key] = bool(settings.get(key, defaults[key]))
    if not isinstance(settings["wallpaper"], str):
        settings["wallpaper"] = ""
    if not isinstance(settings["custom_qss"], str):
        settings["custom_qss"] = ""
    settings["custom_qss"] = settings["custom_qss"][:30000]
    settings["wallpaper"] = settings["wallpaper"][:4096]
    return settings


def save_preferences(settings: dict[str, Any]) -> None:
    current = load_preferences()
    current.update({key: value for key, value in settings.items() if key in current})
    path = preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def log_event(message: str, level: str = "INFO") -> None:
    """Append a short local event. No event is sent over the network."""
    path = data_directory() / "events.jsonl"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 512 * 1024:
            backup = path.with_suffix(".old")
            try:
                backup.unlink(missing_ok=True)
                path.replace(backup)
            except OSError:
                pass
        record = {
            "time": datetime.now().astimezone().isoformat(timespec="seconds"),
            "level": str(level)[:12].upper(),
            "message": str(message).replace("\n", " ")[:500],
        }
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def read_events(limit: int = 200) -> list[dict[str, str]]:
    path = data_directory() / "events.jsonl"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max(1, min(1000, limit)):]
    except OSError:
        return []
    events: list[dict[str, str]] = []
    for line in lines:
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                events.append({
                    "time": str(value.get("time", "")),
                    "level": str(value.get("level", "INFO")),
                    "message": str(value.get("message", "")),
                })
        except ValueError:
            continue
    return list(reversed(events))


def get_network_snapshot() -> dict[str, Any]:
    counters = psutil.net_io_counters(pernic=False)
    interfaces: list[dict[str, Any]] = []
    addresses = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for name in sorted(set(addresses) | set(stats), key=str.lower):
        stat = stats.get(name)
        items = addresses.get(name, [])
        ipv4 = next((item.address for item in items if getattr(item.family, "name", "") == "AF_INET"), "")
        ipv6 = next((item.address for item in items if getattr(item.family, "name", "") == "AF_INET6"), "")
        interfaces.append({
            "name": name,
            "is_up": bool(stat.isup) if stat else False,
            "speed_mbps": int(stat.speed or 0) if stat else 0,
            "mtu": int(stat.mtu or 0) if stat else 0,
            "ipv4": ipv4,
            "ipv6": ipv6,
        })
    return {
        "bytes_sent": int(counters.bytes_sent),
        "bytes_recv": int(counters.bytes_recv),
        "packets_sent": int(counters.packets_sent),
        "packets_recv": int(counters.packets_recv),
        "interfaces": interfaces,
        "time": time.monotonic(),
    }


def get_sensor_snapshot() -> dict[str, Any]:
    temperatures: list[dict[str, Any]] = []
    fans: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()

    try:
        sensor_groups = psutil.sensors_temperatures(fahrenheit=False)
    except (AttributeError, OSError, NotImplementedError):
        sensor_groups = {}
    for group, readings in sensor_groups.items():
        for reading in readings:
            current = getattr(reading, "current", None)
            if current is None:
                continue
            label = str(getattr(reading, "label", "") or group)
            key = (label.lower(), round(float(current)))
            if key in seen:
                continue
            seen.add(key)
            temperatures.append({
                "sensor": label,
                "source": str(group),
                "celsius": round(float(current), 1),
                "high": getattr(reading, "high", None),
                "critical": getattr(reading, "critical", None),
            })

    try:
        fan_groups = psutil.sensors_fans()
    except (AttributeError, OSError, NotImplementedError):
        fan_groups = {}
    for group, readings in fan_groups.items():
        for reading in readings:
            current = getattr(reading, "current", None)
            if current is not None:
                fans.append({"sensor": str(getattr(reading, "label", "") or group), "rpm": int(current)})

    # Linux thermal zones provide a fallback on systems without a sensor library.
    if platform.system() == "Linux":
        for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
            try:
                raw = (zone / "temp").read_text(encoding="ascii").strip()
                value = float(raw)
                celsius = value / 1000 if abs(value) >= 1000 else value
                if -20 <= celsius <= 150:
                    label_path = zone / "type"
                    label = label_path.read_text(encoding="utf-8", errors="replace").strip() if label_path.exists() else zone.name
                    key = (label.lower(), round(celsius))
                    if key not in seen:
                        seen.add(key)
                        temperatures.append({"sensor": label or zone.name, "source": "thermal zone", "celsius": round(celsius, 1), "high": None, "critical": None})
            except (OSError, ValueError):
                continue

    gpu: dict[str, Any] | None = None
    smi = None
    for candidate in ("nvidia-smi", "nvidia-smi.exe"):
        try:
            from shutil import which
            smi = which(candidate)
        except OSError:
            smi = None
        if smi:
            break
    if smi:
        try:
            result = subprocess.run(
                [smi, "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=3, check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                values = [part.strip() for part in result.stdout.splitlines()[0].split(",")]
                if len(values) >= 6:
                    def number(value: str) -> float | None:
                        try:
                            return float(value)
                        except ValueError:
                            return None
                    gpu = {
                        "name": values[0],
                        "temperature": number(values[1]),
                        "utilization": number(values[2]),
                        "memory_used_mb": number(values[3]),
                        "memory_total_mb": number(values[4]),
                        "power_w": number(values[5]),
                    }
        except (OSError, subprocess.TimeoutExpired):
            pass

    battery_data: dict[str, Any] | None = None
    try:
        battery = psutil.sensors_battery()
        if battery is not None:
            battery_data = {
                "percent": round(float(battery.percent), 1),
                "plugged": bool(battery.power_plugged),
                "seconds_left": int(battery.secsleft) if battery.secsleft not in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED) else None,
            }
    except (AttributeError, OSError, NotImplementedError):
        pass

    temperatures.sort(key=lambda row: (row["source"], row["sensor"]))
    return {"temperatures": temperatures, "fans": fans, "gpu": gpu, "battery": battery_data}


def history_path() -> Path:
    """Return the private, per-user path used for local performance history."""
    return data_directory() / "performance.jsonl"


def _bounded_percent(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    import math
    if not math.isfinite(number):
        return None
    return round(max(0.0, min(100.0, number)), 1)


def record_performance_sample(snapshot: dict[str, Any], recorded_at: datetime | None = None) -> bool:
    """Append one validated CPU/memory/disk/GPU sample locally; never use the network."""
    cpu = _bounded_percent(snapshot.get("cpu"))
    memory = _bounded_percent(snapshot.get("memory"))
    disk = _bounded_percent(snapshot.get("disk"))
    if cpu is None or memory is None or disk is None:
        return False
    sample = {
        "time": (recorded_at or datetime.now().astimezone()).astimezone().isoformat(timespec="seconds"),
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "gpu": _bounded_percent(snapshot.get("gpu")),
    }
    path = history_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")
        # Keep the log bounded without rewriting it on every sample.
        if path.stat().st_size > 6 * 1024 * 1024:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-40000:]
            temporary = path.with_suffix(".tmp")
            temporary.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            temporary.replace(path)
        return True
    except OSError:
        return False


def read_performance_history(limit: int = 360) -> list[dict[str, Any]]:
    """Read the newest valid history rows in chronological order."""
    path = history_path()
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for line in lines[-max(1, min(50000, int(limit))):]:
        try:
            payload = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get("time"), str):
            continue
        cpu = _bounded_percent(payload.get("cpu"))
        memory = _bounded_percent(payload.get("memory"))
        disk = _bounded_percent(payload.get("disk"))
        if cpu is None or memory is None or disk is None:
            continue
        rows.append({"time": payload["time"], "cpu": cpu, "memory": memory, "disk": disk, "gpu": _bounded_percent(payload.get("gpu"))})
    return rows


def clear_performance_history() -> None:
    """Remove local performance history only after an explicit user action."""
    history_path().unlink(missing_ok=True)


def get_hardware_snapshot() -> dict[str, Any]:
    """Collect hardware facts exposed by the current OS without privileged access."""
    from . import system

    overview = system.get_system_snapshot()
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    try:
        frequency = psutil.cpu_freq()
    except (AttributeError, OSError, NotImplementedError):
        frequency = None

    cpu_name = (platform.processor() or "").strip()
    if not cpu_name and platform.system() == "Linux":
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
                key, separator, value = line.partition(":")
                if separator and key.strip().lower() in {"model name", "hardware", "processor"} and value.strip():
                    cpu_name = value.strip()
                    break
        except OSError:
            pass

    sensors = get_sensor_snapshot()
    gpu = sensors.get("gpu")
    if not gpu and overview.get("gpu") and overview["gpu"] != "Not detected":
        gpu = {"name": overview["gpu"]}
    try:
        disks = system.list_disks()
    except (OSError, RuntimeError):
        disks = []
    try:
        interfaces = get_network_snapshot().get("interfaces", [])
    except (OSError, RuntimeError):
        interfaces = []
    return {
        "cpu_name": cpu_name or "Название процессора не предоставлено ОС",
        "cpu_percent": float(overview.get("cpu", 0.0)),
        "physical_cores": psutil.cpu_count(logical=False) or 0,
        "logical_cores": psutil.cpu_count(logical=True) or 0,
        "frequency_mhz": float(frequency.current) if frequency and frequency.current else None,
        "memory_used": int(memory.used),
        "memory_total": int(memory.total),
        "memory_percent": float(memory.percent),
        "swap_used": int(swap.used),
        "swap_total": int(swap.total),
        "swap_percent": float(swap.percent),
        "gpu": gpu,
        "temperatures": sensors.get("temperatures", []),
        "fans": sensors.get("fans", []),
        "battery": sensors.get("battery"),
        "os": str(overview.get("os", f"{platform.system()} {platform.release()}")),
        "architecture": platform.machine() or "Unknown",
        "uptime": str(overview.get("uptime", "Unknown")),
        "disk_count": len(disks),
        "active_interfaces": [item for item in interfaces if item.get("is_up")],
    }


def create_diagnostic_report() -> dict[str, Any]:
    """Collect a local, user-requested diagnostic snapshot without uploading it."""
    from . import __version__, system

    snapshot = system.get_system_snapshot()
    # Keep usernames, host names, local addresses and command-line arguments out.
    snapshot.pop("hostname", None)
    network = get_network_snapshot()
    for interface in network["interfaces"]:
        interface.pop("ipv4", None)
        interface.pop("ipv6", None)
    return {
        "forge_version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "python": platform.python_version(),
        },
        "snapshot": snapshot,
        "sensors": get_sensor_snapshot(),
        "network": {
            "bytes_sent": network["bytes_sent"],
            "bytes_recv": network["bytes_recv"],
            "interfaces": [{k: v for k, v in interface.items() if k != "ipv6" and k != "ipv4"} for interface in network["interfaces"]],
        },
        "disks": [
            {key: disk[key] for key in ("fstype", "used", "total", "free", "percent") if key in disk}
            for disk in system.list_disks()
        ],
        "top_processes": [
            {"pid": item["pid"], "name": item["name"], "cpu_percent": item["cpu_percent"], "memory_percent": item["memory_percent"]}
            for item in system.list_processes(limit=15)
        ],
    }
