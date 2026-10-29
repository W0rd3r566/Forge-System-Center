import tempfile
import unittest
from pathlib import Path

from forge.system import format_bytes, get_path_size, scan_directory


class FormatBytesTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_bytes(0), "0 B")

    def test_kilobytes_and_megabytes(self):
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1024 * 1024), "1.0 MB")

    def test_negative_is_clamped(self):
        self.assertEqual(format_bytes(-5), "0 B")


class StorageScanTests(unittest.TestCase):
    def test_scan_counts_top_level_files_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "single.txt").write_bytes(b"12345")
            folder = root / "project"
            folder.mkdir()
            (folder / "code.py").write_bytes(b"1234567")
            result = scan_directory(str(root))
            by_name = {item["name"]: item["size"] for item in result["entries"]}
            self.assertEqual(by_name["single.txt"], 5)
            self.assertEqual(by_name["project"], 7)
            self.assertEqual(result["total"], 12)
            self.assertEqual(result["files_counted"], 2)

    def test_scan_does_not_follow_symlink_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inside = root / "inside"
            outside = root / "outside"
            inside.mkdir()
            outside.mkdir()
            (outside / "secret.bin").write_bytes(b"x" * 100)
            (root / "shortcut").symlink_to(outside, target_is_directory=True)
            result = scan_directory(str(root))
            by_name = {item["name"]: item["size"] for item in result["entries"]}
            self.assertEqual(by_name["shortcut"], 0)
            self.assertEqual(result["total"], 100)

    def test_get_path_size_ignores_symlink_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.write_bytes(b"x" * 32)
            link = root / "link"
            link.symlink_to(target)
            self.assertEqual(get_path_size(link), 0)


if __name__ == "__main__":
    unittest.main()
