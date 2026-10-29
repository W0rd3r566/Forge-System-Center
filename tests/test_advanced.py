import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forge import advanced


class PreferencesTests(unittest.TestCase):
    def test_preferences_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            with patch("forge.advanced.preferences_path", return_value=path):
                settings = advanced.default_preferences()
                settings.update({"theme": "midnight", "accent": "#82b7ff", "font_size": 15, "wallpaper_strength": 32})
                advanced.save_preferences(settings)
                loaded = advanced.load_preferences()
            self.assertEqual(loaded["theme"], "midnight")
            self.assertEqual(loaded["accent"], "#82b7ff")
            self.assertEqual(loaded["font_size"], 15)
            self.assertEqual(loaded["wallpaper_strength"], 32)

    def test_invalid_profile_values_fall_back_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps({
                "theme": [],
                "accent": {},
                "font_size": "too-large",
                "wallpaper": ["not", "a", "path"],
                "custom_qss": [],
            }), encoding="utf-8")
            with patch("forge.advanced.preferences_path", return_value=path):
                loaded = advanced.load_preferences()
            self.assertEqual(loaded["theme"], "graphite")
            self.assertEqual(loaded["accent"], "#a99bff")
            self.assertEqual(loaded["wallpaper"], "")
            self.assertEqual(loaded["custom_qss"], "")
            self.assertGreaterEqual(loaded["font_size"], 10)
            self.assertLessEqual(loaded["font_size"], 17)


class TelemetryTests(unittest.TestCase):
    def test_network_snapshot_has_counter_and_interface_fields(self):
        snapshot = advanced.get_network_snapshot()
        self.assertGreaterEqual(snapshot["bytes_sent"], 0)
        self.assertGreaterEqual(snapshot["bytes_recv"], 0)
        self.assertIn("time", snapshot)
        self.assertIsInstance(snapshot["interfaces"], list)
        if snapshot["interfaces"]:
            self.assertIn("is_up", snapshot["interfaces"][0])
            self.assertIn("name", snapshot["interfaces"][0])

    def test_sensor_snapshot_has_stable_shape_without_assuming_sensors_exist(self):
        snapshot = advanced.get_sensor_snapshot()
        self.assertIn("temperatures", snapshot)
        self.assertIn("fans", snapshot)
        self.assertIn("gpu", snapshot)
        self.assertIn("battery", snapshot)
        self.assertIsInstance(snapshot["temperatures"], list)
        self.assertIsInstance(snapshot["fans"], list)


class PerformanceHistoryTests(unittest.TestCase):
    def test_record_and_read_history_are_local_and_bounded(self):
        from datetime import datetime, timezone

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "performance.jsonl"
            timestamp = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)
            with patch("forge.advanced.history_path", return_value=path):
                saved = advanced.record_performance_sample({"cpu": 120, "memory": 54.5, "disk": 33, "gpu": None}, recorded_at=timestamp)
                rows = advanced.read_performance_history()
            self.assertTrue(saved)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["cpu"], 100.0)
            self.assertEqual(rows[0]["memory"], 54.5)
            self.assertEqual(rows[0]["disk"], 33.0)
            self.assertIsNone(rows[0]["gpu"])
            self.assertTrue(rows[0]["time"].startswith("2026-10-29T12:00:00"))

    def test_invalid_required_metric_is_not_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "performance.jsonl"
            with patch("forge.advanced.history_path", return_value=path):
                saved = advanced.record_performance_sample({"cpu": 22, "memory": None, "disk": 31})
                rows = advanced.read_performance_history()
            self.assertFalse(saved)
            self.assertEqual(rows, [])
            self.assertFalse(path.exists())

    def test_clear_history_removes_only_history_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "performance.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            with patch("forge.advanced.history_path", return_value=path):
                advanced.clear_performance_history()
            self.assertFalse(path.exists())


class HardwareSnapshotTests(unittest.TestCase):
    def test_hardware_snapshot_contains_stable_fields(self):
        snapshot = advanced.get_hardware_snapshot()
        for field in ("cpu_name", "cpu_percent", "physical_cores", "logical_cores", "memory_total", "swap_total", "architecture", "active_interfaces"):
            self.assertIn(field, snapshot)
        self.assertGreaterEqual(snapshot["logical_cores"], 1)
        self.assertIsInstance(snapshot["active_interfaces"], list)


if __name__ == "__main__":
    unittest.main()
