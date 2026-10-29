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
    except (ValueError, TypeError):
        defaults = default_preferences()
        for key in ("font_size", "sidebar_width", "wallpaper_strength", "refresh_ms", "history_points"):
            settings[key] = defaults[key]
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
