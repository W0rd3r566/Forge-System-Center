from __future__ import annotations

import json
import platform
import shutil
import socket
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from . import advanced


PROFILE_PRESETS: dict[str, dict[str, Any]] = {
    "balanced": {
        "refresh_ms": 2500, "history_points": 120, "alerts_enabled": True,
        "alert_cpu_threshold": 90, "alert_memory_threshold": 90,
        "alert_disk_threshold": 95, "alert_temperature_threshold": 90,
        "overlay_refresh_ms": 1500, "overlay_opacity": 94,
    },
    "gaming": {
        "refresh_ms": 1500, "history_points": 180, "alerts_enabled": True,
        "alert_cpu_threshold": 96, "alert_memory_threshold": 94,
        "alert_disk_threshold": 96, "alert_temperature_threshold": 88,
        "overlay_refresh_ms": 1000, "overlay_opacity": 96,
    },
    "work": {
        "refresh_ms": 2500, "history_points": 180, "alerts_enabled": True,
        "alert_cpu_threshold": 92, "alert_memory_threshold": 88,
        "alert_disk_threshold": 92, "alert_temperature_threshold": 90,
        "overlay_refresh_ms": 2000, "overlay_opacity": 94,
    },
    "quiet": {
        "refresh_ms": 6000, "history_points": 90, "alerts_enabled": True,
        "alert_cpu_threshold": 95, "alert_memory_threshold": 94,
        "alert_disk_threshold": 97, "alert_temperature_threshold": 92,
        "overlay_refresh_ms": 4000, "overlay_opacity": 88,
    },
}

PROFILE_LABELS = {
    "balanced": "Сбалансированный",
    "gaming": "Игры",
    "work": "Работа",
    "quiet": "Тихий режим",
}


def _journal_path() -> Path:
    return advanced.data_directory() / "changes.jsonl"


def record_change(action: str, details: str, undo: dict[str, Any] | None = None) -> dict[str, Any]:
    """Store a local change entry. Undo payloads only contain explicitly supported actions."""
    path = _journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "id": uuid.uuid4().hex,
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "action": str(action)[:100],
        "details": str(details).replace("\\n", " ")[:1000],
        "undo": undo,
        "undone": False,
    }
    existing = read_change_records(limit=500)
    existing.append(record)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        for item in existing[-500:]:
            stream.write(json.dumps(item, ensure_ascii=False) + "\\n")
        stream.write(json.dumps(record, ensure_ascii=False) + "\\n")
    # read_change_records returns an empty list when the file does not exist.
    # Keep one copy of the new entry if the previous file was already available.
    if existing and existing[-1].get("id") == record["id"]:
        # The record above has already been appended to existing; avoid a duplicate
        # by regenerating the tail without the final duplicate line.
        rows = existing[-500:]
        rows = rows[:-1] + [record]
        with temporary.open("w", encoding="utf-8") as stream:
            for item in rows:
                stream.write(json.dumps(item, ensure_ascii=False) + "\\n")
    temporary.replace(path)
    return record


def read_change_records(limit: int = 200) -> list[dict[str, Any]]:
    path = _journal_path()
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-max(1, min(500, limit)):]
    except OSError:
        return []
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            value = json.loads(line)
            if isinstance(value, dict) and value.get("id"):
                records.append(value)
        except ValueError:
            continue
    return list(reversed(records))


def latest_reversible_change() -> dict[str, Any] | None:
    for record in read_change_records(500):
        if not record.get("undone") and isinstance(record.get("undo"), dict):
            return record
    return None


