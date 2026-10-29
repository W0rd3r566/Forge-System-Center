import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forge import features


class ChangeJournalTests(unittest.TestCase):
    def test_records_are_newest_first_and_undo_state_is_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("forge.features.advanced.data_directory", return_value=root):
                first = features.record_change("First", "initial")
                second = features.record_change("Second", "reversible", {"kind": "demo"})
                rows = features.read_change_records(20)

                self.assertEqual([row["id"] for row in rows[:2]], [second["id"], first["id"]])
                self.assertEqual(features.latest_reversible_change()["id"], second["id"])

                features.mark_change_undone(second["id"], "test rollback")
                rows = features.read_change_records(20)

            self.assertTrue(rows[0]["undone"])
            self.assertEqual(rows[0]["undo_result"], "test rollback")
            self.assertIsNone(features.latest_reversible_change())

    def test_change_journal_truncates_newlines_in_details(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("forge.features.advanced.data_directory", return_value=Path(directory)):
                features.record_change("Example", "first line\nsecond line", {"kind": "demo"})
                rows = features.read_change_records()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["details"], "first line second line")

    def test_missing_change_cannot_be_marked_undone(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("forge.features.advanced.data_directory", return_value=Path(directory)):
                with self.assertRaises(ValueError):
                    features.mark_change_undone("missing-id", "no-op")

    def test_profiles_define_expected_modes(self):
        self.assertEqual(
            set(features.PROFILE_PRESETS),
            {"balanced", "gaming", "work", "quiet"},
        )
        for key, settings in features.PROFILE_PRESETS.items():
            with self.subTest(profile=key):
                self.assertIn("refresh_ms", settings)
                self.assertIn("history_points", settings)
                self.assertIn("alerts_enabled", settings)
                self.assertIn("overlay_enabled", settings)


class NetworkDiagnosticTests(unittest.TestCase):
    def test_diagnostics_return_stable_structured_results_without_network_io(self):
        fake_addr = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.10", 443))
        with (
            patch("forge.features.platform.system", return_value="Darwin"),
            patch("forge.features._dns_servers", return_value=["192.0.2.53"]),
            patch("forge.features.shutil.which", return_value=None),
            patch("forge.features.socket.getaddrinfo", return_value=[fake_addr]),
        ):
            checks = features.run_network_diagnostics()

        self.assertGreaterEqual(len(checks), 4)
        for check in checks:
            with self.subTest(check=check.get("title")):
                self.assertIn(check["level"], {"OK", "WARN", "INFO"})
                self.assertIsInstance(check["title"], str)
                self.assertIsInstance(check["detail"], str)
        self.assertTrue(any(check["title"] == "DNS-серверы" for check in checks))
        self.assertTrue(any(check["title"] == "DNS-запрос github.com" for check in checks))


if __name__ == "__main__":
    unittest.main()
