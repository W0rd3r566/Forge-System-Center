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


if __name__ == "__main__":
    unittest.main()