def mark_change_undone(change_id: str, result: str) -> None:
    path = _journal_path()
    records = list(reversed(read_change_records(500)))
    found = False
    for record in records:
        if record.get("id") == change_id:
            record["undone"] = True
            record["undo_time"] = datetime.now().astimezone().isoformat(timespec="seconds")
            record["undo_result"] = str(result)[:500]
            found = True
            break
    if not found:
        raise ValueError("The selected change no longer exists in the journal.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        for record in records[-500:]:
            stream.write(json.dumps(record, ensure_ascii=False) + "\\n")
    temporary.replace(path)


def _dns_servers() -> list[str]:
    system_name = platform.system()
    if system_name == "Windows":
        try:
            result = subprocess.run(
                ["ipconfig", "/all"], capture_output=True, text=True,
                timeout=4, check=False, errors="replace",
            )
            servers: list[str] = []
            collecting = False
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if "DNS Servers" in stripped or "DNS-Server" in stripped:
                    _, _, value = stripped.partition(":")
                    value = value.strip()
                    collecting = True
                    if value:
                        servers.append(value)
                elif collecting and line[:1].isspace() and stripped and ":" not in stripped:
                    if len(stripped) < 80:
                        servers.append(stripped)
                else:
                    collecting = False
            return list(dict.fromkeys(servers))[:8]
        except (OSError, subprocess.TimeoutExpired):
            return []
    path = Path("/etc/resolv.conf")
    try:
        rows = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split("#", 1)[0].split()
            if len(parts) >= 2 and parts[0] == "nameserver":
                rows.append(parts[1])
        return list(dict.fromkeys(rows))[:8]
    except OSError:
        return []


def run_network_diagnostics() -> list[dict[str, str]]:
    """Read-only network checks. Does not modify network configuration."""
    checks: list[dict[str, str]] = []
    addresses = []
    try:
        stats = __import__("psutil").net_if_stats()
        addrs = __import__("psutil").net_if_addrs()
        for name, state in sorted(stats.items(), key=lambda item: item[0].lower()):
            if not state.isup:
                continue
            ipv4 = next((item.address for item in addrs.get(name, []) if getattr(item.family, "name", "") == "AF_INET"), "")
            if ipv4 and not ipv4.startswith("127."):
                addresses.append(f"{name}: {ipv4}")
    except Exception as exc:
        checks.append({"level": "INFO", "title": "Сетевые интерфейсы", "detail": f"Не удалось прочитать интерфейсы: {exc}"})
    checks.append({
        "level": "OK" if addresses else "WARN",
        "title": "Локальное подключение",
        "detail": ", ".join(addresses[:8]) if addresses else "Нет активного интерфейса с IPv4-адресом.",
    })

    dns = _dns_servers()
    checks.append({
        "level": "OK" if dns else "INFO",
        "title": "DNS-серверы",
        "detail": ", ".join(dns) if dns else "Не удалось определить DNS-серверы стандартным способом.",
    })

    started = time.monotonic()
    try:
        results = socket.getaddrinfo("github.com", 443, type=socket.SOCK_STREAM)
        elapsed_ms = (time.monotonic() - started) * 1000
        resolved = sorted({item[4][0] for item in results if item and item[4]})[:4]
        checks.append({
            "level": "OK" if resolved else "WARN",
            "title": "DNS-запрос github.com",
            "detail": f"Ответ за {elapsed_ms:.0f} мс · {', '.join(resolved) if resolved else 'адрес не получен'}",
        })
    except (OSError, socket.gaierror) as exc:
        checks.append({"level": "WARN", "title": "DNS-запрос github.com", "detail": f"Не удалось разрешить имя: {exc}"})

    ping = shutil.which("ping") or shutil.which("ping.exe")
    if not ping:
        checks.append({"level": "INFO", "title": "Проверка внешней сети", "detail": "Утилита ping недоступна, этот шаг пропущен."})
    else:
        if platform.system() == "Windows":
            command = [ping, "-n", "2", "-w", "1800", "1.1.1.1"]
        else:
            command = [ping, "-c", "2", "-W", "2", "1.1.1.1"]
        try:
            started = time.monotonic()
            result = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False, errors="replace")
            elapsed_ms = (time.monotonic() - started) * 1000
            output = (result.stdout + "\\n" + result.stderr).strip()
            latency = ""
            for line in output.splitlines():
                if "min/avg/max" in line or "Average =" in line:
                    latency = line.strip()[:220]
                    break
            checks.append({
                "level": "OK" if result.returncode == 0 else "WARN",
                "title": "Доступ к 1.1.1.1",
                "detail": (latency or ("Ответ получен." if result.returncode == 0 else "Ответы не получены; сеть может блокировать ICMP.")) + f" · {elapsed_ms:.0f} мс общего времени",
            })
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"level": "WARN", "title": "Доступ к 1.1.1.1", "detail": f"Проверка не завершилась: {exc}"})

    if platform.system() == "Linux" and shutil.which("ip"):
        try:
            result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True, timeout=2, check=False, errors="replace")
            route = result.stdout.strip().splitlines()
            checks.append({
                "level": "OK" if route else "WARN",
                "title": "Маршрут по умолчанию",
                "detail": route[0][:240] if route else "Маршрут по умолчанию не найден.",
            })
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"level": "INFO", "title": "Маршрут по умолчанию", "detail": str(exc)})
    return checks
